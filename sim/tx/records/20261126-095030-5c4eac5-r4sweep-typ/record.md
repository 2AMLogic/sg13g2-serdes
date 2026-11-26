# TX R4 swing-shortfall sweep record 20261126-095030-5c4eac5-r4sweep-typ

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `5f8a8d4dac695c149590ca210ae8166baefbf2852ad4edf26fb707361089b250`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_typ.sp` sha256 `c5deacf8b9c29eca822018b1b9ce3815eb9852ffe358c9939b75f1b167e80c64`, request sha256 `88ede7207044ba03ae60cee4d3e1cef4c69e2c901d30436c172753485c915e23`
- `r4sweep_c_p80_r300_typ.sp` sha256 `622ee8185e822c31184adcef5c71232b1b1ddbe4f71d1c2596ff92b94df66ac6`, request sha256 `060e87c37f2164fa6844a72c9826df6f70f5aa5c827265bdf3e0e613110e6254`
- `r4sweep_c_p80_r400_typ.sp` sha256 `bf28ab3e27a37c1ac8aed35aafa5802095b401aff7869ed63fc61a45da1b96bd`, request sha256 `f4151703f70570ad17544659f1ed9c42582e7df4bc3302d7a772d47907037945`
- `r4sweep_c_p80_r600_typ.sp` sha256 `ea266a223d73164cd9e3e53f53b995a4b1f81753943ddf356bff1bddcec61f7f`, request sha256 `f4418d8a61837886434a0a0dd6c810dda5e6ccb0bb65374284c24f4f99eace6b`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `0108584d4e4bbe0272aecca85ad475ad71d4db36d445283a6c98549d3efe1f6d`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`

## Swing quantity

`swing = v(padp) - v(padn)` across the fixed external 100 ohm differential load (`Rload`), behind the R18 pad stand-in per leg (4 ohm series + 70.66 fF extracted pad C + PDK ESD clamp diodes; not the pad_esd cell). Stimulus: the issue #21 stream, a static 12-one preamble, a 12-zero run, a 12-one run, then a 48-bit PRBS-7 slice at 100 ps/bit. FFE off (post-cursor slice bias 0 V).

- `static` = `r4_steady_hi - r4_steady_lo`: v(vd) sampled at 1.35 ns (end of the first 12-one run, ~1.13 ns settled) and 2.55 ns (end of the 12-zero run).
- `PRBS run` = `r4_prbs_run_hi - r4_prbs_run_lo`: v(vd) 10 ps before the end of the longest one run (4 bits, 6.59 ns) and longest zero run (6 bits, 4.39 ns) of the PRBS-7 slice.
- `PRBS p-p` = `r4_prbs_max_v - r4_prbs_min_v` over 3.9..8.8 ns (peak excursion incl. overshoot; an upper bound on a settled level).
- With FFE off the static and PRBS-run levels are the VOD-style quantity comparable with R4. The de-emphasised level (all three slices on) is reported separately in the control table; it is a de-emphasis measurement, not a VOD figure.

## Sweep at the low-supply cold corner `typ/1.080V/-40C` (process typ), FFE off

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | main tail mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | 227.8 | 227.2 | 237.7 | 5.41 | 112.6 | 0.733 | 7/7 | -272.2 | -72.2 |
| c_p80_r300 | +80 | 3.00 | 487.7 | 486.9 | 505.7 | 7.36 | 90.7 | 0.351 | 4/4 | -12.3 | 187.7 |
| c_p80_r400 | +80 | 4.00 | 526.4 | 525.7 | 544.3 | 7.34 | 90.0 | 0.202 | 4/4 | 26.4 | 226.4 |
| c_p80_r600 | +80 | 6.00 | 464.9 | 464.4 | 470.0 | 6.40 | 82.7 | 0.084 | 5/5 | -35.1 | 164.9 |

## R3 stress over the typ corners (3 supplies x 3 temperatures, includes 1.32 V)

| candidate | corners pass/fail/error | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | typ 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 6/3/0 | 0.025 (vc_max_drv_out_n, typ/1.320V/-40C) | -0.008 (vc_max_pre_main_outn, typ/1.320V/27C) | 227.8 (typ/1.080V/-40C) | 419.8 |
| c_p80_r300 | 6/3/0 | 0.351 (vc_max_drv_out_n, typ/1.320V/-40C) | -0.016 (vc_max_pre_post_outn, typ/1.320V/125C) | 486.2 (typ/1.080V/125C) | 661.4 |
| c_p80_r400 | 6/3/0 | 0.494 (vc_max_drv_out_n, typ/1.320V/-40C) | -0.074 (vc_max_pre_post_outn, typ/1.320V/-40C) | 377.3 (typ/1.080V/125C) | 568.4 |
| c_p80_r600 | 6/1/2 | 0.699 (vc_max_drv_out_n, typ/1.320V/-40C) | -0.061 (vc_max_pre_post_outp, typ/1.320V/-40C) | 192.4 (typ/1.080V/125C) | n/a |

## Failing / erroring corners (kept)

- ctl typ/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl typ/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl typ/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 typ/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 typ/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 typ/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 typ/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 typ/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 typ/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r600 typ/1.200V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)
- c_p80_r600 typ/1.320V/-40C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r600 typ/1.320V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)

## Control cross-check against `records/20261123-022802-fedf656-vce` (main `5c4eac5`)

| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |
|---|---|---:|---:|
| tx_sizing_ffe0_wcs | wcs/1.080V/-40C | 207.1 | n/a |
| tx_sizing_ffe1_wcs | wcs/1.080V/-40C | 132.0 | n/a |
| tx_sizing_ffe0_typ | typ/1.200V/27C | 416.9 | 419.8 |
| tx_sizing_ffe1_typ | typ/1.200V/27C | 267.4 | n/a |

## Run
- batch-set exit=4

