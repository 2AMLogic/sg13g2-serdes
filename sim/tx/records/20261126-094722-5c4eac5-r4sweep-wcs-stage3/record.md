# TX R4 swing-shortfall sweep record 20261126-094722-5c4eac5-r4sweep-wcs-stage3

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `5f8a8d4dac695c149590ca210ae8166baefbf2852ad4edf26fb707361089b250`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_wcs.sp` sha256 `b1550ff2dc753bdb8d12c92c9900d7ce661460822845715ab0492e390ad40143`, request sha256 `4a23f5d30b0eb115fe98b3f663bf63aaa43ac66f582319b4a1639f7f1c705b11`
- `r4sweep_c_p80_r300_wcs.sp` sha256 `040d788e82a2d929c61dd0e51af113605bf27b17eff691e5b05f1faf3a48a47d`, request sha256 `cb7b993d794c3384772fbff692b25424aca9d08e74d604c24da69574a5512b04`
- `r4sweep_c_p80_r400_wcs.sp` sha256 `3ab2d365f0eb7b33c4c27e040aff1c9959b161f9110ed58ae0ae88929c5eccc8`, request sha256 `a0698ed41fef6ede9adfac86189b8553c0cd54c6b11e919c49ae0e1ed6e84bfd`
- `r4sweep_c_p80_r600_wcs.sp` sha256 `2ab50513d5e488130bce8406e1aaaaf693e2418922b1cb4d9f0001275239f275`, request sha256 `fc1be9038eb479658d8943ffcc39a3d6c274365e309a1b938e1a72e712fc7b3d`
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
| c_p80_r300 | +80 | 3.00 | 421.7 | 421.2 | 438.9 | 6.24 | 88.9 | 0.395 | 5/5 | -78.3 | 121.7 |
| c_p80_r400 | +80 | 4.00 | 452.8 | 452.3 | 470.9 | 6.23 | 88.5 | 0.253 | 5/5 | -47.2 | 152.8 |
| c_p80_r600 | +80 | 6.00 | 421.2 | 420.9 | 429.4 | 5.67 | 87.4 | 0.100 | 5/5 | -78.8 | 121.2 |

## R3 stress over the wcs corners (3 supplies x 3 temperatures, includes 1.32 V)

| candidate | corners pass/fail/error | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | wcs 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 6/3/0 | 0.025 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.008 (vc_max_pre_post_outn, wcs/1.320V/27C) | 208.3 (wcs/1.080V/-40C) | 384.4 |
| c_p80_r300 | 6/3/0 | 0.345 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.007 (vc_max_pre_post_outn, wcs/1.320V/125C) | 421.7 (wcs/1.080V/-40C) | 601.0 |
| c_p80_r400 | 6/3/0 | 0.480 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.016 (vc_max_pre_post_outp, wcs/1.320V/27C) | 346.0 (wcs/1.080V/125C) | 516.9 |
| c_p80_r600 | 6/1/2 | 0.719 (vc_max_drv_out_n, wcs/1.320V/-40C) | -0.044 (vc_max_pre_post_outp, wcs/1.320V/-40C) | 187.5 (wcs/1.080V/125C) | n/a |

## Failing / erroring corners (kept)

- ctl wcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl wcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl wcs/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 wcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 wcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 wcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 wcs/1.320V/125C: fail vc_max_pre_post_outn
- c_p80_r600 wcs/1.200V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)
- c_p80_r600 wcs/1.320V/-40C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r600 wcs/1.320V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)

## Control cross-check against `records/20261123-022802-fedf656-vce` (main `5c4eac5`)

| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |
|---|---|---:|---:|
| tx_sizing_ffe0_wcs | wcs/1.080V/-40C | 207.1 | 208.3 |
| tx_sizing_ffe1_wcs | wcs/1.080V/-40C | 132.0 | n/a |
| tx_sizing_ffe0_typ | typ/1.200V/27C | 416.9 | n/a |
| tx_sizing_ffe1_typ | typ/1.200V/27C | 267.4 | n/a |

## Run
- batch-set exit=4

