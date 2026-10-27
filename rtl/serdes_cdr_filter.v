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
    reg [13:0] phase;
    reg signed [10:0] freq;
    reg signed [15:0] f_next;
    reg signed [15:0] p_next;

    assign pi_code = phase[13:7];
    assign freq_o  = freq;

    always @(posedge clk) begin
        if (!rst_n || clear) begin
            phase <= PHASE_INIT; freq <= 11'sd0; freq_sat <= 1'b0;
        end else if (en && !hold && corr_valid) begin
            f_next = $signed({{5{freq[10]}}, freq}) + KI * corr;
            p_next = $signed({2'b00, phase}) + KP * corr + $signed({{5{freq[10]}}, freq});
            if (f_next > FMAX) begin
                freq <= FMAX; freq_sat <= 1'b1;
            end else if (f_next < -FMAX) begin
                freq <= -FMAX; freq_sat <= 1'b1;
            end else begin
                freq <= f_next[10:0]; freq_sat <= 1'b0;
            end
            phase <= p_next[13:0];
        end
    end
endmodule
