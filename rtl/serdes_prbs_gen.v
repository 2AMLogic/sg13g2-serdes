// serdes_prbs_gen -- word-parallel PRBS-7 / PRBS-31 generator (16 bits per clock).
//
// Polynomials (the spec does not name them; these are the usual choices):
//   PRBS-7  : x^7  + x^6  + 1
//   PRBS-31 : x^31 + x^28 + 1
// State `h` holds the last N emitted bits, h[0] newest. One bit step is
//   nb = h[N-1] ^ h[N-1-K];  h = {h[N-2:0], nb};  emit nb
// (K = 1 for PRBS-7, K = 3 for PRBS-31). Word bit i is the i-th bit of the word
// in transmit order (bit 0 goes on the line first, DR-001 decision 4).
// Seed is all-ones (non-zero); the all-zero state is a lock-up and is never
// entered: `restart`, reset and a zero state all reload the seed.
// Changing `sel31` requires a `restart` pulse.
// Pure RTL-level model, bit-exact against rtl/tests/serdes_ref.py.
module serdes_prbs_gen (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        en,
    input  wire        sel31,     // 0 = PRBS-7, 1 = PRBS-31
    input  wire        restart,   // reload the seed
    output wire [15:0] word       // the word that is consumed when en = 1
);
    wire [30:0] mask = sel31 ? 31'h7FFFFFFF : 31'h0000007F;
    reg  [30:0] h;

    // Dependency of word bit i on the state flops h[0..n-1] as a GF(2) mask
    // (T[j] = h[n-1-j] for j < n, T[n+i] = T[i] ^ T[i+k]), so each bit is one
    // balanced XOR of flops instead of a 16-deep serial recurrence.
    function [30:0] bit_mask(input integer n, input integer k, input integer i);
        reg [1456:0] dep;
        integer j;
        begin
            dep = 1457'd0;
            for (j = 0; j < n; j = j + 1) dep[j*31 +: 31] = 31'd1 << (n - 1 - j);
            for (j = 0; j <= i; j = j + 1)
                dep[(n+j)*31 +: 31] = dep[j*31 +: 31] ^ dep[(j+k)*31 +: 31];
            bit_mask = dep[(n+i)*31 +: 31];
        end
    endfunction

    wire [15:0] w7, w31;
    genvar i;
    generate
        for (i = 0; i < 16; i = i + 1) begin : wbit
            localparam [30:0] M7  = bit_mask(7, 1, i);
            localparam [30:0] M31 = bit_mask(31, 3, i);
            assign w7[i]  = ^(h & M7);
            assign w31[i] = ^(h & M31);
        end
    endgenerate
    wire [15:0] w_n = sel31 ? w31 : w7;
    assign word = w_n;

    // state after the word: newest 16 bits are the word (bit 15 oldest of them),
    // the rest is the old state shifted up by 16
    wire [30:0] h_n = sel31 ? {h[14:0], w31[0], w31[1], w31[2], w31[3], w31[4], w31[5], w31[6], w31[7],
                                         w31[8], w31[9], w31[10], w31[11], w31[12], w31[13], w31[14], w31[15]}
                            : {24'd0, w7[9], w7[10], w7[11], w7[12], w7[13], w7[14], w7[15]};

    always @(posedge clk) begin
        if (!rst_n || restart || (h & mask) == 31'd0)
            h <= mask;
        else if (en)
            h <= h_n;
    end
endmodule
