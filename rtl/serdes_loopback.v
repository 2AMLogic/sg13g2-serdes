// serdes_loopback -- TX source mux and parallel-loopback mux (R22).
//
// TX word: PRBS generator or the external 16-bit word, registered (this register
// is the CMOS side of the CML-to-CMOS boundary, DR-001 decision 3).
// RX word: the deserialised word from the RX path, or, with `par_lb`, the TX word
// looped back at the parallel side (the RX edge word is then forced to zero:
// there is no analog edge sample in a parallel loopback, and the CDR is expected
// to be held). The selected RX words are REGISTERED here (DR-005 option 1,
// issue #36): this is the CMOS side of the RX seam and it cuts the
// configuration fan-out (`par_lb`) and the analog-boundary input off from the
// checker and phase-detector logic. One extra word of latency on the RX path.
// Serial loopback (TX to RX at the pad side) is analog: this block only
// forwards the `ser_lb` control bit to the pin driving that switch.
module serdes_loopback (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        src_ext,       // 1 = external word, 0 = PRBS word
    input  wire        prbs_en,       // PRBS generator running; 0 -> TX word zero if !src_ext
    input  wire [15:0] prbs_word,
    input  wire [15:0] ext_word,
    input  wire        par_lb,
    input  wire        ser_lb_ctl,
    input  wire [15:0] rx_d_in,
    input  wire [15:0] rx_e_in,
    output reg  [15:0] tx_word,
    output reg  [15:0] rx_d,
    output reg  [15:0] rx_e,
    output wire        ser_lb
);
    always @(posedge clk) begin
        if (!rst_n)       tx_word <= 16'h0000;
        else if (src_ext) tx_word <= ext_word;
        else if (prbs_en) tx_word <= prbs_word;
        else              tx_word <= 16'h0000;
    end
    always @(posedge clk) begin
        if (!rst_n) begin
            rx_d <= 16'h0000; rx_e <= 16'h0000;
        end else begin
            rx_d <= par_lb ? tx_word : rx_d_in;
            rx_e <= par_lb ? 16'h0000 : rx_e_in;
        end
    end
    assign ser_lb = ser_lb_ctl;
endmodule
