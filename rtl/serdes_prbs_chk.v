// serdes_prbs_chk -- word-parallel self-synchronising PRBS-7 / PRBS-31 checker
// with error and bit counters.
//
// Same polynomials and bit order as serdes_prbs_gen (state: last N bits, h[0]
// newest; next bit = h[N-1] ^ h[N-1-K], K = 1 / 3). Per 16-bit word, with
// T = {history (oldest..newest), word} laid out so that the prediction for word
// bit i is T[i] ^ T[i+K]:
//   hunt   : the prediction uses RECEIVED bits only (`rr`, a plain shift
//            register of the last N received bits). A word with no mismatch and
//            a non-zero resulting history counts as clean; LOCK_WORDS
//            consecutive clean words enter `locked`. (The non-zero test rejects
//            a stuck-at-0 line, which a linear predictor would otherwise "lock"
//            to.)
//   locked : the prediction uses a FREE-RUNNING reference `f` (loaded from `rr`
//            on the word that completes the lock run, then advanced one word
//            per checked word), so one line error is counted once, not once per
//            tap. Mismatches add to `err_cnt`; every bit of the word adds to
//            `bit_cnt`.
// Counters saturate at 32'hFFFF_FFFF and are cleared by `clear` (which also
// drops lock). Changing `sel31` needs a `clear`.
//
// Pipelined for the 1.6 ns word clock (DR-005 option 1, issue #36). Stages
// advance every clock; `v*` flags mark real words:
//   A  hunt-side compare: `hc` (clean word) from rr + the word        rx -> +1
//   B  lock state machine (good/locked), free-running reference, and the
//      locked-side mismatch vector                                         +2
//   C  4-bit group popcounts of the mismatch vector                        +3
//   D  `word_err` / `word_valid` / `was_locked` registers (total popcount) +4
//   E  err_cnt / bit_cnt accumulate (one clock behind D, as before)        +5
// The mode used for a word is the state at stage B. Lock gain is applied to the
// very next word (the reference is loaded in the same clock); LOSS of lock is
// decided from the D registers (`word_err >= LOSS_THR` on a word that started
// locked) and so reaches stage B four words late: the lost word and up to four
// following words are still counted as locked (their mismatches are added to
// `err_cnt`), then `locked` drops and hunting restarts. Differences from the
// single-stage checker this replaces (rtl/tests/serdes_ref.py::PrbsChk tracks
// them): +4 clocks of latency on word_err/word_valid, +1 on `locked`; the hunt
// history after a loss is the received bits (the old one kept predicted bits
// for its older half).
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
    output wire [31:0] err_cnt,
    output reg  [31:0] bit_cnt,
    output reg   [4:0] word_err,    // mismatches in the last enabled word (0 unless it started locked)
    output reg         word_valid   // pulses when word_err holds a new word
);
    // Dependency of reference bit i (T[n+i], the free-running prediction of word
    // bit i) on the history flops h[0..n-1], as a GF(2) mask: T[j] (j<n) = h[n-1-j],
    // T[n+i] = T[i] ^ T[i+k].
    function [30:0] ref_mask(input integer n, input integer k, input integer i);
        reg [1456:0] dep;               // 47 T-entries x 31 bits
        integer j;
        begin
            dep = 1457'd0;
            for (j = 0; j < n; j = j + 1) dep[j*31 +: 31] = 31'd1 << (n - 1 - j);
            for (j = 0; j <= i; j = j + 1)
                dep[(n+j)*31 +: 31] = dep[j*31 +: 31] ^ dep[(j+k)*31 +: 31];
            ref_mask = dep[(n+i)*31 +: 31];
        end
    endfunction

    reg  [30:0] rr;                     // last N received bits, [0] newest
    reg  [30:0] f;                      // free-running reference history
    reg   [3:0] good;
    reg         was_locked;             // `locked` as it was when word_err was produced

    // ---- per-order combinational slices (m = 0: PRBS-7, m = 1: PRBS-31) ----
    wire [15:0] m_eh   [0:1];           // hunt mismatch vector
    wire [15:0] m_ref  [0:1];           // free-running prediction of the word
    wire [30:0] m_rrn  [0:1];           // history after the word (received bits)
    wire [30:0] m_fadv [0:1];           // f advanced by one word
    genvar m, i, j;
    generate
        for (m = 0; m < 2; m = m + 1) begin : mode
            localparam integer N = m ? 31 : 7;
            localparam integer K = m ? 3 : 1;
            for (i = 0; i < 16; i = i + 1) begin : bit_
                localparam [30:0] MSK = ref_mask(N, K, i);
                wire ta, tb;
                if (i < N)     assign ta = rr[N-1-i];     else assign ta = rx_word[i-N];
                if (i + K < N) assign tb = rr[N-1-i-K];   else assign tb = rx_word[i+K-N];
                assign m_eh[m][i]  = rx_word[i] ^ ta ^ tb;
                assign m_ref[m][i] = ^(f & MSK);
            end
            for (j = 0; j < 31; j = j + 1) begin : hist
                if (j < N) begin
                    if (j < 16) begin
                        assign m_rrn[m][j]  = rx_word[15-j];
                        assign m_fadv[m][j] = m_ref[m][15-j];
                    end else begin
                        assign m_rrn[m][j]  = rr[j-16];
                        assign m_fadv[m][j] = f[j-16];
                    end
                end else begin
                    assign m_rrn[m][j]  = 1'b0;
                    assign m_fadv[m][j] = 1'b0;
                end
            end
        end
    endgenerate

    wire [15:0] e_h    = sel31 ? m_eh[1]   : m_eh[0];
    wire [30:0] rr_new = sel31 ? m_rrn[1]  : m_rrn[0];
    wire [15:0] ref_w  = sel31 ? m_ref[1]  : m_ref[0];
    wire [30:0] f_adv  = sel31 ? m_fadv[1] : m_fadv[0];

    // ---- stage A -> B registers ----
    reg         vA, hcA;
    reg  [15:0] rxA;
    // ---- stage B -> C ----
    reg         vB, wlB;
    reg  [15:0] eB;
    // ---- stage C -> D ----
    reg         vC, wlC;
    reg  [11:0] gC;

    function [2:0] pop4(input [3:0] x);
        reg [1:0] a, b;
        begin
            a = x[0] + x[1];
            b = x[2] + x[3];
            pop4 = a + b;
        end
    endfunction

    wire        hc_now = (e_h == 16'h0000) && (rr_new != 31'd0);
    wire        lost   = locked && word_valid && was_locked && (word_err >= LOSS_THR);
    wire        gain   = vA && !locked && hcA && (good + 4'd1 >= LOCK_WORDS);

    // ---- counters (DR-005 option 1, issue #36) ----
    // A 32-bit saturating add is too deep for 1.6 ns, so the carries are kept
    // in flops. err_cnt = {eh, el}: `el` (5 b) takes the word's mismatches, its
    // carry-out is held in `pend` and added to `eh` (27 b, 7 groups) one clock
    // later; `pe[g]` is the registered "group g is all ones" flag, so the carry
    // into group g is an AND of flops. The err_cnt port is the RESOLVED value
    // (pending carry included), identical clock by clock to a one-stage adder.
    // bit_cnt[31:4] counts words the same way (bit_cnt[3:0] never changes).
    // A deposit into these registers must also set pend/pe/pb consistently.
    reg   [4:0] el;
    reg  [26:0] eh;
    reg         pend;
    reg   [2:0] pe;
    reg   [2:0] pb;
    wire  [5:0] el_sum = {1'b0, el} + {1'b0, word_err};
    wire  [2:0] ce, cb;
    wire [26:0] eh_nxt;
    wire [27:0] bh_nxt;
    wire  [2:0] pe_nxt;
    wire  [2:0] pb_nxt;
    reg         inc_b;                  // word_valid & was_locked, as its own flop
    assign ce[0] = pend;
    assign cb[0] = inc_b;
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
            if (j < 3) begin
                assign bh_nxt[OB-4 +: WB] = bit_cnt[OB +: WB] + {{(WB-1){1'b0}}, cb[j]};
                assign pb_nxt[j] = cb[j] ? (bit_cnt[OB +: WB] == {{(WB-1){1'b1}}, 1'b0}) : pb[j];
            end
        end
    endgenerate
    wire        sat_e = pend & (&pe);
    wire        sat_b = inc_b & (&pb);
    assign err_cnt = sat_e ? 32'hFFFFFFFF : {eh_nxt, el};

    wire  [4:0] pc_c   = ({2'b00, gC[11:9]} + {2'b00, gC[8:6]}) + ({2'b00, gC[5:3]} + {2'b00, gC[2:0]});

    always @(posedge clk) begin
        if (!rst_n || clear) begin
            rr <= 31'd0; f <= 31'd0; good <= 4'd0; locked <= 1'b0; was_locked <= 1'b0;
            vA <= 1'b0; hcA <= 1'b0; rxA <= 16'd0;
            vB <= 1'b0; wlB <= 1'b0; eB <= 16'd0;
            vC <= 1'b0; wlC <= 1'b0; gC <= 12'd0;
            word_valid <= 1'b0; inc_b <= 1'b0; word_err <= 5'd0;
            el <= 5'd0; eh <= 27'd0; pend <= 1'b0; pe <= 3'd0; pb <= 3'd0; bit_cnt <= 32'd0;
        end else begin
            // A
            vA <= en;
            if (en) begin
                hcA <= hc_now; rxA <= rx_word; rr <= rr_new;
            end
            // B: lock state machine, reference, locked-side mismatch vector
            if (lost) begin
                locked <= 1'b0; good <= 4'd0;
            end else if (vA && !locked) begin
                if (hcA) begin
                    if (gain) locked <= 1'b1;
                    good <= (good == 4'hF) ? good : good + 4'd1;
                end else begin
                    good <= 4'd0;
                end
            end
            if (vA) f <= gain ? rr : f_adv;
            vB <= vA;
            if (vA) begin
                eB <= rxA ^ ref_w; wlB <= locked;
            end
            // C
            vC <= vB;
            if (vB) begin
                gC <= {pop4(eB[15:12]), pop4(eB[11:8]), pop4(eB[7:4]), pop4(eB[3:0])};
                wlC <= wlB;
            end
            // D
            word_valid <= vC;
            inc_b <= vC & wlC;
            if (vC) begin
                word_err <= wlC ? pc_c : 5'd0; was_locked <= wlC;
            end
            // E: consumes the previous word's D result
            if (sat_e) begin
                el <= 5'h1F; eh <= {27{1'b1}}; pend <= 1'b0; pe <= 3'h7;
            end else begin
                eh <= eh_nxt; pe <= pe_nxt;
                pend <= word_valid & el_sum[5];
                if (word_valid) el <= el_sum[4:0];
            end
            if (sat_b) begin
                bit_cnt <= 32'hFFFFFFFF; pb <= 3'h7;
            end else if (inc_b) begin
                bit_cnt <= {bh_nxt, bit_cnt[3:0]}; pb <= pb_nxt;
            end
        end
    end
endmodule
