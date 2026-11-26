# RX MOS-cell sizing record 20261123-025944-cd608e7-mos

**Sizing evidence, not a spec result and not a measurement.** Simulated at schematic level: no extracted parasitics (the cell has no
layout), ideal clock and data sources. No `spec/` row is graded here. The limits in the request are
first-look bounds that grade this record only; DR-008 item 3 leaves the converter unsized and
unspecified.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49` (layout/toolchain.json)
- `sim/rx/lvl_cml2cmos.sp` sha256 `b4c38242f06b4020a9e38188a3a23a922bb486484eedc4902c1eb7ec67033429`, `lvl_cml2cmos.request.json` sha256 `52c413e39c37ef8ce1dd4e33a5c55f52c5e985e72d84a09bddd1d6691959f8c1`
- netlists, via `.include`: `design/rx/netlists/latch_cml.spice` sha256 `f829d16d83c2bc026d5aff9b7edc14206956a1c73b31df5d29fc2ca1b368166a`, `design/rx/netlists/clk_buf_quad.spice` sha256 `95f3356809f3bff3f6d1c25738b3faa73182ce099689abf19f7417e2018ed148`, `design/rx/netlists/lvl_cml2cmos.spice` sha256 `802fe8bcc7f3bb904d6b716b04c920826d3ad6d0f53f5d9a2e7f9d8612226175`
- Circuit: the `latch_regen` deck (clock buffer + `latch_cml`) with one `lvl_cml2cmos` on `qp`/`qn`, as `Xlvl_d0` sits on `Xlat_d0` in `design/rx/netlists/rx_top.spice`. `Xlvl_d180`, `Xlvl_e90` and `Xlvl_e270` are the same cell on equivalent latch outputs (same clock amplitude and buffering), so this one instance stands for the four.
- Input stimulus: ideal 5 GHz four-phase clock, +-150 mV per phase about 0.8333 vdd, ideal quadrature and 50 % duty; +-10 mV differential data toggling every 400 ps. The latch output `qp`/`qn` is therefore the 1010 stream of a 5 Gb/s per-wire sampler output (200 ps per bit, the fastest toggle the converter sees) at the latch's own swing and common mode, both read per corner in the table.
- Load: 20 fF on `d0` to ground, an assumption (the CMOS deserializer behind the converter does not exist yet); the same lumped load as the TX clock-converter bench.
- Corner set: 5 MOS process corners (tt/ff/ss/fs/sf) x 1.08/1.2/1.32 V x -40/27/125 C = 45 corners. Each MOS corner is ganged with an HBT / CAP / RES section as in `sim/tx/make_tb.py` (tt_typ, ff_bcs, ss_wcs, fs_typ, sf_typ), so the latch moves with the converter. Mismatch and Monte Carlo are not run.
- Models: MOS is PSP103 through `osdi_preload` (psp103, psp103_nqs, r3_cmc, mosvar); the HBT is ngspice's built-in `npn13G2`; the latch and clock-buffer resistors are the ideal `res` of `design/rx` (the CAP / RES sections are ganged for the TX pairing and act on nothing here).
- Parasitics source: none. Schematic netlists, lumped load, no extracted or estimated interconnect.
- Applicable requirement: none is defined for this cell (DR-008 item 3; R2 leaves the level conversion open, DR-014 gate G3). First-look bounds used instead: the output reaches 90 % of vdd high and 10 % of vdd low, within 100 ps of the hold edge that regenerates the bit (half the 5 GHz clock period, the `latch_regen` limit: the time to the next sample phase).

## Run
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261123-025944-cd608e7-mos/lvl_cml2cmos.report.json lvl_cml2cmos.request.json`
- lvl_cml2cmos exit=3 (3 = a first-look limit failed; the report is complete)
- status **fail** (2/45 corners pass, 43 fail, 0 error, 132 measurements `not_reached`); engine worker, ngspice 47, backend job `klt-sim-0b9e4e0f9fe7`

## lvl_cml2cmos (latch-driven, 5 Gb/s 1010 per wire, 20 fF load)

`tpd` is from the latch differential output `q = v(qp) - v(qn)` crossing zero (which happens during the latch's sample phase) to `d0` crossing vdd/2. `hold->` is from the clock edge that closes the sample phase (`ck` falling, the edge the `latch_regen` record measures from) to `d0` reaching 90 % (LH) or 10 % (HL) of vdd; those two carry the 100 ps first-look limit. `tr`/`tf` are the 10 %-90 % output edges and `high`/`low` the time `d0` spends above and below vdd/2 for one bit (200 ps each at the input). `q swing` and `q CM` are the latch output the converter actually saw, its input gates being the only extra load on the latch. `Idd` is the converter's own supply current (through `Vddc`), averaged over 2-3 ns.

| corner | q swing (V) | q CM (V) | out hi (V) | out lo (V) | tpd LH (ps) | tpd HL (ps) | hold->90 % LH (ps) | hold->10 % HL (ps) | tr / tf (ps) | high / low (ps) | Idd (mA) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ff_bcs/1.080V/-40C | 0.41 | 0.987 | 0.011 | -0.018 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.354 | no high level: out hi 0.011 V < vdd/2 |
| ff_bcs/1.080V/125C | 0.67 | 0.914 | 1.098 | -0.014 | 198.8 | 207.1 | 143.0 | 154.1 | 57.7 / 66.4 | 207.8 / 192.1 | 0.346 | hold edge to 90 % LH 143.0 ps > 100 ps; hold edge to 10 % HL 154.1 ps > 100 ps |
| ff_bcs/1.080V/27C | 0.52 | 0.957 | 0.810 | -0.022 | 237.2 | 136.9 | not reached | 85.4 | not reached / not reached | 99.2 / 300.7 | 0.375 | LH edge stops at 0.810 V, under 90 % of vdd |
| ff_bcs/1.200V/-40C | 0.73 | 1.013 | 1.224 | -0.030 | 184.6 | 144.1 | 126.5 | 85.0 | 43.2 / 47.2 | 158.9 / 241.1 | 0.567 | hold edge to 90 % LH 126.5 ps > 100 ps |
| ff_bcs/1.200V/125C | 0.95 | 0.957 | 1.221 | -0.013 | 168.7 | 184.3 | 109.8 | 125.2 | 49.0 / 53.4 | 215.1 / 184.9 | 0.416 | hold edge to 90 % LH 109.8 ps > 100 ps; hold edge to 10 % HL 125.2 ps > 100 ps |
| ff_bcs/1.200V/27C | 0.84 | 0.983 | 1.221 | -0.027 | 177.5 | 160.0 | 118.6 | 99.7 | 45.0 / 48.8 | 181.7 / 218.2 | 0.493 | hold edge to 90 % LH 118.6 ps > 100 ps |
| ff_bcs/1.320V/-40C | 1.04 | 1.048 | 1.345 | -0.032 | 154.4 | 129.6 | 93.1 | 66.7 | 36.0 / 40.3 | 174.3 / 225.7 | 0.671 | ok |
| ff_bcs/1.320V/125C | 1.14 | 1.036 | 1.340 | -0.006 | 148.1 | 168.5 | 86.4 | 106.1 | 44.3 / 46.8 | 219.7 / 180.3 | 0.491 | hold edge to 10 % HL 106.1 ps > 100 ps |
| ff_bcs/1.320V/27C | 1.11 | 1.025 | 1.341 | -0.025 | 154.2 | 144.8 | 91.1 | 80.2 | 38.7 / 42.1 | 190.0 / 210.0 | 0.583 | ok |
| fs_typ/1.080V/-40C | 0.35 | 1.002 | 0.000 | -0.001 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.291 | no high level: out hi 0.000 V < vdd/2 |
| fs_typ/1.080V/125C | 0.57 | 0.941 | 0.086 | -0.021 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.225 | no high level: out hi 0.086 V < vdd/2 |
| fs_typ/1.080V/27C | 0.44 | 0.976 | 0.002 | -0.004 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.248 | no high level: out hi 0.002 V < vdd/2 |
| fs_typ/1.200V/-40C | 0.63 | 1.037 | 0.055 | -0.029 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.409 | no high level: out hi 0.055 V < vdd/2 |
| fs_typ/1.200V/125C | 0.82 | 0.989 | 1.208 | -0.022 | 210.5 | 192.2 | 162.7 | 139.9 | 64.0 / 66.7 | 181.2 / 218.7 | 0.383 | hold edge to 90 % LH 162.7 ps > 100 ps; hold edge to 10 % HL 139.9 ps > 100 ps |
| fs_typ/1.200V/27C | 0.72 | 1.012 | 0.778 | -0.027 | 239.4 | 114.6 | not reached | 71.2 | not reached / not reached | 74.7 / 325.1 | 0.410 | LH edge stops at 0.778 V, under 90 % of vdd |
| fs_typ/1.320V/-40C | 0.90 | 1.077 | 1.346 | -0.033 | 187.7 | 134.5 | 135.0 | 77.6 | 46.8 / 48.0 | 146.1 / 253.8 | 0.624 | hold edge to 90 % LH 135.0 ps > 100 ps |
| fs_typ/1.320V/125C | 1.02 | 1.055 | 1.339 | -0.022 | 181.0 | 180.9 | 128.5 | 123.7 | 55.2 / 55.4 | 199.4 / 200.6 | 0.460 | hold edge to 90 % LH 128.5 ps > 100 ps; hold edge to 10 % HL 123.7 ps > 100 ps |
| fs_typ/1.320V/27C | 0.99 | 1.057 | 1.343 | -0.031 | 185.8 | 152.3 | 132.1 | 93.8 | 49.9 / 50.6 | 165.9 / 234.0 | 0.544 | hold edge to 90 % LH 132.1 ps > 100 ps |
| sf_typ/1.080V/-40C | 0.35 | 1.002 | 0.007 | -0.012 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.288 | no high level: out hi 0.007 V < vdd/2 |
| sf_typ/1.080V/125C | 0.57 | 0.941 | 1.100 | -0.016 | 228.1 | 228.9 | 182.6 | 185.8 | 70.5 / 80.0 | 200.3 / 199.7 | 0.298 | hold edge to 90 % LH 182.6 ps > 100 ps; hold edge to 10 % HL 185.8 ps > 100 ps |
| sf_typ/1.080V/27C | 0.44 | 0.976 | 0.318 | -0.028 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.278 | no high level: out hi 0.318 V < vdd/2 |
| sf_typ/1.200V/-40C | 0.63 | 1.037 | 1.231 | -0.033 | 203.5 | 163.9 | 150.2 | 110.1 | 48.7 / 53.6 | 159.8 / 240.2 | 0.496 | hold edge to 90 % LH 150.2 ps > 100 ps; hold edge to 10 % HL 110.1 ps > 100 ps |
| sf_typ/1.200V/125C | 0.82 | 0.989 | 1.230 | -0.019 | 189.7 | 206.4 | 135.7 | 153.3 | 54.7 / 61.0 | 216.2 / 183.8 | 0.370 | hold edge to 90 % LH 135.7 ps > 100 ps; hold edge to 10 % HL 153.3 ps > 100 ps |
| sf_typ/1.200V/27C | 0.72 | 1.012 | 1.233 | -0.030 | 196.8 | 182.9 | 142.0 | 127.6 | 50.4 / 55.4 | 185.3 / 214.6 | 0.436 | hold edge to 90 % LH 142.0 ps > 100 ps; hold edge to 10 % HL 127.6 ps > 100 ps |
| sf_typ/1.320V/-40C | 0.91 | 1.077 | 1.354 | -0.034 | 167.1 | 148.0 | 110.8 | 90.2 | 40.3 / 43.7 | 179.9 / 220.0 | 0.598 | hold edge to 90 % LH 110.8 ps > 100 ps |
| sf_typ/1.320V/125C | 1.02 | 1.055 | 1.351 | -0.015 | 166.9 | 186.1 | 109.6 | 128.3 | 48.3 / 52.5 | 218.7 / 181.3 | 0.441 | hold edge to 90 % LH 109.6 ps > 100 ps; hold edge to 10 % HL 128.3 ps > 100 ps |
| sf_typ/1.320V/27C | 0.99 | 1.056 | 1.352 | -0.029 | 168.1 | 163.1 | 110.2 | 103.8 | 43.2 / 46.7 | 194.3 / 205.7 | 0.523 | hold edge to 90 % LH 110.2 ps > 100 ps; hold edge to 10 % HL 103.8 ps > 100 ps |
| ss_wcs/1.080V/-40C | 0.29 | 1.014 | 0.000 | -0.001 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.241 | no high level: out hi 0.000 V < vdd/2 |
| ss_wcs/1.080V/125C | 0.48 | 0.965 | 0.008 | -0.014 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.171 | no high level: out hi 0.008 V < vdd/2 |
| ss_wcs/1.080V/27C | 0.37 | 0.993 | 0.001 | -0.003 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.204 | no high level: out hi 0.001 V < vdd/2 |
| ss_wcs/1.200V/-40C | 0.55 | 1.062 | 0.012 | -0.025 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.339 | no high level: out hi 0.012 V < vdd/2 |
| ss_wcs/1.200V/125C | 0.70 | 1.021 | 1.165 | -0.026 | 240.4 | 204.4 | 210.2 | 159.2 | 86.4 / 79.4 | 163.5 / 236.4 | 0.328 | hold edge to 90 % LH 210.2 ps > 100 ps; hold edge to 10 % HL 159.2 ps > 100 ps |
| ss_wcs/1.200V/27C | 0.62 | 1.041 | 0.274 | -0.035 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.314 | no high level: out hi 0.274 V < vdd/2 |
| ss_wcs/1.320V/-40C | 0.79 | 1.106 | 1.346 | -0.037 | 204.0 | 151.0 | 155.5 | 98.5 | 50.7 / 52.7 | 146.2 / 253.7 | 0.554 | hold edge to 90 % LH 155.5 ps > 100 ps |
| ss_wcs/1.320V/125C | 0.91 | 1.086 | 1.349 | -0.025 | 200.4 | 202.2 | 152.2 | 150.3 | 60.4 / 62.2 | 201.2 / 198.7 | 0.413 | hold edge to 90 % LH 152.2 ps > 100 ps; hold edge to 10 % HL 150.3 ps > 100 ps |
| ss_wcs/1.320V/27C | 0.86 | 1.090 | 1.346 | -0.034 | 203.8 | 170.5 | 154.3 | 116.6 | 54.6 / 56.2 | 166.0 / 234.0 | 0.486 | hold edge to 90 % LH 154.3 ps > 100 ps; hold edge to 10 % HL 116.6 ps > 100 ps |
| tt_typ/1.080V/-40C | 0.35 | 1.002 | 0.002 | -0.004 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.292 | no high level: out hi 0.002 V < vdd/2 |
| tt_typ/1.080V/125C | 0.57 | 0.941 | 0.912 | -0.020 | 253.8 | 190.9 | not reached | 146.2 | not reached / not reached | 136.6 / 263.3 | 0.286 | LH edge stops at 0.912 V, under 90 % of vdd; hold edge to 10 % HL 146.2 ps > 100 ps |
| tt_typ/1.080V/27C | 0.44 | 0.976 | 0.008 | -0.015 | not reached | not reached | not reached | n/a | not reached / not reached | not reached / not reached | 0.253 | no high level: out hi 0.008 V < vdd/2 |
| tt_typ/1.200V/-40C | 0.63 | 1.037 | 1.060 | -0.031 | 222.9 | 134.1 | not reached | 81.9 | not reached / not reached | 110.8 / 289.1 | 0.490 | LH edge stops at 1.060 V, under 90 % of vdd |
| tt_typ/1.200V/125C | 0.82 | 0.989 | 1.224 | -0.020 | 197.0 | 202.7 | 145.7 | 149.6 | 58.8 / 62.3 | 205.2 / 194.8 | 0.379 | hold edge to 90 % LH 145.7 ps > 100 ps; hold edge to 10 % HL 149.6 ps > 100 ps |
| tt_typ/1.200V/27C | 0.72 | 1.012 | 1.215 | -0.030 | 209.4 | 168.8 | 158.4 | 114.1 | 55.5 / 58.2 | 158.7 / 241.2 | 0.443 | hold edge to 90 % LH 158.4 ps > 100 ps; hold edge to 10 % HL 114.1 ps > 100 ps |
| tt_typ/1.320V/-40C | 0.90 | 1.077 | 1.350 | -0.035 | 175.2 | 142.5 | 121.2 | 84.9 | 43.7 / 44.8 | 166.5 / 233.5 | 0.615 | hold edge to 90 % LH 121.2 ps > 100 ps |
| tt_typ/1.320V/125C | 1.02 | 1.055 | 1.346 | -0.019 | 172.2 | 183.9 | 117.5 | 126.0 | 51.8 / 53.0 | 211.3 / 188.7 | 0.452 | hold edge to 90 % LH 117.5 ps > 100 ps; hold edge to 10 % HL 126.0 ps > 100 ps |
| tt_typ/1.320V/27C | 0.99 | 1.056 | 1.346 | -0.031 | 175.5 | 158.1 | 120.0 | 98.8 | 46.7 / 47.6 | 182.0 / 218.0 | 0.536 | hold edge to 90 % LH 120.0 ps > 100 ps |

## Reading the grid

- Corners where `d0` never rose above vdd/2 in the window (the converter did not switch high): **14** -- ff_bcs/1.080V/-40C, fs_typ/1.080V/-40C, fs_typ/1.080V/125C, fs_typ/1.080V/27C, fs_typ/1.200V/-40C, sf_typ/1.080V/-40C, sf_typ/1.080V/27C, ss_wcs/1.080V/-40C, ss_wcs/1.080V/125C, ss_wcs/1.080V/27C, ss_wcs/1.200V/-40C, ss_wcs/1.200V/27C, tt_typ/1.080V/-40C, tt_typ/1.080V/27C.
- Corners where `d0` crossed vdd/2 but the LH edge stopped under 90 % of vdd: **4** -- ff_bcs/1.080V/27C, fs_typ/1.200V/27C, tt_typ/1.080V/125C, tt_typ/1.200V/-40C.
- Corners whose HL edge never came down to 10 % of vdd: **0**.
- Corners over the 100 ps first-look limit, hold edge to 90 % LH: **24** -- ff_bcs/1.080V/125C, ff_bcs/1.200V/-40C, ff_bcs/1.200V/125C, ff_bcs/1.200V/27C, fs_typ/1.200V/125C, fs_typ/1.320V/-40C, fs_typ/1.320V/125C, fs_typ/1.320V/27C, sf_typ/1.080V/125C, sf_typ/1.200V/-40C, sf_typ/1.200V/125C, sf_typ/1.200V/27C, sf_typ/1.320V/-40C, sf_typ/1.320V/125C, sf_typ/1.320V/27C, ss_wcs/1.200V/125C, ss_wcs/1.320V/-40C, ss_wcs/1.320V/125C, ss_wcs/1.320V/27C, tt_typ/1.200V/125C, tt_typ/1.200V/27C, tt_typ/1.320V/-40C, tt_typ/1.320V/125C, tt_typ/1.320V/27C.
- Corners over the 100 ps first-look limit, hold edge to 10 % HL: **18** -- ff_bcs/1.080V/125C, ff_bcs/1.200V/125C, ff_bcs/1.320V/125C, fs_typ/1.200V/125C, fs_typ/1.320V/125C, sf_typ/1.080V/125C, sf_typ/1.200V/-40C, sf_typ/1.200V/125C, sf_typ/1.200V/27C, sf_typ/1.320V/125C, sf_typ/1.320V/27C, ss_wcs/1.200V/125C, ss_wcs/1.320V/125C, ss_wcs/1.320V/27C, tt_typ/1.080V/125C, tt_typ/1.200V/125C, tt_typ/1.200V/27C, tt_typ/1.320V/125C.
- Corners inside both first-look limits with full levels: **2 of 45** -- ff_bcs/1.320V/-40C, ff_bcs/1.320V/27C.
- Hold edge to 90 % LH, over the 27 corners that reached it: 86.4 ps (ff_bcs/1.320V/125C) to 210.2 ps (ss_wcs/1.200V/125C).
- Hold edge to 10 % HL, over the 31 corners that reached it: 66.7 ps (ff_bcs/1.320V/-40C) to 185.8 ps (sf_typ/1.080V/125C).
- At 1.08 V: 0 of 15 corners inside both first-look limits.
- At 1.20 V: 0 of 15 corners inside both first-look limits.
- At 1.32 V: 2 of 15 corners inside both first-look limits.

## Failing or erroring corners (kept, not dropped)

- ff_bcs/1.080V/-40C: fail -- no high level: out hi 0.011 V < vdd/2
- ff_bcs/1.080V/125C: fail -- hold edge to 90 % LH 143.0 ps > 100 ps; hold edge to 10 % HL 154.1 ps > 100 ps
- ff_bcs/1.080V/27C: fail -- LH edge stops at 0.810 V, under 90 % of vdd
- ff_bcs/1.200V/-40C: fail -- hold edge to 90 % LH 126.5 ps > 100 ps
- ff_bcs/1.200V/125C: fail -- hold edge to 90 % LH 109.8 ps > 100 ps; hold edge to 10 % HL 125.2 ps > 100 ps
- ff_bcs/1.200V/27C: fail -- hold edge to 90 % LH 118.6 ps > 100 ps
- ff_bcs/1.320V/125C: fail -- hold edge to 10 % HL 106.1 ps > 100 ps
- fs_typ/1.080V/-40C: fail -- no high level: out hi 0.000 V < vdd/2
- fs_typ/1.080V/125C: fail -- no high level: out hi 0.086 V < vdd/2
- fs_typ/1.080V/27C: fail -- no high level: out hi 0.002 V < vdd/2
- fs_typ/1.200V/-40C: fail -- no high level: out hi 0.055 V < vdd/2
- fs_typ/1.200V/125C: fail -- hold edge to 90 % LH 162.7 ps > 100 ps; hold edge to 10 % HL 139.9 ps > 100 ps
- fs_typ/1.200V/27C: fail -- LH edge stops at 0.778 V, under 90 % of vdd
- fs_typ/1.320V/-40C: fail -- hold edge to 90 % LH 135.0 ps > 100 ps
- fs_typ/1.320V/125C: fail -- hold edge to 90 % LH 128.5 ps > 100 ps; hold edge to 10 % HL 123.7 ps > 100 ps
- fs_typ/1.320V/27C: fail -- hold edge to 90 % LH 132.1 ps > 100 ps
- sf_typ/1.080V/-40C: fail -- no high level: out hi 0.007 V < vdd/2
- sf_typ/1.080V/125C: fail -- hold edge to 90 % LH 182.6 ps > 100 ps; hold edge to 10 % HL 185.8 ps > 100 ps
- sf_typ/1.080V/27C: fail -- no high level: out hi 0.318 V < vdd/2
- sf_typ/1.200V/-40C: fail -- hold edge to 90 % LH 150.2 ps > 100 ps; hold edge to 10 % HL 110.1 ps > 100 ps
- sf_typ/1.200V/125C: fail -- hold edge to 90 % LH 135.7 ps > 100 ps; hold edge to 10 % HL 153.3 ps > 100 ps
- sf_typ/1.200V/27C: fail -- hold edge to 90 % LH 142.0 ps > 100 ps; hold edge to 10 % HL 127.6 ps > 100 ps
- sf_typ/1.320V/-40C: fail -- hold edge to 90 % LH 110.8 ps > 100 ps
- sf_typ/1.320V/125C: fail -- hold edge to 90 % LH 109.6 ps > 100 ps; hold edge to 10 % HL 128.3 ps > 100 ps
- sf_typ/1.320V/27C: fail -- hold edge to 90 % LH 110.2 ps > 100 ps; hold edge to 10 % HL 103.8 ps > 100 ps
- ss_wcs/1.080V/-40C: fail -- no high level: out hi 0.000 V < vdd/2
- ss_wcs/1.080V/125C: fail -- no high level: out hi 0.008 V < vdd/2
- ss_wcs/1.080V/27C: fail -- no high level: out hi 0.001 V < vdd/2
- ss_wcs/1.200V/-40C: fail -- no high level: out hi 0.012 V < vdd/2
- ss_wcs/1.200V/125C: fail -- hold edge to 90 % LH 210.2 ps > 100 ps; hold edge to 10 % HL 159.2 ps > 100 ps
- ss_wcs/1.200V/27C: fail -- no high level: out hi 0.274 V < vdd/2
- ss_wcs/1.320V/-40C: fail -- hold edge to 90 % LH 155.5 ps > 100 ps
- ss_wcs/1.320V/125C: fail -- hold edge to 90 % LH 152.2 ps > 100 ps; hold edge to 10 % HL 150.3 ps > 100 ps
- ss_wcs/1.320V/27C: fail -- hold edge to 90 % LH 154.3 ps > 100 ps; hold edge to 10 % HL 116.6 ps > 100 ps
- tt_typ/1.080V/-40C: fail -- no high level: out hi 0.002 V < vdd/2
- tt_typ/1.080V/125C: fail -- LH edge stops at 0.912 V, under 90 % of vdd; hold edge to 10 % HL 146.2 ps > 100 ps
- tt_typ/1.080V/27C: fail -- no high level: out hi 0.008 V < vdd/2
- tt_typ/1.200V/-40C: fail -- LH edge stops at 1.060 V, under 90 % of vdd
- tt_typ/1.200V/125C: fail -- hold edge to 90 % LH 145.7 ps > 100 ps; hold edge to 10 % HL 149.6 ps > 100 ps
- tt_typ/1.200V/27C: fail -- hold edge to 90 % LH 158.4 ps > 100 ps; hold edge to 10 % HL 114.1 ps > 100 ps
- tt_typ/1.320V/-40C: fail -- hold edge to 90 % LH 121.2 ps > 100 ps
- tt_typ/1.320V/125C: fail -- hold edge to 90 % LH 117.5 ps > 100 ps; hold edge to 10 % HL 126.0 ps > 100 ps
- tt_typ/1.320V/27C: fail -- hold edge to 90 % LH 120.0 ps > 100 ps
- 43 of 45 corners are graded other than `pass`; the per-corner cause is the `verdict` column above. Corners graded `pass`: ff_bcs/1.320V/-40C, ff_bcs/1.320V/27C.

## What this record does not establish

- Post-layout timing. The cell has no layout; no extracted parasitics, no wire model, no supply or ground network, no supply isolation between the CML and CMOS rails.
- The load the converter will actually drive. 20 fF is an assumption; the deserializer that follows `d0`, `d180`, `e90`, `e270` is not implemented, so its input capacitance, its setup time and the valid window it needs are unknown.
- A pass against a requirement. The converter has none; the limits here are first-look bounds, and a corner inside them is not evidence that the converter meets R2 or any other row.
- The latch's own limits. Where the latch does not regenerate enough swing (`latch_regen`, record 20261114-050716-eb34d10: six 1.080 V corners under 0.25 V peak |q|) the converter sees that swing; `q swing` shows it per corner so the cause stays visible.
- Mismatch, Monte Carlo, sampler offset, noise, jitter or data patterns other than 1010 per wire.

**Erratum (2026-11-26, [PR #254](https://github.com/2AMLogic/sg13g2-serdes/pull/254)).**
The two latch inputs each swing ±10 mV about the common mode with opposite
polarity, giving ±20 mV differential (40 mV peak to peak). Transitions start
every 200 ps and repeat with a 400 ps period. The [RX converter layout](../../../../layout/analog/rx/records/2026-11-23-9f3e17c/record.md)
has clean DRC and matching LVS. This run used schematic netlists and an
assumed 20 fF load. The 31 falling delays summarized above require an output
that first crossed vdd/2. Two further raw 10 % crossings occurred without a
valid high level, at 51.4 ps (`ss_wcs/1.200V/27C`) and 76.1 ps
(`sf_typ/1.080V/27C`). These clarifications use the original fleet report.
