# TX R4 swing-shortfall sweep record 20261126-095254-5c4eac5-r4sweep-bcs

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `5f8a8d4dac695c149590ca210ae8166baefbf2852ad4edf26fb707361089b250`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_bcs.sp` sha256 `d0335e6b4b09c6ceed88c55058c218d51a5c1e02b4297710b23b77536134b6c1`, request sha256 `c179a9c93b6f97bc1ce664a0b07ff2a64fb7f2ddf951d29b80aa400e1b57d6af`
- `r4sweep_c_p80_r300_bcs.sp` sha256 `6cccb4a160f4ce2fcea7475393248c006595bc3c1a40366fc0eb33d345b27df2`, request sha256 `7fab391e652c1d154b4910ffe0280ce9764db646f76b876f8970094178f6d8ea`
- `r4sweep_c_p80_r400_bcs.sp` sha256 `93d2c020e4898156a7b9e79c8761ab37b200ad0bebe88d0f5b3baa7e64a11f9a`, request sha256 `bd1b56827a31b150bf8d3fe1fa15a193332b3ceb9acfc66b7bec677c53f977ec`
- `r4sweep_c_p80_r600_bcs.sp` sha256 `37ac25e4e31c5af048abcccbaee364125c990c32114f1e8fbfca3a4c7622834e`, request sha256 `dd9675188165b16ac437fe1342ff520ea9d6004634688533e051d5a8573fdf1d`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `0108584d4e4bbe0272aecca85ad475ad71d4db36d445283a6c98549d3efe1f6d`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`

## Swing quantity

`swing = v(padp) - v(padn)` across the fixed external 100 ohm differential load (`Rload`), behind the R18 pad stand-in per leg (4 ohm series + 70.66 fF extracted pad C + PDK ESD clamp diodes; not the pad_esd cell). Stimulus: the issue #21 stream, a static 12-one preamble, a 12-zero run, a 12-one run, then a 48-bit PRBS-7 slice at 100 ps/bit. FFE off (post-cursor slice bias 0 V).

- `static` = `r4_steady_hi - r4_steady_lo`: v(vd) sampled at 1.35 ns (end of the first 12-one run, ~1.13 ns settled) and 2.55 ns (end of the 12-zero run).
- `PRBS run` = `r4_prbs_run_hi - r4_prbs_run_lo`: v(vd) 10 ps before the end of the longest one run (4 bits, 6.59 ns) and longest zero run (6 bits, 4.39 ns) of the PRBS-7 slice.
- `PRBS p-p` = `r4_prbs_max_v - r4_prbs_min_v` over 3.9..8.8 ns (peak excursion incl. overshoot; an upper bound on a settled level).
- With FFE off the static and PRBS-run levels are the VOD-style quantity comparable with R4. The de-emphasised level (all three slices on) is reported separately in the control table; it is a de-emphasis measurement, not a VOD figure.

## Sweep at the low-supply cold corner `bcs/1.080V/-40C` (process bcs), FFE off

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | main tail mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | 247.6 | 246.8 | 260.6 | 6.40 | 117.8 | 0.724 | 6/6 | -252.4 | -52.4 |
| c_p80_r300 | +80 | 3.00 | 567.1 | 566.0 | 586.1 | 8.87 | 91.9 | 0.305 | 3/3 | 67.1 | 267.1 |
| c_p80_r400 | +80 | 4.00 | 608.6 | 607.8 | 621.3 | 8.75 | 90.6 | 0.165 | 3/3 | 108.6 | 308.6 |
| c_p80_r600 | +80 | 6.00 | 517.0 | 516.5 | 519.2 | 7.37 | 75.8 | 0.070 | 8/8 | 17.0 | 217.0 |

## R3 stress over the bcs corners (3 supplies x 3 temperatures, includes 1.32 V)

| candidate | corners pass/fail/error | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | bcs 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 6/3/0 | 0.024 (vc_max_drv_out_n, bcs/1.320V/-40C) | -0.008 (vc_max_pre_main_outn, bcs/1.320V/27C) | 247.6 (bcs/1.080V/-40C) | 456.7 |
| c_p80_r300 | 6/3/0 | 0.352 (vc_max_drv_out_n, bcs/1.320V/-40C) | -0.076 (vc_max_pre_post_outn, bcs/1.320V/-40C) | 539.0 (bcs/1.080V/125C) | 734.4 |
| c_p80_r400 | 6/3/0 | 0.505 (vc_max_drv_out_n, bcs/1.320V/-40C) | -0.106 (vc_max_pre_post_outn, bcs/1.320V/-40C) | 413.2 (bcs/1.080V/125C) | 630.0 |
| c_p80_r600 | 6/1/2 | 0.678 (vc_max_drv_out_n, bcs/1.320V/-40C) | -0.070 (vc_max_pre_post_outn, bcs/1.320V/-40C) | 194.6 (bcs/1.080V/125C) | n/a |

## Failing / erroring corners (kept)

- ctl bcs/1.320V/-40C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl bcs/1.320V/27C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- ctl bcs/1.320V/125C: fail vc_max_pre_main_outp, vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 bcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 bcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r300 bcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 bcs/1.320V/-40C: fail vc_max_pre_main_outn, vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 bcs/1.320V/27C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r400 bcs/1.320V/125C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r600 bcs/1.200V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)
- c_p80_r600 bcs/1.320V/-40C: fail vc_max_pre_post_outp, vc_max_pre_post_outn
- c_p80_r600 bcs/1.320V/27C: error diagnostics analysis_aborted, timestep_too_small (no measurement values)

## Control cross-check against `records/20261123-022802-fedf656-vce` (main `5c4eac5`)

| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |
|---|---|---:|---:|
| tx_sizing_ffe0_wcs | wcs/1.080V/-40C | 207.1 | n/a |
| tx_sizing_ffe1_wcs | wcs/1.080V/-40C | 132.0 | n/a |
| tx_sizing_ffe0_typ | typ/1.200V/27C | 416.9 | n/a |
| tx_sizing_ffe1_typ | typ/1.200V/27C | 267.4 | n/a |

## Run
- batch-set exit=4

