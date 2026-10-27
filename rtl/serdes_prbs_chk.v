// serdes_prbs_chk -- word-parallel self-synchronising PRBS-7 / PRBS-31 checker
// with error and bit counters.
//
// Same polynomials and bit order as serdes_prbs_gen. Two modes, per received bit
// r with prediction p = h[N-1] ^ h[N-1-K] (h = last N bits, h[0] newest):
//   hunt   : h takes the RECEIVED bit. A run of correct predictions counts up;
//            LOCK_RUN consecutive correct predictions with a non-zero history
//            enter `locked`. (The non-zero test rejects a stuck-at-0 line,
//            which a linear predictor would otherwise "lock" to.)
//   locked : h takes the PREDICTION (free-running reference), so one line error
//            is counted once, not once per tap. Mismatches add to `err_cnt`,
//            every bit adds to `bit_cnt`.
// A word with LOSS_THR or more mismatches while locked drops back to hunt at
// the end of that word. Counters saturate at 32'hFFFF_FFFF and are cleared by
// `clear`. `clear` also drops lock. Changing `sel31` needs a `clear`.
// The bit that completes the lock run is not counted (it is the last hunt bit).
module serdes_prbs_chk #(
    parameter LOCK_RUN = 32,
    parameter LOSS_THR = 8
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        sel31,
    input  wire        clear,
    input  wire [15:0] rx_word,
    output reg         locked,
    output reg  [31:0] err_cnt,
    output reg  [31:0] bit_cnt,
    output reg   [4:0] word_err,    // mismatches in the last enabled word (locked bits only)
    output reg         word_valid   // pulses one clock after a word was checked
);
    wire [30:0] mask = sel31 ? 31'h7FFFFFFF : 31'h0000007F;
    reg  [30:0] h;
    reg   [7:0] good;

    reg  [30:0] h_t;
    reg   [7:0] good_t;
    reg         lk_t;
    reg   [4:0] werr_t;
    reg   [4:0] nbits_t;
    reg         p, e;
    reg  [32:0] sum;
    integer     i;

    always @(posedge clk) begin
        word_valid <= 1'b0;
        if (!rst_n || clear) begin
            h <= 31'd0; good <= 8'd0; locked <= 1'b0;
            err_cnt <= 32'd0; bit_cnt <= 32'd0; word_err <= 5'd0;
        end else if (en) begin
            h_t = h; good_t = good; lk_t = locked; werr_t = 5'd0; nbits_t = 5'd0;
            for (i = 0; i < 16; i = i + 1) begin
                p = sel31 ? (h_t[30] ^ h_t[27]) : (h_t[6] ^ h_t[5]);
                e = p ^ rx_word[i];
                if (lk_t) begin
                    nbits_t = nbits_t + 5'd1;
                    if (e) werr_t = werr_t + 5'd1;
                    h_t = ((h_t << 1) | {30'd0, p}) & mask;
                end else begin
                    h_t = ((h_t << 1) | {30'd0, rx_word[i]}) & mask;
                    if (e) good_t = 8'd0;
                    else if (good_t != 8'hFF) good_t = good_t + 8'd1;
                    if (!e && good_t >= LOCK_RUN && h_t != 31'd0) lk_t = 1'b1;
                end
            end
            // loss of lock is judged on the word that started locked
            if (locked && werr_t >= LOSS_THR) begin
                lk_t = 1'b0; good_t = 8'd0;
            end
            h <= h_t; good <= good_t; locked <= lk_t;
            word_err <= werr_t; word_valid <= 1'b1;
            sum = {1'b0, err_cnt} + {28'd0, werr_t};
            err_cnt <= sum[32] ? 32'hFFFFFFFF : sum[31:0];
            sum = {1'b0, bit_cnt} + {28'd0, nbits_t};
            bit_cnt <= sum[32] ? 32'hFFFFFFFF : sum[31:0];
        end
    end
endmodule
