// serdes_cdr_pd -- word-level Alexander (bang-bang) phase detector reduction.
//
// Per DR-001 decision 2 the half-rate RX takes data samples on 0/180 deg and
// edge samples on 90/270 deg. After the deserialiser, one 625 MHz word carries
// 16 data samples d[k] and 16 edge samples e[k], where e[k] is the edge sample
// taken BETWEEN d[k-1] and d[k] (d[-1] is the last data bit of the previous
// word, held in `dprev`). Per bit, with A = d[k-1], T = e[k], B = d[k]:
//   A == B          : no transition, no information
//   A != B, T == A  : edge sample before the transition -> clock EARLY  -> +1
//   A != B, T == B  : edge sample after  the transition -> clock LATE   -> -1
// `corr` = (#early - #late), -16..+16: positive asks the loop to DELAY the
// sampling clock (raise the phase-interpolator code). Registered output.
module serdes_cdr_pd (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire [15:0] d_word,
    input  wire [15:0] e_word,
    output reg  signed [5:0] corr,
    output reg         corr_valid
);
    // balanced adder tree: 16 one-bit votes -> 0..16
    function [4:0] pop16(input [15:0] x);
        reg [1:0] a0, a1, a2, a3, a4, a5, a6, a7;
        reg [2:0] b0, b1, b2, b3;
        reg [3:0] c0, c1;
        begin
            a0 = x[0]  + x[1];  a1 = x[2]  + x[3];  a2 = x[4]  + x[5];  a3 = x[6]  + x[7];
            a4 = x[8]  + x[9];  a5 = x[10] + x[11]; a6 = x[12] + x[13]; a7 = x[14] + x[15];
            b0 = a0 + a1; b1 = a2 + a3; b2 = a4 + a5; b3 = a6 + a7;
            c0 = b0 + b1; c1 = b2 + b3;
            pop16 = c0 + c1;
        end
    endfunction

    reg         dprev;
    wire [15:0] d_prev_w = {d_word[14:0], dprev};   // bit k = d[k-1]
    wire [15:0] trans    = d_word ^ d_prev_w;       // A != B
    wire [15:0] early    = trans & ~(e_word ^ d_prev_w);   // T == A
    wire [15:0] late     = trans &  (e_word ^ d_prev_w);   // T == B
    wire  [4:0] n_early  = pop16(early);
    wire  [4:0] n_late   = pop16(late);

    always @(posedge clk) begin
        corr_valid <= 1'b0;
        if (!rst_n) begin
            dprev <= 1'b0; corr <= 6'sd0;
        end else if (en) begin
            corr <= $signed({1'b0, n_early}) - $signed({1'b0, n_late});
            corr_valid <= 1'b1;
            dprev <= d_word[15];
        end
    end
endmodule
