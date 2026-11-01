// serdes_eye_mon -- eye-monitor dwell controller (R22).
//
// The host steps the sampling phase offset and sampler offset through the
// control interface (registers drive `ph_off` / `smp_off` straight to the analog
// side). For each point the host pulses `start`; this block waits SETTLE checked
// words for the analog offsets to take effect, then counts PRBS-checker
// mismatches over `dwell` words and raises `done`. `busy` is high from `start`
// until `done`. A point read as `err_cnt` / `bit_cnt` is the eye-opening sample
// for that (phase, offset); sweeping and plotting are host-side.
// `abort_lost`: if the checker loses lock during the dwell the point is flagged
// invalid rather than reported as a low error count.
module serdes_eye_mon #(
    parameter SETTLE = 16
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,
    input  wire [15:0] dwell,         // words, 0 treated as 1
    input  wire        chk_locked,
    input  wire        word_valid,
    input  wire  [4:0] word_err,
    output reg         busy,
    output reg         done,
    output reg         invalid,
    output wire [31:0] err_cnt,
    output reg  [31:0] bit_cnt
);
    // Down counters with a registered "last" flag, so the end-of-phase tests are
    // a single flop (DR-005 option 1, issue #36: the 16-bit == 1 compare was a
    // 10-deep AND chain). `settle_last` = settle_left <= 1, `dwell_last` =
    // dwell_left == 1, both kept in step with their counter.
    reg [15:0] settle_left;
    reg [15:0] dwell_left;
    reg        settle_last, dwell_last;
    reg        counting;

    wire [15:0] dwell_load = (dwell == 16'd0) ? 16'd1 : dwell;
    wire [15:0] dwell_dec  = dwell_left - 16'd1;
    wire [15:0] settle_dec = settle_left - 16'd1;

    // Counters with registered carries (see serdes_prbs_chk): err_cnt = {eh, el},
    // `el` takes word_err and its carry-out is added to `eh` one clock later
    // (`pend`); `pe`/`pb` are registered "group is all ones" flags. err_cnt is
    // therefore only final one clock after the last counted word, so `done` is
    // raised one clock after the last word (`fin`). bit_cnt wraps at 2^32.
    reg   [4:0] el;
    reg  [26:0] eh;
    reg         pend;
    reg   [2:0] pe, pb;
    reg         fin;
    assign err_cnt = {eh, el};
    wire  [5:0] el_sum = {1'b0, el} + {1'b0, word_err};
    wire  [2:0] ce, cb;
    wire [26:0] eh_nxt;
    wire [27:0] bh_nxt;
    wire  [2:0] pe_nxt, pb_nxt;
    wire        cnt_ev = busy && word_valid && counting;
    assign ce[0] = pend;
    assign cb[0] = cnt_ev;
    genvar j;
    generate
        for (j = 0; j < 3; j = j + 1) begin : grp
            localparam integer W  = 9;                    // err hi: 3 x 9 bits
            localparam integer WB = (j == 0) ? 10 : 9;    // bit_cnt[31:4]: 10 + 9 + 9
            localparam integer OB = (j == 0) ? 4 : 14 + 9 * (j - 1);
            if (j > 0) begin
                assign ce[j] = ce[j-1] & pe[j-1];
                assign cb[j] = cb[j-1] & pb[j-1];
            end
            assign eh_nxt[9*j +: W] = eh[9*j +: W] + {{(W-1){1'b0}}, ce[j]};
            assign pe_nxt[j] = ce[j] ? (eh[9*j +: W] == {{(W-1){1'b1}}, 1'b0}) : pe[j];
            assign bh_nxt[OB-4 +: WB] = bit_cnt[OB +: WB] + {{(WB-1){1'b0}}, cb[j]};
            assign pb_nxt[j] = cb[j] ? (bit_cnt[OB +: WB] == {{(WB-1){1'b1}}, 1'b0}) : pb[j];
        end
    endgenerate
    wire        sat_e = pend & (&pe);

    always @(posedge clk) begin
        if (!rst_n) begin
            busy <= 1'b0; done <= 1'b0; invalid <= 1'b0; fin <= 1'b0;
            el <= 5'd0; eh <= 27'd0; pend <= 1'b0; pe <= 3'd0; pb <= 3'd0; bit_cnt <= 32'd0;
            settle_left <= 16'd0; dwell_left <= 16'd0; counting <= 1'b0;
            settle_last <= 1'b0; dwell_last <= 1'b0;
        end else begin
            // counters: run on every clock (carry flush), restart on `start`
            if (start && !busy) begin
                el <= 5'd0; eh <= 27'd0; pend <= 1'b0; pe <= 3'd0; pb <= 3'd0; bit_cnt <= 32'd0;
            end else begin
                if (sat_e) begin
                    el <= 5'h1F; eh <= {27{1'b1}}; pend <= 1'b0; pe <= 3'h7;
                end else begin
                    eh <= eh_nxt; pe <= pe_nxt;
                    pend <= cnt_ev & el_sum[5];
                    if (cnt_ev) el <= el_sum[4:0];
                end
                if (cnt_ev) begin
                    bit_cnt <= {bh_nxt, bit_cnt[3:0]}; pb <= pb_nxt;
                end
            end
            if (fin) begin
                fin <= 1'b0; busy <= 1'b0; done <= 1'b1; counting <= 1'b0;
            end else if (start && !busy) begin
                busy <= 1'b1; done <= 1'b0; invalid <= 1'b0;
                settle_left <= SETTLE; dwell_left <= dwell_load; counting <= 1'b0;
                settle_last <= (SETTLE <= 1); dwell_last <= (dwell_load == 16'd1);
            end else if (busy && word_valid) begin
                if (!counting) begin
                    if (settle_last) counting <= 1'b1;
                    settle_left <= settle_dec;
                    settle_last <= (settle_left <= 16'd2);
                end else begin
                    if (!chk_locked) invalid <= 1'b1;
                    dwell_left <= dwell_dec;
                    dwell_last <= (dwell_left == 16'd2);
                    if (dwell_last) begin
                        fin <= 1'b1; counting <= 1'b0;
                    end
                end
            end
        end
    end
endmodule
