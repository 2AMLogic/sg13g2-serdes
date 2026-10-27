// serdes_digital_top -- CMOS digital partition of the 10 Gb/s SerDes canary.
//
// Everything at or below the 625 MHz word clock (DR-001 decision 3). The analog
// partition (HBT CML last two serialiser stages, driver, RX buffer/CTLE, four
// samplers, 5 GHz clock path) sits on the boundary ports below; nothing here
// is a PLL/VCO. `clk` is the divided 625 MHz word clock from the analog side.
// Word bit i is the i-th bit on the line (bit 0 first) in both directions.
//
// Chip pins of this partition (<= 8, R22): clk, rst_n, spi_cs_n, spi_sclk,
// spi_mosi, spi_miso, status_o (spi_miso_oe is the pad output enable).
module serdes_digital_top (
    input  wire        clk,
    input  wire        rst_n,
    // control/readout pins
    input  wire        spi_cs_n,
    input  wire        spi_sclk,
    input  wire        spi_mosi,
    output wire        spi_miso,
    output wire        spi_miso_oe,
    output wire        status_o,
    // boundary to the analog partition
    input  wire [15:0] ext_tx_word,   // external TX word (src_ext = 1)
    output wire [15:0] tx_word,       // to the CML serialiser, 625 MHz
    input  wire [15:0] rx_data_word,  // deserialised data samples
    input  wire [15:0] rx_edge_word,  // deserialised edge samples
    output wire  [6:0] pi_code,       // CDR phase-interpolator code
    output wire  [6:0] eye_ph_off,    // eye-monitor sampling phase offset
    output wire  [5:0] eye_smp_off,   // eye-monitor sampler offset
    output wire        ser_lb         // analog serial-loopback switch
);
    wire ser_lb_ctl;
    wire prbs_en, src_ext, sel31, chk_en, par_lb, cdr_en, cdr_hold;
    wire chk_clear, gen_restart, cdr_clear, eye_start;
    wire [15:0] eye_dwell;
    wire [15:0] prbs_word, rx_d, rx_e;
    wire        chk_locked, word_valid, freq_sat;
    wire [31:0] chk_err, chk_bits, eye_err, eye_bits;
    wire  [4:0] word_err;
    wire        eye_busy, eye_done, eye_invalid;
    wire signed [5:0]  corr;
    wire        corr_valid;
    wire signed [10:0] freq;

    serdes_prbs_gen u_gen (
        .clk(clk), .rst_n(rst_n), .en(prbs_en), .sel31(sel31),
        .restart(gen_restart), .word(prbs_word));

    serdes_loopback u_lb (
        .clk(clk), .rst_n(rst_n), .src_ext(src_ext), .prbs_en(prbs_en),
        .prbs_word(prbs_word), .ext_word(ext_tx_word), .par_lb(par_lb),
        .ser_lb_ctl(ser_lb_ctl), .rx_d_in(rx_data_word), .rx_e_in(rx_edge_word),
        .tx_word(tx_word), .rx_d(rx_d), .rx_e(rx_e), .ser_lb(ser_lb));

    serdes_prbs_chk u_chk (
        .clk(clk), .rst_n(rst_n), .en(chk_en), .sel31(sel31), .clear(chk_clear),
        .rx_word(rx_d), .locked(chk_locked), .err_cnt(chk_err), .bit_cnt(chk_bits),
        .word_err(word_err), .word_valid(word_valid));

    serdes_cdr_pd u_pd (
        .clk(clk), .rst_n(rst_n), .en(cdr_en), .d_word(rx_d), .e_word(rx_e),
        .corr(corr), .corr_valid(corr_valid));

    serdes_cdr_filter u_flt (
        .clk(clk), .rst_n(rst_n), .clear(cdr_clear), .en(cdr_en), .hold(cdr_hold),
        .corr_valid(corr_valid), .corr(corr), .pi_code(pi_code), .freq_o(freq),
        .freq_sat(freq_sat));

    serdes_eye_mon u_eye (
        .clk(clk), .rst_n(rst_n), .start(eye_start), .dwell(eye_dwell),
        .chk_locked(chk_locked), .word_valid(word_valid), .word_err(word_err),
        .busy(eye_busy), .done(eye_done), .invalid(eye_invalid),
        .err_cnt(eye_err), .bit_cnt(eye_bits));

    serdes_ctrl u_ctrl (
        .clk(clk), .rst_n(rst_n), .spi_cs_n(spi_cs_n), .spi_sclk(spi_sclk),
        .spi_mosi(spi_mosi), .spi_miso(spi_miso), .spi_miso_oe(spi_miso_oe),
        .status_o(status_o),
        .prbs_en(prbs_en), .src_ext(src_ext), .sel31(sel31), .chk_en(chk_en),
        .par_lb(par_lb), .ser_lb(ser_lb_ctl), .cdr_en(cdr_en), .cdr_hold(cdr_hold),
        .chk_clear(chk_clear), .gen_restart(gen_restart), .cdr_clear(cdr_clear),
        .eye_ph_off(eye_ph_off), .eye_smp_off(eye_smp_off), .eye_dwell(eye_dwell),
        .eye_start(eye_start),
        .chk_locked(chk_locked), .chk_err(chk_err), .chk_bits(chk_bits),
        .freq_sat(freq_sat), .eye_busy(eye_busy), .eye_done(eye_done),
        .eye_invalid(eye_invalid), .eye_err(eye_err), .eye_bits(eye_bits),
        .pi_code(pi_code), .freq(freq));
endmodule
