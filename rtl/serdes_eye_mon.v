// serdes_eye_mon -- eye-monitor dwell controller (R22).
//
// The host steps the sampling phase offset and sampler offset through the
// control interface (registers drive `ph_off` / `smp_off` straight to the analog
// side). For each point the host pulses `start`; this block waits SETTLE checked
// words for the analog offsets to take effect, then counts PRBS-checker
// mismatches over `dwell` words and raises `done`. `busy` is high from `start`
// until `done`. A point read as `err_cnt` / `bit_cnt` is the eye-opening sample
// for that (phase, offset); sweeping and plotting are host-side.
// `abort_lost`: if the checker loses lock during the dwell the point is flagged
// invalid rather than reported as a low error count.
module serdes_eye_mon #(
    parameter SETTLE = 16
) (
    input  wire        clk,
    input  wire        rst_n,
    input  wire        start,
    input  wire [15:0] dwell,         // words, 0 treated as 1
    input  wire        chk_locked,
    input  wire        word_valid,
    input  wire  [4:0] word_err,
    output reg         busy,
    output reg         done,
    output reg         invalid,
    output reg  [31:0] err_cnt,
    output reg  [31:0] bit_cnt
);
    reg [15:0] settle_left;
    reg [15:0] dwell_left;
    reg        counting;
    reg [32:0] sum;

    always @(posedge clk) begin
        if (!rst_n) begin
            busy <= 1'b0; done <= 1'b0; invalid <= 1'b0; err_cnt <= 32'd0; bit_cnt <= 32'd0;
            settle_left <= 16'd0; dwell_left <= 16'd0; counting <= 1'b0;
        end else if (start && !busy) begin
            busy <= 1'b1; done <= 1'b0; invalid <= 1'b0; err_cnt <= 32'd0; bit_cnt <= 32'd0;
            settle_left <= SETTLE; dwell_left <= (dwell == 16'd0) ? 16'd1 : dwell; counting <= 1'b0;
        end else if (busy && word_valid) begin
            if (!counting) begin
                if (settle_left <= 16'd1) counting <= 1'b1;
                settle_left <= settle_left - 16'd1;
            end else begin
                if (!chk_locked) invalid <= 1'b1;
                sum = {1'b0, err_cnt} + {28'd0, word_err};
                err_cnt <= sum[32] ? 32'hFFFFFFFF : sum[31:0];
                bit_cnt <= bit_cnt + 32'd16;
                dwell_left <= dwell_left - 16'd1;
                if (dwell_left == 16'd1) begin
                    busy <= 1'b0; done <= 1'b1; counting <= 1'b0;
                end
            end
        end
    end
endmodule
