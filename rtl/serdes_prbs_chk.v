// serdes_prbs_chk -- word-parallel self-synchronising PRBS-7 / PRBS-31 checker
// with error and bit counters.
//
// Same polynomials and bit order as serdes_prbs_gen (state: last N bits, h[0]
// newest; next bit = h[N-1] ^ h[N-1-K], K = 1 / 3). Per 16-bit word, with
// T = {received bits (word), oldest..newest history h} laid out so that the
// prediction for word bit i is T[i] ^ T[i+K]:
//   hunt   : T takes the RECEIVED bits, so a prediction needs only past
//            received bits. A word with no mismatch and a non-zero resulting
//            history counts as clean; LOCK_WORDS consecutive clean words enter
//            `locked`. (The non-zero test rejects a stuck-at-0 line, which a
//            linear predictor would otherwise "lock" to.)
//   locked : T takes the PREDICTIONS (free-running reference), so one line
//            error is counted once, not once per tap. Mismatches add to
//            `err_cnt`; every bit of the word adds to `bit_cnt`.
// A locked word with LOSS_THR or more mismatches drops back to hunt at the end
// of that word. Lock is decided at word granularity; the word that completes
// the lock run is not counted. Counters saturate at 32'hFFFF_FFFF and are
// cleared by `clear` (which also drops lock). They run one clock behind
// `word_err` / `word_valid` (a registered accumulate stage). Changing `sel31`
// needs a `clear`.
module serdes_prbs_chk #(
    parameter LOCK_WORDS = 4,
    parameter LOSS_THR   = 8
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
    output reg   [4:0] word_err,    // mismatches in the last enabled word (0 unless it started locked)
    output reg         word_valid   // pulses one clock after a word was checked
);
    wire [30:0] mask = sel31 ? 31'h7FFFFFFF : 31'h0000007F;
    reg  [30:0] h;
    reg   [3:0] good;
    reg         was_locked;         // `locked` as it was when word_err was produced

    // T vectors: indices 0..N-1 history oldest..newest, N.. the word
    reg  [46:0] t_h, t_l;
    reg  [15:0] e_h, e_l, ref_w;
    reg  [30:0] h_hunt, h_lock;
    reg   [4:0] pc;
    reg   [4:0] nerr;
    integer     i, n, k, j;

    always @* begin
        n = sel31 ? 31 : 7;
        k = sel31 ? 3 : 1;
        t_h = 47'd0;
        t_l = 47'd0;
        for (j = 0; j < 31; j = j + 1)
            if (j < n) begin
                t_h[j] = h[n - 1 - j];
                t_l[j] = h[n - 1 - j];
            end
        // hunt: word bits are the received bits
        for (i = 0; i < 16; i = i + 1) begin
            t_h[n + i] = rx_word[i];
            e_h[i]     = rx_word[i] ^ (t_h[i] ^ t_h[i + k]);
        end
        // locked: word bits are the free-running prediction
        for (i = 0; i < 16; i = i + 1) begin
            t_l[n + i] = t_l[i] ^ t_l[i + k];
            ref_w[i]   = t_l[n + i];
            e_l[i]     = rx_word[i] ^ ref_w[i];
        end
        h_hunt = 31'd0;
        h_lock = 31'd0;
        for (j = 0; j < 31; j = j + 1)
            if (j < n) begin
                h_hunt[j] = t_h[n + 15 - j];
                h_lock[j] = t_l[n + 15 - j];
            end
        // popcount of the locked mismatches
        pc = 5'd0;
        for (i = 0; i < 16; i = i + 1) pc = pc + {4'd0, e_l[i]};
        nerr = locked ? pc : 5'd0;
    end

    wire hunt_clean = (e_h == 16'h0000) && (h_hunt != 31'd0);
    wire lost       = locked && (pc >= LOSS_THR);

    reg  [32:0] sum;
    always @(posedge clk) begin
        word_valid <= 1'b0;
        if (!rst_n || clear) begin
            h <= 31'd0; good <= 4'd0; locked <= 1'b0; was_locked <= 1'b0;
            err_cnt <= 32'd0; bit_cnt <= 32'd0; word_err <= 5'd0;
        end else begin
            if (en) begin
                word_err <= nerr; word_valid <= 1'b1; was_locked <= locked;
                if (locked && !lost) begin
                    h <= h_lock;
                end else begin
                    h <= h_hunt;
                    if (lost) begin
                        locked <= 1'b0; good <= 4'd0;
                    end else if (hunt_clean) begin
                        if (good + 4'd1 >= LOCK_WORDS) locked <= 1'b1;
                        good <= (good == 4'hF) ? good : good + 4'd1;
                    end else begin
                        good <= 4'd0;
                    end
                end
            end
            // accumulate stage: consumes the previous word's result
            if (word_valid) begin
                sum = {1'b0, err_cnt} + {28'd0, word_err};
                err_cnt <= sum[32] ? 32'hFFFFFFFF : sum[31:0];
                if (was_locked) begin
                    sum = {1'b0, bit_cnt} + 33'd16;
                    bit_cnt <= sum[32] ? 32'hFFFFFFFF : sum[31:0];
                end
            end
        end
    end
endmodule
