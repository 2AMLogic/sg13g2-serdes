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
    reg         dprev;
    reg  signed [5:0] c;
    reg         a, b, t;
    integer     i;
    always @(posedge clk) begin
        corr_valid <= 1'b0;
        if (!rst_n) begin
            dprev <= 1'b0; corr <= 6'sd0;
        end else if (en) begin
            c = 6'sd0;
            for (i = 0; i < 16; i = i + 1) begin
                a = (i == 0) ? dprev : d_word[i-1];
                b = d_word[i];
                t = e_word[i];
                if (a != b) begin
                    if (t == a) c = c + 6'sd1;
                    else        c = c - 6'sd1;
                end
            end
            corr <= c; corr_valid <= 1'b1; dprev <= d_word[15];
        end
    end
endmodule
