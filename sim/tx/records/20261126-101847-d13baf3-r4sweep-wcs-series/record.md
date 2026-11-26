# TX R4 swing-shortfall sweep record 20261126-101847-d13baf3-r4sweep-wcs-series

**Sizing evidence, not a spec result and not a measurement.** Issue #286. Nothing here is measured, no `spec/` row is graded and R3/R4 are not edited. The tested range bounds the tested designs only.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- Repository klt pin: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`. Executed versions are in report provenance.
- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` (main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load return of PR #270 is NOT in this record; see the scope note below.
- generator `sim/tx/make_sweep_r4.py` sha256 `b458ed4e83c55d7f24459feb37a847030535d77efa1413fa9d7f1dec837bd0a2`, candidates `sim/tx/r4sweep_candidates.json` sha256 `7ef527d2b5f99a85d49733e6d79aa613ac6e786278564b5bb7f0c38879e2fa4a`
- `r4sweep_ctl_wcs.sp` sha256 `7e65e1e048952ef995a0507ab348dfb4d4e62721a99427ef7209527472b87adb`, request sha256 `fffc79df603c81fa9bd2ddafa89333df3d428cb40824d9fba0cc1bc43f032fe8`
- `r4sweep_dvb_m40_wcs.sp` sha256 `e1fa9f9c12e670cce3eca7748d92fe28aab6df2fa6e2c3dcb291c8b9a5ae2843`, request sha256 `916bb54825f4eff1ac41a2152847d589f8e40dc7f1fe5341092293b1bfaa50c9`
- `r4sweep_dvb_p40_wcs.sp` sha256 `73384627b09afb532a20892bd7e00f9db174ba5156ae38d50899671c245d04b8`, request sha256 `82a6fb99733dbae8ed2bfb855a0782a008ad0dd1fe925e2beed5a660c29779a8`
- `r4sweep_dvb_p80_wcs.sp` sha256 `6801e11c90f9b63d5a7b50f2cfd1d6734d5efaefd103e00a6ed93db5707a5b24`, request sha256 `0d8d8ad9d829a2a9129ac7d12fe8872b4f430a1a1e1126d550bbd50e33ea7903`
- `r4sweep_dvb_p120_wcs.sp` sha256 `ede6a0ae7fb58a8fab57eb100056f0029e7daaa7376729d7409b303c1bb2f411`, request sha256 `7bde3fbe78d19ad85eb18c1154ef0097d6efa6fe2c3e0fc8d61692a710440a85`
- `r4sweep_rtk_125_wcs.sp` sha256 `72e512a0fcee34b5cf6012f70166bc07019d35fe811a7e374f18aa2e1dd99ac5`, request sha256 `26b92b3dd5b4e9c51fd63b574ff3d0758538695c5c2dd0671e05cba4cbe3d37a`
- `r4sweep_rtk_150_wcs.sp` sha256 `467c57753fc18d7e79f96cc75da7dc4eda985d81bc5742ff4be565ecc44ffcfb`, request sha256 `8ab10a1670e6d6cb62e868daa7c330081917c83cdf7b9b841af7e90429826e3e`
- `r4sweep_rtk_200_wcs.sp` sha256 `a8e8f19af365c00ed05211d9172137d728eff5048ed749ac8cacba4357d5048e`, request sha256 `75028d66800be0c066ee61ea9dd682821748d86f1aac1c5a526682f6c965fea3`
- `r4sweep_c_p80_r200_wcs.sp` sha256 `474a2183650415c596416e50be38616c210939f5eff20a08e53522f93b445e75`, request sha256 `6d0f45821ac6d02c62e91e15ac065fa188a38cc5e3e10ffba45e1e7fc4fad153`
- `r4sweep_c_p80_r300_wcs.sp` sha256 `dcd18214496f44b94039516d5a2d30dda68b055ee207e823c5e77302388ceac2`, request sha256 `65793551df68be2255ffc8381c82940830252be6d0a8e2dc5892eb7ebcdb2b3e`
- `r4sweep_c_p120_r300_wcs.sp` sha256 `5656b4ba5b7821dbcde685901076a0cbf4b8cc561df8be7ff1fed1dbc6372e01`, request sha256 `cfc2912f4c5a754b5ada547552cb87d611d8b2bf9f732b8fa8bf49ed5f705644`
- `r4sweep_c_p80_r400_wcs.sp` sha256 `ac4b544c597837e28962a67e41658c74aaee4fd0ecb88ee8cbfa6c23cbb64ab5`, request sha256 `30c9536f80b2ec7ac6fce814511850efb9d1e72498ec49ac75f878fba13d272c`
- `r4sweep_c_p80_r600_wcs.sp` sha256 `05ab8aa7cd174728b30e2cde5d69d047c7cbbd40436d06a9fb162176230ee94a`, request sha256 `bccb617e7d314061ab2691fad36ef217b9c8e0e534986022d5c847ed9d6c4302`
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

| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | XQTM Ic / Ie mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ctl | +0 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| dvb_m40 | -40 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| dvb_p40 | +40 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| dvb_p80 | +80 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| dvb_p120 | +120 | 1.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| rtk_125 | +0 | 1.25 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| rtk_150 | +0 | 1.50 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| rtk_200 | +0 | 2.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r200 | +80 | 2.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r300 | +80 | 3.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p120_r300 | +120 | 3.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r400 | +80 | 4.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |
| c_p80_r600 | +80 | 6.00 | n/a | n/a | n/a | n/a / n/a | n/a | n/a | n/a/n/a | n/a | n/a |

## R3 stress over the wcs corners (3 supplies x 3 temperatures, includes 1.32 V)

Extrema use available measurements. Gaps are listed below.

| candidate | corners pass/fail/error/missing | smallest driver_ffe R3 margin V (card, corner) | smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | wcs 1.20 V / 27 C static mVppd |
|---|---|---|---|---|---|
| ctl | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| dvb_m40 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| dvb_p40 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| dvb_p80 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| dvb_p120 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| rtk_125 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| rtk_150 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| rtk_200 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r200 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r300 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p120_r300 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r400 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |
| c_p80_r600 | 0/0/0/9 (missing report) | n/a | n/a | n/a | n/a |

## Failing, errored or missing data

- ctl: missing report for all 9 requested corners.
- dvb_m40: missing report for all 9 requested corners.
- dvb_p40: missing report for all 9 requested corners.
- dvb_p80: missing report for all 9 requested corners.
- dvb_p120: missing report for all 9 requested corners.
- rtk_125: missing report for all 9 requested corners.
- rtk_150: missing report for all 9 requested corners.
- rtk_200: missing report for all 9 requested corners.
- c_p80_r200: missing report for all 9 requested corners.
- c_p80_r300: missing report for all 9 requested corners.
- c_p120_r300: missing report for all 9 requested corners.
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
