// serdes_ctrl -- SPI-style control/readout interface and register file (R22).
//
// Chip pins used by the digital partition (<= 8): clk, rst_n, spi_cs_n,
// spi_sclk, spi_mosi, spi_miso, status = 7 (spi_miso_oe drives the pad's
// output enable, it is not a pin).
//
// Frame (mode 0, MSB first, 24 SCLK cycles while spi_cs_n is low):
//   bit 23     : 1 = write, 0 = read
//   bits 22:16 : register address
//   bits 15:0  : write data (master drives mosi) / read data (slave drives miso;
//                the slave shifts out the register from the falling edge that
//                follows the 8th rising edge, MSB first)
// SCLK, MOSI and CS are sampled by clk through 2-flop synchronisers: SCLK must
// be at most clk/4. A frame that ends (cs_n high) before 24 rising edges is
// discarded without a write.
//
// Register map (16 bit):
//   00 CTRL     rw  [0] prbs_en [1] src_ext [2] sel31 [3] chk_en [4] par_lb
//                   [5] ser_lb [6] cdr_en [7] cdr_hold; write-1 pulses (read 0):
//                   [8] chk_clear [9] snap [10] gen_restart [11] cdr_clear
//                   reset value 0x0002 (external TX word, everything else off)
//   01 -- reserved, reads 0
//   02 ERR_LO   ro  snapshot of the checker error count [15:0]
//   03 ERR_HI   ro  snapshot [31:16]
//   04 BIT_LO   ro  snapshot of the checked-bit count [15:0]
//   05 BIT_HI   ro  snapshot [31:16]
//   06 STATUS   ro  [0] chk_locked [1] freq_sat [2] eye_busy [3] eye_done [4] eye_invalid
//   07 EYE_PH   rw  [6:0]  sampling phase offset
//   08 EYE_OFS  rw  [5:0]  sampler offset
//   09 EYE_DWELL rw [15:0] dwell words (reset 0x0100)
//   0A EYE_CTRL wo  [0] start (pulse)
//   0B EYE_ERR_LO ro, 0C EYE_ERR_HI ro, 0D EYE_BIT_LO ro, 0E EYE_BIT_HI ro
//   0F PI_CODE  ro  [6:0] CDR phase-interpolator code
//   10 FREQ     ro  [10:0] CDR integrator (two's complement)
//   11 ID       ro  0x5E2D
// Unmapped addresses read 0 and ignore writes.
// `status_o` = chk_locked & chk_en (a single-pin lock indication).
module serdes_ctrl (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        spi_cs_n,
    input  wire        spi_sclk,
    input  wire        spi_mosi,
    output reg         spi_miso,
    output wire        spi_miso_oe,
    output wire        status_o,

    // control outputs
    output wire        prbs_en,
    output wire        src_ext,
    output wire        sel31,
    output wire        chk_en,
    output wire        par_lb,
    output wire        ser_lb,
    output wire        cdr_en,
    output wire        cdr_hold,
    output reg         chk_clear,
    output reg         gen_restart,
    output reg         cdr_clear,
    output wire  [6:0] eye_ph_off,
    output wire  [5:0] eye_smp_off,
    output wire [15:0] eye_dwell,
    output reg         eye_start,

    // status inputs
    input  wire        chk_locked,
    input  wire [31:0] chk_err,
    input  wire [31:0] chk_bits,
    input  wire        freq_sat,
    input  wire        eye_busy,
    input  wire        eye_done,
    input  wire        eye_invalid,
    input  wire [31:0] eye_err,
    input  wire [31:0] eye_bits,
    input  wire  [6:0] pi_code,
    input  wire signed [10:0] freq
);
    localparam [15:0] ID = 16'h5E2D;

    // ---- synchronisers and edge detect ----
    reg [2:0] sclk_s, cs_s, mosi_s;
    always @(posedge clk) begin
        if (!rst_n) begin
            sclk_s <= 3'b000; cs_s <= 3'b111; mosi_s <= 3'b000;
        end else begin
            sclk_s <= {sclk_s[1:0], spi_sclk};
            cs_s   <= {cs_s[1:0],  spi_cs_n};
            mosi_s <= {mosi_s[1:0], spi_mosi};
        end
    end
    wire cs_act  = ~cs_s[1];
    wire rise    = ~sclk_s[2] &  sclk_s[1];
    wire fall    =  sclk_s[2] & ~sclk_s[1];
    wire mosi_v  = mosi_s[1];

    // ---- registers ----
    reg  [7:0]  ctrl;
    reg  [6:0]  eph;
    reg  [5:0]  eofs;
    reg  [15:0] edwell;
    reg  [31:0] snap_err, snap_bits;
    reg         snap_pend;

    assign prbs_en  = ctrl[0];
    assign src_ext  = ctrl[1];
    assign sel31    = ctrl[2];
    assign chk_en   = ctrl[3];
    assign par_lb   = ctrl[4];
    assign ser_lb   = ctrl[5];
    assign cdr_en   = ctrl[6];
    assign cdr_hold = ctrl[7];
    assign eye_ph_off  = eph;
    assign eye_smp_off = eofs;
    assign eye_dwell   = edwell;
    assign status_o    = chk_locked & ctrl[3];

    reg [15:0] rdata;
    reg  [6:0] a;
    always @* begin
        case (a)
            7'h00: rdata = {8'd0, ctrl};
            7'h02: rdata = snap_err[15:0];
            7'h03: rdata = snap_err[31:16];
            7'h04: rdata = snap_bits[15:0];
            7'h05: rdata = snap_bits[31:16];
            7'h06: rdata = {11'd0, eye_invalid, eye_done, eye_busy, freq_sat, chk_locked};
            7'h07: rdata = {9'd0, eph};
            7'h08: rdata = {10'd0, eofs};
            7'h09: rdata = edwell;
            7'h0B: rdata = eye_err[15:0];
            7'h0C: rdata = eye_err[31:16];
            7'h0D: rdata = eye_bits[15:0];
            7'h0E: rdata = eye_bits[31:16];
            7'h0F: rdata = {9'd0, pi_code};
            7'h10: rdata = {{5{freq[10]}}, freq};
            7'h11: rdata = ID;
            default: rdata = 16'h0000;
        endcase
    end

    // ---- frame engine ----
    reg  [4:0]  nrise;           // rising edges seen in this frame
    reg  [22:0] sh;              // bits 23..1 of the frame as they arrive
    reg  [15:0] shifter;
    assign spi_miso_oe = cs_act;

    wire [15:0] wd_full = {sh[14:0], mosi_v};
    wire  [6:0] ad_full = sh[21:15];

    always @(posedge clk) begin
        chk_clear <= 1'b0; gen_restart <= 1'b0; cdr_clear <= 1'b0; eye_start <= 1'b0;
        if (!rst_n) begin
            ctrl <= 8'h02; eph <= 7'd0; eofs <= 6'd0; edwell <= 16'h0100;
            snap_err <= 32'd0; snap_bits <= 32'd0; snap_pend <= 1'b0;
            nrise <= 5'd0; sh <= 23'd0; shifter <= 16'd0; a <= 7'd0;
            spi_miso <= 1'b0;
        end else begin
            if (snap_pend) begin
                // taken one clock after the write so the pulse and counters are stable
                snap_err <= chk_err; snap_bits <= chk_bits; snap_pend <= 1'b0;
            end
            if (!cs_act) begin
                nrise <= 5'd0; spi_miso <= 1'b0;
            end else begin
                if (rise) begin
                    sh    <= {sh[21:0], mosi_v};
                    nrise <= (nrise == 5'd24) ? nrise : nrise + 5'd1;
                    if (nrise == 5'd7) a <= {sh[5:0], mosi_v};
                    if (nrise == 5'd23 && sh[22]) begin
                        case (ad_full)
                            7'h00: begin
                                ctrl        <= wd_full[7:0];
                                chk_clear   <= wd_full[8];
                                snap_pend   <= wd_full[9];
                                gen_restart <= wd_full[10];
                                cdr_clear   <= wd_full[11];
                            end
                            7'h07: eph    <= wd_full[6:0];
                            7'h08: eofs   <= wd_full[5:0];
                            7'h09: edwell <= wd_full;
                            7'h0A: eye_start <= wd_full[0];
                            default: ;
                        endcase
                    end
                end
                if (fall) begin
                    if (nrise == 5'd8) begin
                        spi_miso <= rdata[15]; shifter <= {rdata[14:0], 1'b0};
                    end else if (nrise > 5'd8) begin
                        spi_miso <= shifter[15]; shifter <= {shifter[14:0], 1'b0};
                    end
                end
            end
        end
    end
endmodule
