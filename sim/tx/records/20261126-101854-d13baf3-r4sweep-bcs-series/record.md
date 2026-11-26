# TX R4 swing-shortfall sweep record 20261126-101854-d13baf3-r4sweep-bcs-series

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- Repository klt pin: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`. Executed versions are in report provenance.
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `b458ed4e83c55d7f24459feb37a847030535d77efa1413fa9d7f1dec837bd0a2`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_bcs.sp` sha256 `d289232f829280f830dda94e82646f34845c9ba37dcedc838dbc1bb258fd6f51`, request sha256 `e047be4df90512ac2c1b125dedd78e715834104ea9a65501ab86f0d184df36c1`
- `r4sweep_c_p80_r300_bcs.sp` sha256 `25874e3ca302c4f4aeca46ad3a0f9d44a8d897ed4c560926b09299e44d25f613`, request sha256 `f429209fc8e13449104be5cccab5a5f4ee5bae8022b516c18fc2f0ab58183355`
- `r4sweep_c_p80_r400_bcs.sp` sha256 `04a6bfad855445c83fdbc0c2cc09759ef77af9fb962c4a75edf0ca6a2264199a`, request sha256 `869df025df829f95f49848105a6bd5959d39f50aa58f219b75725b27b6cfcbc2`
- `r4sweep_c_p80_r600_bcs.sp` sha256 `1b1bfd0c3c6cf48ebe6d7ad32142d1968bb97e902902db20154d754cfefff226`, request sha256 `665ebb0b51c0af48cbea90c6d6d4b131c718cc90f21a056b61c1cb2dff4ad2a0`
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

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | XQTM Ic / Ie mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r300 | +80 | 3.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r400 | +80 | 4.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r600 | +80 | 6.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |

## R3 stress over the bcs corners (3 supplies x 3 temperatures, includes 1.32 V)

Extrema use available measurements. Gaps are listed below.

| candidate | corners pass/fail/error/missing | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | bcs 1.20 V / 27 C static mVppd |
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
