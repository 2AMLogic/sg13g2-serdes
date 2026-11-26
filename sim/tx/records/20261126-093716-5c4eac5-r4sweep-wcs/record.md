# TX R4 swing-shortfall sweep record 20261126-093716-5c4eac5-r4sweep-wcs

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `5f8a8d4dac695c149590ca210ae8166baefbf2852ad4edf26fb707361089b250`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_wcs.sp` sha256 `b1550ff2dc753bdb8d12c92c9900d7ce661460822845715ab0492e390ad40143`, request sha256 `4a23f5d30b0eb115fe98b3f663bf63aaa43ac66f582319b4a1639f7f1c705b11`
- `r4sweep_dvb_m40_wcs.sp` sha256 `7f07ba395fc2ce5aff3b72d2b4ece7476603139b843e0c8fe05fe2c0b04d1e62`, request sha256 `7ade68804ff2223252911cc406f74c8bcf6525a81a81bfa58b8fad8ca4e074ad`
- `r4sweep_dvb_p40_wcs.sp` sha256 `e3d1e62bca78971764256b7b18301deb75a15358c721c691dcf74545c7af8501`, request sha256 `b0889cd75b2c9bfc7f7b343f9c222f6460986cb7643f824c97f2e6b08a474888`
- `r4sweep_dvb_p80_wcs.sp` sha256 `a4b1509ecba273cc2a9b018350861877cce76588286462a2cfdae7b56ed575f5`, request sha256 `18e0110b35f7290cd3091eba10120eba5a4824a7fdc20acbdcefa043a9eeb046`
- `r4sweep_dvb_p120_wcs.sp` sha256 `0208111108b84495dfd2d8a81a6b6ef782e8aa1b6c002dddf3288d9bd8338854`, request sha256 `7028571845cfa504d4a144b6f0463d223483ec94f542d2e91089a4c55845a696`
- `r4sweep_rtk_125_wcs.sp` sha256 `709734870a8f53c9178102260584579078fc425e0cd66a19a213337e832ab090`, request sha256 `52a2e71d1ce3394e1fb7c4567536fa7f2a52b9ff206b7a7301def22340224f53`
- `r4sweep_rtk_150_wcs.sp` sha256 `6c8c4e734f48c08fe761326857796e0e3ef74a80f8ea603991326fbcd89384af`, request sha256 `b4339d4ceb1fecd6a93e2db21f27914ef1b5606f9fa1fc428fa8eb81ef1adccc`
- `r4sweep_rtk_200_wcs.sp` sha256 `1e947b979977fabe6c12d489bf360db365406873e37027742a9d7f50ba10c98a`, request sha256 `6d14aa7a48aa32ce03e5575fa45bff70eddbc2e519085df12c8344ecd0397ea2`
- `r4sweep_c_p80_r200_wcs.sp` sha256 `ccfb8625c0a0c88c9f924f3d0eb4b8c5ce90f084d5346e569b94eee3cf12138d`, request sha256 `0a1e7eeb608662cc8d5f6e2e1434052c196f5e5ec3d18fc5ff24544c5e8f1862`
- `r4sweep_c_p80_r300_wcs.sp` sha256 `040d788e82a2d929c61dd0e51af113605bf27b17eff691e5b05f1faf3a48a47d`, request sha256 `cb7b993d794c3384772fbff692b25424aca9d08e74d604c24da69574a5512b04`
- `r4sweep_c_p120_r300_wcs.sp` sha256 `0302ebae807d6881d71815ba4d4b3b6a7c97474843875e93f2edf338470fa49e`, request sha256 `8a91c6400925b9a095b10a8ea0eb7c5f2dbb8410810ab68e70214a917f7fa91d`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `0108584d4e4bbe0272aecca85ad475ad71d4db36d445283a6c98549d3efe1f6d`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`

## Swing quantity

`swing = v(padp) - v(padn)` across the fixed external 100 ohm differential load (`Rload`), behind the R18 pad stand-in per leg (4 ohm series + 70.66 fF extracted pad C + PDK ESD clamp diodes; not the pad_esd cell). Stimulus: the issue #21 stream, a static 12-one preamble, a 12-zero run, a 12-one run, then a 48-bit PRBS-7 slice at 100 ps/bit. FFE off (post-cursor slice bias 0 V).

- `static` = `r4_steady_hi - r4_steady_lo`: v(vd) sampled at 1.35 ns (end of the first 12-one run, ~1.13 ns settled) and 2.55 ns (end of the 12-zero run).
- `PRBS run` = `r4_prbs_run_hi - r4_prbs_run_lo`: v(vd) 10 ps before the end of the longest one run (4 bits, 6.59 ns) and longest zero run (6 bits, 4.39 ns) of the PRBS-7 slice.
- `PRBS p-p` = `r4_prbs_max_v - r4_prbs_min_v` over 3.9..8.8 ns (peak excursion incl. overshoot; an upper bound on a settled level).
- With FFE off the static and PRBS-run levels are the VOD-style quantity comparable with R4. The de-emphasised level (all three slices on) is reported separately in the control table; it is a de-emphasis measurement, not a VOD figure.

## Sweep at the low-supply cold corner `wcs/1.080V/-40C` (process wcs), FFE off

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | main tail mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | 208.3 | 207.8 | 215.5 | 4.63 | 107.6 | 0.744 | 8/8 | -291.7 | -91.7 |
| dvb_m40 | -40 | 1.00 | 127.7 | 127.1 | 140.0 | 2.82 | 132.8 | 0.785 | 18/18 | -372.3 | -172.3 |
| dvb_p40 | +40 | 1.00 | 249.3 | 248.9 | 255.9 | 5.59 | 97.7 | 0.722 | 7/7 | -250.7 | -50.7 |
| dvb_p80 | +80 | 1.00 | 271.1 | 270.8 | 283.5 | 6.26 | 90.2 | 0.708 | 7/6 | -228.9 | -28.9 |
| dvb_p120 | +120 | 1.00 | 273.8 | 273.5 | 289.5 | 6.88 | 85.8 | 0.705 | 6/6 | -226.2 | -26.2 |
| rtk_125 | +0 | 1.25 | 233.3 | 232.8 | 240.4 | 4.63 | 107.3 | 0.711 | 7/7 | -266.7 | -66.7 |
| rtk_150 | +0 | 1.50 | 253.8 | 253.2 | 260.5 | 4.63 | 107.1 | 0.680 | 7/7 | -246.2 | -46.2 |
| rtk_200 | +0 | 2.00 | 285.0 | 284.4 | 291.1 | 4.63 | 106.8 | 0.620 | 6/6 | -215.0 | -15.0 |
| c_p80_r200 | +80 | 2.00 | 370.3 | 369.9 | 386.0 | 6.25 | 89.4 | 0.545 | 5/5 | -129.7 | 70.3 |
| c_p80_r300 | +80 | 3.00 | 421.7 | 421.2 | 438.9 | 6.24 | 88.9 | 0.395 | 5/5 | -78.3 | 121.7 |
| c_p120_r300 | +120 | 3.00 | 425.1 | 424.7 | 445.9 | 6.86 | 84.5 | 0.388 | 5/5 | -74.9 | 125.1 |

## R3 stress over the wcs corners (3 supplies x 3 temperatures, includes 1.32 V)

| candidate | corners pass/fail/error | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | wcs 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 6/3/0 | 0.025 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_post_outn, wcs/1.320V/27C) | 208.3 (wcs/1.080V/-40C) | 384.4 |
| dvb_m40 | 6/3/0 | 0.008 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.010 (vc_max_pre_main_outn, wcs/1.320V/-40C) | 127.7 (wcs/1.080V/-40C) | 281.2 |
| dvb_p40 | 6/3/0 | 0.053 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_post_outn, wcs/1.320V/27C) | 249.3 (wcs/1.080V/-40C) | 465.5 |
| dvb_p80 | 6/3/0 | 0.091 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_post_outn, wcs/1.320V/27C) | 271.1 (wcs/1.080V/-40C) | 518.3 |
| dvb_p120 | 6/3/0 | 0.122 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_post_outn, wcs/1.320V/27C) | 273.8 (wcs/1.080V/-40C) | 549.7 |
| rtk_125 | 6/3/0 | 0.033 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_main_outn, wcs/1.320V/-40C) | 233.3 (wcs/1.080V/-40C) | 425.2 |
| rtk_150 | 6/3/0 | 0.042 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.009 (vc_max_pre_main_outn, wcs/1.320V/-40C) | 253.8 (wcs/1.080V/-40C) | 457.7 |
| rtk_200 | 6/3/0 | 0.061 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.009 (vc_max_pre_main_outn, wcs/1.320V/-40C) | 285.0 (wcs/1.080V/-40C) | 506.1 |
| c_p80_r200 | 6/3/0 | 0.213 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.007 (vc_max_pre_post_outn, wcs/1.320V/-40C) | 370.3 (wcs/1.080V/-40C) | 653.9 |
| c_p80_r300 | 6/3/0 | 0.345 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.007 (vc_max_pre_post_outn, wcs/1.320V/125C) | 421.7 (wcs/1.080V/-40C) | 601.0 |
| c_p120_r300 | 6/3/0 | 0.472 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.007 (vc_max_pre_post_outn, wcs/1.320V/125C) | 425.1 (wcs/1.080V/-40C) | 601.9 |

## Failing / erroring corners (kept)

- ctl wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl wcs/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_m40 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_m40 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_m40 wcs/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p40 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p40 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p40 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p80 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p80 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p80 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p120 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p120 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- dvb_p120 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_125 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_125 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_125 wcs/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_150 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_150 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_150 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_200 wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_200 wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- rtk_200 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r200 wcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r200 wcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r200 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p120_r300 wcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p120_r300 wcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p120_r300 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn

## Control cross-check against `records/20261123-022802-fedf656-vce` (main `5c4eac5`)

| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |
|---|---|---:|---:|
| tx_sizing_ffe0_wcs | wcs/1.080V/-40C | 207.1 | 208.3 |
| tx_sizing_ffe1_wcs | wcs/1.080V/-40C | 132.0 | n/a |
| tx_sizing_ffe0_typ | typ/1.200V/27C | 416.9 | n/a |
| tx_sizing_ffe1_typ | typ/1.200V/27C | 267.4 | n/a |

## Run
- batch-set exit=3


## Erratum 2026-11-26

This record uses a buffered main-tail bias. Its REM current is XQTM emitter current, and its reverse-Vbe card reads the shared bias node. The operating-point recommendation based on these runs has been withdrawn. [Corrected comparison and probe checks in PR #288](../20261126-r4sweep-verdict/verdict.md#erratum-2026-11-26)
