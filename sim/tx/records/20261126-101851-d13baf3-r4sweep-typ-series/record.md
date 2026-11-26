# TX R4 swing-shortfall sweep record 20261126-101851-d13baf3-r4sweep-typ-series

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- Repository klt pin: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`. Executed versions are in report provenance.
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `b458ed4e83c55d7f24459feb37a847030535d77efa1413fa9d7f1dec837bd0a2`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_typ.sp` sha256 `34f03cb2cc7f115832a1b8c33fa19db99adb5c48c45f6bcd7a3c8234d5eaeb51`, request sha256 `32d576a4562d190e7ec8f4723772a9778035949f9db6881d768010de6a0b6ab6`
- `r4sweep_c_p80_r300_typ.sp` sha256 `dc6db3abc36627d55fc967d24579b2eb72ad10f982a56cc152e181dfbbe181b3`, request sha256 `ddc48594710681b3e30525b442a58c628d31ef880a89cd3a2e2a891ca9097ade`
- `r4sweep_c_p80_r400_typ.sp` sha256 `f08ce927290c8eae692852b0d03d63e6046e25a47a1c49144397bad046a5336b`, request sha256 `9d2ba84cc2d6afe3ac9a108b734abbb078fd23c0295de48f5a92ed87bf69c875`
- `r4sweep_c_p80_r600_typ.sp` sha256 `8652216c57e8cebafd019a057cdf37c401035c77c8ea88a054e4dd1c6e782e11`, request sha256 `309c55f64513d0675580342211ddc4803193f89395324c2d78bd9d291f1e08af`
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

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | XQTM Ic / Ie mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r300 | +80 | 3.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r400 | +80 | 4.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r600 | +80 | 6.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |

## R3 stress over the typ corners (3 supplies x 3 temperatures, includes 1.32 V)

Extrema use available measurements. Gaps are listed below.

| candidate | corners pass/fail/error/missing | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | typ 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r300 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r400 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r600 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |

## Failing, errored or missing data

- ctl: missing report for all 9 requested corners.
- c_p80_r300: missing report for all 9 requested corners.
- c_p80_r400: missing report for all 9 requested corners.
- c_p80_r600: missing report for all 9 requested corners.

## Control cross-check against `records/20261123-022802-fedf656-vce` (main `5c4eac5`)

| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |
|---|---|---:|---:|
| tx_sizing_ffe0_wcs | wcs/1.080V/-40C | 207.1 | n/a |
| tx_sizing_ffe1_wcs | wcs/1.080V/-40C | 132.0 | n/a |
| tx_sizing_ffe0_typ | typ/1.200V/27C | 416.9 | n/a |
| tx_sizing_ffe1_typ | typ/1.200V/27C | 267.4 | n/a |

## Run
- batch-set exit=1
