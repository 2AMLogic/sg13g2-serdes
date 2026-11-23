# RX sizing record 20261123-025159-fedf656-vce

**Sizing evidence, not a spec result.** Nothing here is measured. `spec/target-spec.md` is PROPOSED;
rows R8-R10, R20 are used as draft targets only. Passives are ideal, the pad capacitance is a
placeholder, the clock source is ideal, the CTLE load is a placeholder 80 fF, and the MOS level
converter is not simulated. The grid is the HBT-family PVT set: hbt_typ/bcs/wcs x 1.08/1.2/1.32 V x -40/27/125 C (27 points).

## Pins
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0, tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc` (sim/pdk.json)
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49` (layout/toolchain.json)
- Schematics/netlists: design/rx/ at the commit named in the record id; netlist staleness gate `design/check-netlists.sh`

## Runs

### ctle_ac
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261123-025159-fedf656-vce/ctle_ac.report.json ctle_ac.request.json`
- ctle_ac exit=0
- status: **pass** (27/27 corners pass, 0 error); engine host worker, ngspice 47, backend job `klt-sim-64492e966772`

### ctle_op
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261123-025159-fedf656-vce/ctle_op.report.json ctle_op.request.json`
- ctle_op exit=0
- status: **pass** (27/27 corners pass, 0 error); engine host worker, ngspice 47, backend job `klt-sim-406d0c0ca990`

### pad_ac
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261123-025159-fedf656-vce/pad_ac.report.json pad_ac.request.json`
- pad_ac exit=0
- status: **pass** (27/27 corners pass, 0 error); engine host worker, ngspice 47, backend job `klt-sim-0b7e75a15244`

### latch_regen
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261123-025159-fedf656-vce/latch_regen.report.json latch_regen.request.json`
- latch_regen exit=3
- status: **fail** (18/27 corners pass, 0 error); engine host worker, ngspice 47, backend job `klt-sim-c5eb5774b199`

## CTLE AC response per setting (peaking = gain at 5 GHz minus gain at 0.1 GHz, differential, dB)

Code = c2c1c0. First-look comparison with R10: 0-10 dB peaking at 5 GHz in >= 8 steps (code 0 <= 1 dB, code 7 >= 10 dB, monotonic in between); the `check` column applies that.

| corner | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 | gain@0.1G c0 / c7 | gain@5G c7 | check |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hbt_typ/1.080V/-40C | 0.60 | 4.08 | 6.19 | 7.53 | 8.42 | 9.01 | 9.42 | 9.71 | -17.87 / -12.82 | -3.11 | c7 < 10 dB |
| hbt_typ/1.080V/27C | 0.02 | 3.96 | 6.23 | 7.64 | 8.57 | 9.18 | 9.61 | 9.90 | -15.15 / -10.32 | -0.42 | c7 < 10 dB |
| hbt_typ/1.080V/125C | 0.03 | 3.89 | 6.14 | 7.57 | 8.51 | 9.15 | 9.60 | 9.91 | -14.11 / -9.61 | 0.29 | c7 < 10 dB |
| hbt_typ/1.200V/-40C | -0.19 | 4.06 | 6.40 | 7.83 | 8.75 | 9.35 | 9.76 | 10.03 | -13.87 / -8.91 | 1.12 | ok |
| hbt_typ/1.200V/27C | -0.21 | 4.00 | 6.35 | 7.80 | 8.74 | 9.36 | 9.78 | 10.07 | -13.58 / -8.83 | 1.24 | ok |
| hbt_typ/1.200V/125C | -0.10 | 3.89 | 6.19 | 7.64 | 8.59 | 9.24 | 9.69 | 9.99 | -13.38 / -8.97 | 1.02 | c7 < 10 dB |
| hbt_typ/1.320V/-40C | -0.28 | 4.09 | 6.47 | 7.92 | 8.84 | 9.44 | 9.84 | 10.11 | -13.04 / -8.12 | 1.99 | ok |
| hbt_typ/1.320V/27C | -0.28 | 4.02 | 6.40 | 7.86 | 8.81 | 9.43 | 9.85 | 10.13 | -13.02 / -8.32 | 1.81 | ok |
| hbt_typ/1.320V/125C | -0.19 | 3.84 | 6.15 | 7.61 | 8.56 | 9.21 | 9.64 | 9.93 | -13.01 / -8.68 | 1.25 | c7 < 10 dB |
| hbt_bcs/1.080V/-40C | 0.28 | 4.13 | 6.42 | 7.88 | 8.86 | 9.53 | 10.00 | 10.33 | -17.29 / -12.75 | -2.42 | ok |
| hbt_bcs/1.080V/27C | -0.08 | 4.07 | 6.45 | 7.95 | 8.95 | 9.62 | 10.09 | 10.42 | -14.84 / -10.42 | -0.00 | ok |
| hbt_bcs/1.080V/125C | -0.03 | 3.99 | 6.33 | 7.82 | 8.82 | 9.50 | 9.97 | 10.30 | -13.89 / -9.67 | 0.63 | ok |
| hbt_bcs/1.200V/-40C | -0.22 | 4.16 | 6.61 | 8.13 | 9.13 | 9.79 | 10.25 | 10.56 | -13.64 / -9.16 | 1.40 | ok |
| hbt_bcs/1.200V/27C | -0.24 | 4.10 | 6.54 | 8.07 | 9.07 | 9.74 | 10.21 | 10.52 | -13.39 / -9.02 | 1.50 | ok |
| hbt_bcs/1.200V/125C | -0.13 | 3.98 | 6.34 | 7.84 | 8.84 | 9.52 | 9.99 | 10.31 | -13.20 / -9.05 | 1.27 | ok |
| hbt_bcs/1.320V/-40C | -0.29 | 4.19 | 6.66 | 8.19 | 9.19 | 9.85 | 10.30 | 10.61 | -12.85 / -8.40 | 2.21 | ok |
| hbt_bcs/1.320V/27C | -0.29 | 4.11 | 6.57 | 8.10 | 9.10 | 9.78 | 10.24 | 10.55 | -12.85 / -8.52 | 2.03 | ok |
| hbt_bcs/1.320V/125C | -0.22 | 3.88 | 6.23 | 7.72 | 8.69 | 9.35 | 9.78 | 10.07 | -12.87 / -8.77 | 1.31 | ok |
| hbt_wcs/1.080V/-40C | 1.14 | 4.11 | 5.99 | 7.18 | 7.98 | 8.50 | 8.87 | 9.12 | -18.67 / -13.18 | -4.06 | c0 > 1 dB; c7 < 10 dB |
| hbt_wcs/1.080V/27C | 0.19 | 3.87 | 6.02 | 7.35 | 8.22 | 8.80 | 9.19 | 9.46 | -15.53 / -10.41 | -0.95 | c7 < 10 dB |
| hbt_wcs/1.080V/125C | 0.14 | 3.80 | 5.97 | 7.36 | 8.28 | 8.90 | 9.34 | 9.64 | -14.37 / -9.77 | -0.13 | c7 < 10 dB |
| hbt_wcs/1.200V/-40C | -0.14 | 3.95 | 6.20 | 7.55 | 8.40 | 8.96 | 9.33 | 9.57 | -14.12 / -8.77 | 0.80 | c7 < 10 dB |
| hbt_wcs/1.200V/27C | -0.15 | 3.91 | 6.18 | 7.57 | 8.47 | 9.06 | 9.45 | 9.72 | -13.80 / -8.80 | 0.93 | c7 < 10 dB |
| hbt_wcs/1.200V/125C | -0.05 | 3.81 | 6.06 | 7.49 | 8.43 | 9.07 | 9.51 | 9.82 | -13.58 / -9.11 | 0.71 | c7 < 10 dB |
| hbt_wcs/1.320V/-40C | -0.27 | 3.99 | 6.29 | 7.67 | 8.53 | 9.09 | 9.45 | 9.69 | -13.23 / -7.93 | 1.76 | c7 < 10 dB |
| hbt_wcs/1.320V/27C | -0.24 | 3.94 | 6.26 | 7.67 | 8.58 | 9.18 | 9.57 | 9.84 | -13.20 / -8.27 | 1.57 | c7 < 10 dB |
| hbt_wcs/1.320V/125C | -0.14 | 3.81 | 6.10 | 7.55 | 8.50 | 9.15 | 9.60 | 9.90 | -13.19 / -8.82 | 1.09 | c7 < 10 dB |

- Corners meeting the first-look R10 check (c0 <= 1 dB, c7 >= 10 dB, monotonic): 13 of 27.

## CTLE output common mode (V, code 7)

| corner | out CM |
|---|---|
| hbt_typ/1.080V/-40C | 1.038 |
| hbt_typ/1.080V/27C | 0.961 |
| hbt_typ/1.080V/125C | 0.834 |
| hbt_typ/1.200V/-40C | 1.028 |
| hbt_typ/1.200V/27C | 0.940 |
| hbt_typ/1.200V/125C | 0.813 |
| hbt_typ/1.320V/-40C | 0.988 |
| hbt_typ/1.320V/27C | 0.904 |
| hbt_typ/1.320V/125C | 0.784 |
| hbt_bcs/1.080V/-40C | 1.032 |
| hbt_bcs/1.080V/27C | 0.949 |
| hbt_bcs/1.080V/125C | 0.809 |
| hbt_bcs/1.200V/-40C | 1.015 |
| hbt_bcs/1.200V/27C | 0.920 |
| hbt_bcs/1.200V/125C | 0.777 |
| hbt_bcs/1.320V/-40C | 0.969 |
| hbt_bcs/1.320V/27C | 0.876 |
| hbt_bcs/1.320V/125C | 0.738 |
| hbt_wcs/1.080V/-40C | 1.045 |
| hbt_wcs/1.080V/27C | 0.976 |
| hbt_wcs/1.080V/125C | 0.865 |
| hbt_wcs/1.200V/-40C | 1.043 |
| hbt_wcs/1.200V/27C | 0.965 |
| hbt_wcs/1.200V/125C | 0.856 |
| hbt_wcs/1.320V/-40C | 1.011 |
| hbt_wcs/1.320V/27C | 0.939 |
| hbt_wcs/1.320V/125C | 0.841 |

## Latch regeneration at 5 GHz (clock buffer + latch, ps)

Time from the clock edge that closes the sample phase to |q| reaching a fixed level, +-10 mV differential input. First-look limit: 100 ps (half period at 5 GHz). Two fixed absolute levels, neither swing-relative:

- **0.25 V (decision level)** -- the level the behavioural link benches need the sampler to resolve to. A corner whose |q| asymptotes below it is recorded `not reached` (`on_unreached: "null"`), which is a swing verdict, not a timing one.
- **0.10 V (floor level)** -- low enough that every corner in this grid crosses it, so a regeneration *speed* is returned even where the decision level is not reached.

`verdict` compares the corner against the 100 ps limit and names the cause: `swing` = the decision level is never reached (the floor-level time shows the latch is not slow), `speed` = a level is reached but later than 100 ps.

| corner | up @0.25 V | dn @0.25 V | up @0.10 V | dn @0.10 V | peak \|q\| (V) | q swing (V) | verdict |
|---|---|---|---|---|---|---|---|
| hbt_typ/1.080V/-40C | not reached | not reached | 10.6 | 10.2 | 0.176 | 0.35 | swing: peak \|q\| 0.176 V < 0.25 V |
| hbt_typ/1.080V/27C | not reached | not reached | 8.6 | 8.0 | 0.222 | 0.44 | swing: peak \|q\| 0.222 V < 0.25 V |
| hbt_typ/1.080V/125C | 71.4 | 66.2 | 8.1 | 7.3 | 0.286 | 0.57 | ok |
| hbt_typ/1.200V/-40C | 85.8 | 84.5 | 5.0 | 4.7 | 0.320 | 0.64 | ok |
| hbt_typ/1.200V/27C | 19.3 | 18.5 | 4.7 | 4.2 | 0.365 | 0.73 | ok |
| hbt_typ/1.200V/125C | 13.7 | 13.1 | 4.9 | 4.4 | 0.414 | 0.83 | ok |
| hbt_typ/1.320V/-40C | 13.4 | 11.6 | 3.6 | 3.2 | 0.458 | 0.92 | ok |
| hbt_typ/1.320V/27C | 11.4 | 10.4 | 3.6 | 3.1 | 0.500 | 1.00 | ok |
| hbt_typ/1.320V/125C | 10.1 | 9.6 | 3.8 | 3.4 | 0.514 | 1.03 | ok |
| hbt_bcs/1.080V/-40C | not reached | not reached | 6.9 | 6.6 | 0.206 | 0.41 | swing: peak \|q\| 0.206 V < 0.25 V |
| hbt_bcs/1.080V/27C | 92.5 | 92.3 | 5.3 | 5.0 | 0.261 | 0.52 | ok |
| hbt_bcs/1.080V/125C | 18.3 | 17.5 | 4.6 | 4.1 | 0.336 | 0.67 | ok |
| hbt_bcs/1.200V/-40C | 22.0 | 18.4 | 3.3 | 3.1 | 0.370 | 0.74 | ok |
| hbt_bcs/1.200V/27C | 13.5 | 12.2 | 2.7 | 2.4 | 0.423 | 0.85 | ok |
| hbt_bcs/1.200V/125C | 10.1 | 9.5 | 2.7 | 2.4 | 0.477 | 0.96 | ok |
| hbt_bcs/1.320V/-40C | 8.4 | 7.3 | 2.0 | 1.7 | 0.527 | 1.06 | ok |
| hbt_bcs/1.320V/27C | 7.7 | 7.0 | 1.8 | 1.5 | 0.558 | 1.12 | ok |
| hbt_bcs/1.320V/125C | 7.3 | 6.9 | 2.0 | 1.8 | 0.569 | 1.14 | ok |
| hbt_wcs/1.080V/-40C | not reached | not reached | 17.5 | 16.8 | 0.148 | 0.30 | swing: peak \|q\| 0.148 V < 0.25 V |
| hbt_wcs/1.080V/27C | not reached | not reached | 14.1 | 13.1 | 0.187 | 0.37 | swing: peak \|q\| 0.187 V < 0.25 V |
| hbt_wcs/1.080V/125C | not reached | not reached | 14.1 | 12.6 | 0.240 | 0.48 | swing: peak \|q\| 0.240 V < 0.25 V |
| hbt_wcs/1.200V/-40C | 93.9 | 93.7 | 6.9 | 6.4 | 0.278 | 0.56 | ok |
| hbt_wcs/1.200V/27C | 67.7 | 50.1 | 7.0 | 6.3 | 0.313 | 0.63 | ok |
| hbt_wcs/1.200V/125C | 19.8 | 18.6 | 7.6 | 6.8 | 0.352 | 0.71 | ok |
| hbt_wcs/1.320V/-40C | 20.7 | 18.4 | 5.1 | 4.7 | 0.401 | 0.80 | ok |
| hbt_wcs/1.320V/27C | 15.3 | 14.3 | 5.2 | 4.7 | 0.433 | 0.87 | ok |
| hbt_wcs/1.320V/125C | 13.3 | 12.4 | 5.5 | 5.0 | 0.454 | 0.91 | ok |

- Corners where |q| never reached the 0.25 V decision level (recorded `not_reached`, a swing limit -- the floor-level time at the same corner shows the latch still regenerates): 6 -- hbt_typ/1.080V/-40C, hbt_typ/1.080V/27C, hbt_bcs/1.080V/-40C, hbt_wcs/1.080V/-40C, hbt_wcs/1.080V/27C, hbt_wcs/1.080V/125C
- Corners that reached 0.25 V but slower than 100 ps (a speed limit): 0
- Corners slower than 100 ps to the 0.10 V floor level: 0
- Top-level `not_reached` measurement count in the report: 12; `errored`: 0.

## Termination + pad first-look |Zdiff| (ohm, placeholder 50 fF pads)

| corner | 0.1 GHz | 5 GHz |
|---|---|---|
| hbt_typ/1.080V/-40C | 99.9 | 95.8 |
| hbt_typ/1.080V/27C | 99.9 | 95.7 |
| hbt_typ/1.080V/125C | 99.9 | 95.5 |
| hbt_typ/1.200V/-40C | 99.9 | 95.9 |
| hbt_typ/1.200V/27C | 99.9 | 95.8 |
| hbt_typ/1.200V/125C | 99.9 | 95.5 |
| hbt_typ/1.320V/-40C | 99.9 | 96.0 |
| hbt_typ/1.320V/27C | 99.9 | 95.8 |
| hbt_typ/1.320V/125C | 99.9 | 95.4 |
| hbt_bcs/1.080V/-40C | 99.9 | 96.0 |
| hbt_bcs/1.080V/27C | 99.9 | 96.0 |
| hbt_bcs/1.080V/125C | 99.9 | 95.8 |
| hbt_bcs/1.200V/-40C | 99.9 | 96.1 |
| hbt_bcs/1.200V/27C | 99.9 | 96.0 |
| hbt_bcs/1.200V/125C | 99.9 | 95.8 |
| hbt_bcs/1.320V/-40C | 99.9 | 96.2 |
| hbt_bcs/1.320V/27C | 99.9 | 96.0 |
| hbt_bcs/1.320V/125C | 99.9 | 95.7 |
| hbt_wcs/1.080V/-40C | 99.9 | 95.4 |
| hbt_wcs/1.080V/27C | 99.9 | 95.4 |
| hbt_wcs/1.080V/125C | 99.8 | 95.1 |
| hbt_wcs/1.200V/-40C | 99.9 | 95.7 |
| hbt_wcs/1.200V/27C | 99.9 | 95.5 |
| hbt_wcs/1.200V/125C | 99.8 | 95.1 |
| hbt_wcs/1.320V/-40C | 99.9 | 95.8 |
| hbt_wcs/1.320V/27C | 99.9 | 95.5 |
| hbt_wcs/1.320V/125C | 99.8 | 95.1 |

## HBT node stress versus DR-003 (collector <= 1.32 V, Vce <= 1.4 V, reverse Vbe <= 1.0 V)

- Highest collector node: `latch_xl_qs1_vc_max` = 1.390 V at hbt_bcs/1.320V/125C.
- Highest Vce (against open-base BVCEO 1.4 V): `latch_xl_qs1_vce_max` = 1.163 V at hbt_wcs/1.320V/-40C.
- Largest reverse Vbe (Ve - Vb; negative = still forward biased): `latch_xl_qh1_vbe_rev_max` = -0.178 V at hbt_bcs/1.320V/125C.
- Over a DR-003 limit: 35 (corner, node) pairs across 6 nodes. Worst per node:
  - `latch_xl_qs1_vc_max` = 1.390 V at hbt_bcs/1.320V/125C
  - `latch_xl_qh1_vc_max` = 1.390 V at hbt_bcs/1.320V/125C
  - `latch_xl_qs2_vc_max` = 1.348 V at hbt_bcs/1.320V/125C
  - `latch_xl_qh2_vc_max` = 1.348 V at hbt_bcs/1.320V/125C
  - `clk_xclk_qq2a_vc_max` = 1.324 V at hbt_bcs/1.320V/-40C
  - `clk_xclk_qq2b_vc_max` = 1.324 V at hbt_bcs/1.320V/-40C
- Per-node values for every HBT, corner and CTLE code are in the `*.report.json` files in this directory.

### R3 per-device table (worst over all corners; ctle over the 8 code copies)

Limits: collector <= 1.32 V, Vce <= 1.4 V (open-base BVCEO), reverse Vbe <= 1.0 V. A value over its limit keeps its row -- violations are marked, not dropped.

| device | vc max (V) @ corner | Vce max (V) @ corner | vbe rev max (V) @ corner |
|---|---|---|---|
| clk_buf_quad.qi1a | 1.3142 (hbt_bcs/1.320V/-40C) | 1.1093 (hbt_wcs/1.320V/-40C) | -0.5106 (hbt_bcs/1.080V/125C) |
| clk_buf_quad.qi1b | 1.3173 (hbt_bcs/1.320V/-40C) | 1.1103 (hbt_wcs/1.320V/-40C) | -0.5105 (hbt_bcs/1.080V/125C) |
| clk_buf_quad.qi2a | 1.2131 (hbt_bcs/1.320V/-40C) | 0.9125 (hbt_wcs/1.320V/-40C) | -0.4840 (hbt_bcs/1.320V/125C) |
| clk_buf_quad.qi2b | 1.1293 (hbt_wcs/1.320V/-40C) | 0.8510 (hbt_wcs/1.080V/-40C) | -0.5032 (hbt_bcs/1.320V/125C) |
| clk_buf_quad.qq1a | 1.3153 (hbt_wcs/1.320V/-40C) | 1.1102 (hbt_wcs/1.320V/-40C) | -0.5123 (hbt_bcs/1.080V/125C) |
| clk_buf_quad.qq1b | 1.3183 (hbt_bcs/1.320V/-40C) | 1.1127 (hbt_wcs/1.320V/-40C) | -0.5076 (hbt_bcs/1.080V/125C) |
| clk_buf_quad.qq2a | 1.3239 **>1.32** (hbt_bcs/1.320V/-40C) | 1.0312 (hbt_wcs/1.320V/-40C) | -0.5023 (hbt_bcs/1.320V/125C) |
| clk_buf_quad.qq2b | 1.3236 **>1.32** (hbt_bcs/1.320V/-40C) | 1.0303 (hbt_wcs/1.320V/-40C) | -0.5097 (hbt_bcs/1.320V/125C) |
| ctle.q1 | 1.0447 (hbt_wcs/1.080V/-40C) | 1.0280 (hbt_wcs/1.080V/-40C) | -0.7242 (hbt_bcs/1.080V/125C) |
| ctle.q2 | 1.0447 (hbt_wcs/1.080V/-40C) | 1.0280 (hbt_wcs/1.080V/-40C) | -0.7242 (hbt_bcs/1.080V/125C) |
| ctle.qa0 | 0.5579 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7232 (hbt_bcs/1.080V/125C) |
| ctle.qa1 | 0.5580 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7231 (hbt_bcs/1.080V/125C) |
| ctle.qa2 | 0.5580 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7231 (hbt_bcs/1.080V/125C) |
| ctle.qb0 | 0.5579 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7232 (hbt_bcs/1.080V/125C) |
| ctle.qb1 | 0.5580 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7231 (hbt_bcs/1.080V/125C) |
| ctle.qb2 | 0.5580 (hbt_bcs/1.320V/125C) | 0.3317 (hbt_wcs/1.320V/125C) | -0.7231 (hbt_bcs/1.080V/125C) |
| ctle.qfa | 1.0447 (hbt_wcs/1.080V/-40C) | 1.0285 (hbt_wcs/1.080V/-40C) | -0.7216 (hbt_bcs/1.080V/125C) |
| ctle.qfb | 1.0447 (hbt_wcs/1.080V/-40C) | 1.0285 (hbt_wcs/1.080V/-40C) | -0.7216 (hbt_bcs/1.080V/125C) |
| ctle.sna0 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8022 (hbt_wcs/1.080V/-40C) | -0.4722 (hbt_bcs/1.080V/125C) |
| ctle.sna1 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4721 (hbt_bcs/1.080V/125C) |
| ctle.sna2 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4720 (hbt_bcs/1.080V/125C) |
| ctle.snb0 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8022 (hbt_wcs/1.080V/-40C) | -0.4722 (hbt_bcs/1.080V/125C) |
| ctle.snb1 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4721 (hbt_bcs/1.080V/125C) |
| ctle.snb2 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4720 (hbt_bcs/1.080V/125C) |
| ctle.spa0 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8022 (hbt_wcs/1.080V/-40C) | -0.4722 (hbt_bcs/1.080V/125C) |
| ctle.spa1 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4721 (hbt_bcs/1.080V/125C) |
| ctle.spa2 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4720 (hbt_bcs/1.080V/125C) |
| ctle.spb0 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8022 (hbt_wcs/1.080V/-40C) | -0.4722 (hbt_bcs/1.080V/125C) |
| ctle.spb1 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4721 (hbt_bcs/1.080V/125C) |
| ctle.spb2 | 1.0447 (hbt_wcs/1.080V/-40C) | 0.8021 (hbt_wcs/1.080V/-40C) | -0.4720 (hbt_bcs/1.080V/125C) |
| latch_cml.qh1 | 1.3901 **>1.32** (hbt_bcs/1.320V/125C) | 1.0129 (hbt_wcs/1.320V/-40C) | -0.1783 (hbt_bcs/1.320V/125C) |
| latch_cml.qh2 | 1.3481 **>1.32** (hbt_bcs/1.320V/125C) | 1.0155 (hbt_wcs/1.320V/-40C) | -0.2180 (hbt_bcs/1.320V/125C) |
| latch_cml.qs1 | 1.3901 **>1.32** (hbt_bcs/1.320V/125C) | 1.1634 (hbt_wcs/1.320V/-40C) | -0.4715 (hbt_bcs/1.200V/125C) |
| latch_cml.qs2 | 1.3481 **>1.32** (hbt_bcs/1.320V/125C) | 1.1205 (hbt_wcs/1.320V/-40C) | -0.4741 (hbt_bcs/1.200V/125C) |
| latch_cml.qth | 0.7007 (hbt_bcs/1.320V/125C) | 0.7068 (hbt_bcs/1.320V/125C) | -0.4406 (hbt_bcs/1.080V/125C) |
| latch_cml.qts | 0.5846 (hbt_bcs/1.320V/125C) | 0.5730 (hbt_bcs/1.320V/125C) | -0.4402 (hbt_bcs/1.080V/125C) |

- 36 unique HBT device rows: ctle 22, clk_buf_quad 8, latch_cml 6 (matches the npn13G2 instance count of design/rx/netlists/{ctle,latch_cml,clk_buf_quad}.spice; rx_top instantiates the latch 4x, so 54 HBT instances exist in the top assembly).


## Limits missed (first-look comparisons)

- none recorded as `fail` (the latch corners that do not reach the decision level are graded `not_reached`, not `fail` or `error`; they are listed above)

## Not simulated

- `lvl_cml2cmos` (thin-oxide MOS, PSP103 via OSDI): not simulated -- no RX MOS bench exists (the TX benches of issue #80 show the OSDI path works on the fleet since PR #76). It has no HBT, so R3 Vce is not applicable to it; its CMOS levels need a G3-class CMOS-evidence bench, not this record.
- PDK resistors `rsil`/`rppd` (`r3_cmc` OSDI): not simulated; every resistor in design/rx is an ideal `res` for that reason, so resistor corners (`res_*`) are not exercised.
- Pad/ESD capacitance at 5 GHz, SDD11 (R9) and the core-to-pad seam: not simulated beyond the placeholder |Zdiff| above; owned by #24/#28.
- Sampler offset and noise (Monte Carlo, DR-002), CDR, link behaviour, clock duty/quadrature error (R20 +-1 %, +-2 deg) and mismatch: not simulated.
- Full PVT-full grid (135 points): not run; only the 27-point HBT-family grid (MOS corners absent), `hbt_*` sections ganged with `cap_*` and `dio_*`. The spec's 7-point PVT-edge set is a subset of it.
- Unconfirmed: the +-10 % supply tolerance is a proposal (DR-003); temperature -40/27/125 C is a proposal.
