// serdes_cdr_filter -- CDR digital loop filter (proportional + integral), fixed point.
//
// Input `corr` (signed 6 b, serdes_cdr_pd) is applied once per 625 MHz word:
//   freq  <= sat_FW( freq + KI * corr )           frequency (integral) path
//   phase <= phase + KP * corr + freq   (mod 2^14) phase accumulator
//   pi_code = phase[13:7]                          7-bit phase-interpolator code
// phase wraps modulo one 5 GHz clock period (half-rate: 2 UI), so the 128 PI
// codes cover 360 deg. One phase LSB = 1/16384 clock period. A frequency offset
// of f ppm moves the data phase by 16 UI * f * 1e-6 per word = 8e-6 * f clock
// periods = 0.131 * f phase LSB per word, so +-300 ppm (R13) needs |freq| ~ 39
// LSB; FMAX = 1023 covers about +-7800 ppm.
// `freq_sat` is high while the integrator is clamped. `hold` freezes both
// accumulators. `clear` resets phase to PHASE_INIT (mid-scale) and freq to 0.
// Reset value is the same. Bit-exact against rtl/tests/serdes_ref.py.
//
// Pipelined for the 1.6 ns word clock (DR-005 option 1, issue #36). The
// arithmetic is unchanged; only WHEN each result appears moves:
//   F1  freq / freq_sat update (as before) and the low half of the phase
//       increment t = KP*corr + freq (the old freq)             -> freq_o at +1
//   F2  low 7 phase bits += t[6:0] (carry registered); t's high half
//   F3  high 7 phase bits (= pi_code) += t[13:7] + carry          -> pi_code at +3
// pi_code is the model's pi_code delayed by 2 clocks relative to freq_o; a
// `hold` / `clear` takes effect on words not yet accepted by F1 (words already
// in F2/F3 still land; `clear` flushes them). KI must be 0 or 1 (the integrator
// adder is split assuming |KI*corr| < 32).
module serdes_cdr_filter #(
    parameter KP = 16,                  // proportional gain, phase LSB per vote
    parameter KI = 1,                   // integral gain, freq LSB per vote
    parameter signed [10:0] FMAX = 11'sd1023,
    parameter [13:0] PHASE_INIT = 14'h2000
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        clear,
    input  wire        en,              // cdr_en
    input  wire        hold,
    input  wire        corr_valid,
    input  wire signed [5:0] corr,
    output wire [6:0]  pi_code,
    output wire signed [10:0] freq_o,
    output reg         freq_sat
);
    reg [6:0] ph_hi, ph_lo;             // phase = {ph_hi, ph_lo}
    // The integrator register `fr` holds the sum before clamping (12 b). The
    // flags `sp` / `sn` (registered with it) say it went past +FMAX / -FMAX; the
    // clamped view `freq` is then +/-FMAX. The next sum is fr + corr when no flag
    // is set, and +/-FMAX + corr (a function of corr alone) when one is, so no
    // saturation compare sits behind the adder.
    reg  signed [11:0] fr;
    reg                sp, sn;
    wire signed [10:0] freq = sp ? FMAX : (sn ? -FMAX : fr[10:0]);
    // phase increment t = KP*corr + freq(old), built in two halves
    reg [6:0]  tl_r;                    // F1 -> F2: t[6:0]
    reg        tc_r;                    // F1 -> F2: carry out of t[6:0]
    reg [10:0] tf_r;                    // F1 -> F2: old freq (for t's high half)
    reg  [5:0] tk_r;                    // F1 -> F2: corr
    reg [6:0]  th_r;                    // F2 -> F3: t[13:7]
    reg        pc_r;                    // F2 -> F3: carry out of ph_lo + t[6:0]
    reg        v1, v2;
    reg  [7:0] lo_sum;
    reg [13:0] kc;                      // KP*corr, truncated
    reg  [7:0] t_lo;

    assign pi_code = ph_hi;
    assign freq_o  = freq;

    wire acc = en && !hold && corr_valid;

    // fr + KI*corr with a carry-select upper part: the low 6 bits add; the upper
    // 6 bits move by (carry - sign of corr) in {-1, 0, +1}.
    wire signed [10:0] kic = KI * corr;
    // {f_neg, f_pos, nh[5:0], sum[5:0]} of (6-bit upper | 6-bit lower) base + kic:
    // carry-select upper part, out-of-range flags from the select signals
    function [13:0] addpath(input [5:0] fh, input [5:0] fa, input [5:0] kb, input ksign);
        reg [6:0] fs;
        reg [5:0] gg, pp, zx, nh, tp, tm;
        integer   i;
        reg       c6, dp, dm, d0, fs_z, q15, qm16, qm15;
        begin
            fs = {1'b0, fa} + {1'b0, kb};
            gg = fa & kb;
            pp = fa | kb;
            c6 = gg[5] | (pp[5] & gg[4]) | (pp[5] & pp[4] & gg[3]) |
                 (pp[5] & pp[4] & pp[3] & gg[2]) | (pp[5] & pp[4] & pp[3] & pp[2] & gg[1]) |
                 (pp[5] & pp[4] & pp[3] & pp[2] & pp[1] & gg[0]);
            zx = (fa ^ kb) ^ {pp[4:0], 1'b0};          // fs[5:0] == 0 without the carry chain
            fs_z = (zx == 6'd0);
            dp = c6 & ~ksign;
            dm = ~c6 & ksign;
            d0 = ~dp & ~dm;
            // fh +1 / -1 as toggle masks from flop-only prefixes (all-ones / all-zeros
            // below bit i), so the late carry-derived dp / dm see two gates
            for (i = 0; i < 6; i = i + 1) begin
                tp[i] = (i == 0) ? 1'b1 : (&(fh | (6'h3F << i)));
                tm[i] = (i == 0) ? 1'b1 : ~(|(fh & ~(6'h3F << i)));
                nh[i] = fh[i] ^ ((dp & tp[i]) | (dm & tm[i]));
            end
            q15  = (fh == 6'd15);
            qm16 = (fh == 6'b110000);
            qm15 = (fh == 6'b110001);
            addpath = {(dm & qm16) | (((d0 & qm16) | (dm & qm15)) & fs_z),   // sum <= -1024
                       dp & q15,                                               // sum >= 1024
                       nh, fs[5:0]};
        end
    endfunction

    wire [13:0] r_n = addpath(fr[11:6], fr[5:0], kic[5:0], kic[5]);
    wire [13:0] r_p = addpath(6'd15, 6'd63, kic[5:0], kic[5]);          // +FMAX + corr
    wire [13:0] r_m = addpath(6'b110000, 6'd1, kic[5:0], kic[5]);       // -FMAX + corr
    wire [13:0] r_s = sp ? r_p : (sn ? r_m : r_n);

    always @(posedge clk) begin
        if (!rst_n || clear) begin
            ph_hi <= PHASE_INIT[13:7]; ph_lo <= PHASE_INIT[6:0];
            fr <= 12'sd0; sp <= 1'b0; sn <= 1'b0; freq_sat <= 1'b0;
            tl_r <= 7'd0; tc_r <= 1'b0; tf_r <= 11'd0; tk_r <= 6'd0;
            th_r <= 7'd0; pc_r <= 1'b0; v1 <= 1'b0; v2 <= 1'b0;
        end else begin
            // F1
            v1 <= acc;
            if (acc) begin
                fr <= r_s[11:0];
                sp <= r_s[12]; sn <= r_s[13];
                freq_sat <= r_s[12] | r_s[13];
                kc = KP * corr;
                t_lo = {1'b0, kc[6:0]} + {1'b0, freq[6:0]};
                tl_r <= t_lo[6:0]; tc_r <= t_lo[7];
                tf_r <= freq; tk_r <= corr;
            end
            // F2
            v2 <= v1;
            if (v1) begin
                lo_sum = {1'b0, ph_lo} + {1'b0, tl_r};
                ph_lo <= lo_sum[6:0];
                pc_r  <= lo_sum[7];
                kc = KP * $signed(tk_r);
                th_r <= kc[13:7] + {{3{tf_r[10]}}, tf_r[10:7]} + {6'd0, tc_r};
            end
            // F3
            if (v2) ph_hi <= ph_hi + th_r + {6'd0, pc_r};
        end
    end
endmodule
