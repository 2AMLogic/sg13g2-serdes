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

    reg  [30:0] h_n;
    reg  [15:0] w_n;
    reg         nb;
    integer     i;
    always @* begin
        h_n = h;
        w_n = 16'h0000;
        for (i = 0; i < 16; i = i + 1) begin
            nb  = sel31 ? (h_n[30] ^ h_n[27]) : (h_n[6] ^ h_n[5]);
            h_n = ((h_n << 1) | {30'd0, nb}) & mask;
            w_n[i] = nb;
        end
    end
    assign word = w_n;

    always @(posedge clk) begin
        if (!rst_n || restart || (h & mask) == 31'd0)
            h <= mask;
        else if (en)
            h <= h_n;
    end
endmodule
