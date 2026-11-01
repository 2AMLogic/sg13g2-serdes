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
//
// Three register stages (DR-005 option 1, issue #36; was one, which could not
// meet the 1.6 ns word clock): word clock N is `en`-sampled, then
//   P1  early/late votes and their 4-bit group popcounts (24 flops)
//   P2  early total and late total (5 b each)
//   P3  corr = early - late                      (registered output)
// so `corr` / `corr_valid` appear 3 clocks after the word (was 1): +2 clocks of
// CDR loop latency. Stages advance every clock; `corr_valid` marks real words.
module serdes_cdr_pd (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire [15:0] d_word,
    input  wire [15:0] e_word,
    output reg  signed [5:0] corr,
    output reg         corr_valid
);
    function [2:0] pop4(input [3:0] x);
        reg [1:0] a, b;
        begin
            a = x[0] + x[1];
            b = x[2] + x[3];
            pop4 = a + b;
        end
    endfunction

    reg         dprev;
    wire [15:0] d_prev_w = {d_word[14:0], dprev};   // bit k = d[k-1]
    wire [15:0] trans    = d_word ^ d_prev_w;       // A != B
    wire [15:0] agree    = ~(e_word ^ d_prev_w);    // T == A
    wire [15:0] early    = trans &  agree;
    wire [15:0] late     = trans & ~agree;

    reg         v1, v2;
    reg  [11:0] ge, gl;         // P1: per 4-bit group early / late counts (3 b each)
    reg   [4:0] n_early, n_late;// P2

    always @(posedge clk) begin
        if (!rst_n) begin
            dprev <= 1'b0; v1 <= 1'b0; v2 <= 1'b0; corr_valid <= 1'b0;
            ge <= 12'd0; gl <= 12'd0; n_early <= 5'd0; n_late <= 5'd0;
            corr <= 6'sd0;
        end else begin
            // P1
            v1 <= en;
            if (en) begin
                ge <= {pop4(early[15:12]), pop4(early[11:8]), pop4(early[7:4]), pop4(early[3:0])};
                gl <= {pop4(late[15:12]),  pop4(late[11:8]),  pop4(late[7:4]),  pop4(late[3:0])};
                dprev <= d_word[15];
            end
            // P2
            v2 <= v1;
            if (v1) begin
                n_early <= ({2'b00, ge[11:9]} + {2'b00, ge[8:6]}) + ({2'b00, ge[5:3]} + {2'b00, ge[2:0]});
                n_late  <= ({2'b00, gl[11:9]} + {2'b00, gl[8:6]}) + ({2'b00, gl[5:3]} + {2'b00, gl[2:0]});
            end
            // P3
            corr_valid <= v2;
            if (v2) corr <= $signed({1'b0, n_early}) - $signed({1'b0, n_late});
        end
    end
endmodule
