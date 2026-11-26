# TX R3 per-device Vce record 20261123-211956-ee22e3c-vce

**Sizing evidence, not a spec result and not a measurement.** This is the R3 evidence pass of issue #242 (gate G2, row R3 of tracker #238): per-device Vce, collector and reverse-Vbe maxima, transient peaks included, over each bench family's full PVT grid including the +10 % supply (1.32 V). Nothing here is measured, and no `spec/` row is graded.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- `tx_sizing_ffe0_bcs.sp` sha256 `4b10084b91cd2cb1434879b2414957f7c14442bacc16be75b617b9ea4cc86e08`, `tx_sizing_ffe0_bcs.request.json` sha256 `3355c21c9d32f326980ee546791508d8a3f375986d344c8f0dc8bf213cc0173d`
- `tx_sizing_ffe0_typ.sp` sha256 `208f8e7b480f6c5ed3bda52d0d4ef240c6582cc99598ba544ce0c77c4a6dc78c`, `tx_sizing_ffe0_typ.request.json` sha256 `03b106b815609bc010c25d868c6d8296cc802c07a25911fc67dd78550c461aa6`
- `tx_sizing_ffe0_wcs.sp` sha256 `f68f771cff0bf3e23fdec40dacca4c051854e5907871e8de58d88b663c8f95c6`, `tx_sizing_ffe0_wcs.request.json` sha256 `cb93ad45c7e18dafbbb6185895fef46179f9629861e43fb7728c39ac71a31b5e`
- `tx_sizing_ffe1_bcs.sp` sha256 `4378fe58793cdffb2d4d70c6bd92eb75f89f44febb39db0579d582d464d3acb0`, `tx_sizing_ffe1_bcs.request.json` sha256 `0b7ec62999b6616d13b802ab699f9b3d4a162db0fe3c5751474eb193095ed43d`
- `tx_sizing_ffe1_typ.sp` sha256 `d53bd15bdbe437c08933a1406c6f110e437af5f43e784f49223a1bc1034dd7a0`, `tx_sizing_ffe1_typ.request.json` sha256 `09561f8af23db2130bc102c44b06accc9c7cb763915d0581458de3dedc886238`
- `tx_sizing_ffe1_wcs.sp` sha256 `0f44d414866682ce1175421a63804747959fcd408714f8e90fabe2b5b0f65b41`, `tx_sizing_ffe1_wcs.request.json` sha256 `fafe5717e56b2c23032a23e563a054a65087b1cca0284e37be2f5ec37049b6fb`
- `tx_mos_mux2to1_cml.sp` sha256 `e358b401aeb438ea9e4913d7faebb001db145887919cc170f9f13ea1ffb8f639`, `tx_mos_mux2to1_cml.request.json` sha256 `db5f3400639d5d17a914887a4ab5b23504e6680b17f1a185efe63f07e39adcf8`
- `tx_mos_ffe_en.sp` sha256 `aff84b6e7f59fb900b9e523f8df3be6a2b2b5683cac8050255c8ebe7ab9aac97`, `tx_mos_ffe_en.request.json` sha256 `3dec90f406e3447e04609f83d5cc649f66220c93fd40dd5633119b5f010d3365`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `7560c58c40f02776081d1eb27b67d3373c5750c9abd18d81932261b45b32f331`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`
- netlist `design/tx/netlists/mux2to1_cml.spice` sha256 `44e54544e7b6712b608eebe4b77624f738d3e981a5b634043e0198379e9f0f7f`
- netlist `design/tx/netlists/ffe_en.spice` sha256 `1d3f8b9d5b58779edb3aa9776a635327dc42f69739bf2ae0d920ffecff4f1094`
- the mux bench also inlines `bias` + `predriver` (main); their HBTs are the tx_sizing / ffe_en rows above -- the same cells in a loaded context.

## Run
- tx_sizing_ffe0_bcs exit=0; tx_sizing_ffe0_typ exit=0; tx_sizing_ffe0_wcs exit=0; tx_sizing_ffe1_bcs exit=0; tx_sizing_ffe1_typ exit=0; tx_sizing_ffe1_wcs exit=0; tx_mos_mux2to1_cml exit=4; tx_mos_ffe_en exit=0
- ffe0_bcs: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-946b4c9496ad`
- ffe0_typ: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-495dc0105fde`
- ffe0_wcs: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-f8ccc686072c`
- ffe1_bcs: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-5d6052cab3ef`
- ffe1_typ: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-4087ca4d7787`
- ffe1_wcs: status **pass** (9/9 corners pass, 0 fail, 0 error), backend job `klt-sim-af430db63fa1`
- tx_mos_mux2to1_cml: status **error** (43/45 corners pass, 0 fail, 2 error), backend job `klt-sim-0bbef09e6561`
- tx_mos_ffe_en: status **pass** (45/45 corners pass, 0 fail, 0 error), backend job `klt-sim-323f13df7d6f`

## Failing or erroring corners (kept, not dropped)

- tx_mos_mux2to1_cml/ss_wcs/1.080V/-40C: error measurement measurement 'rise_pm30mv_s' produced no value -- ngspice reported: out of interval
- tx_mos_mux2to1_cml/ss_wcs/1.080V/27C: error measurement measurement 'rise_pm30mv_s' produced no value -- ngspice reported: out of interval

## HBT enumeration (design/tx/netlists/*.spice)

| cell | HBT devices | instances in tx_top | R3 Vce covered by |
|---|---|---|---|
| `bias` | 1 | 1 | tx_sizing benches; ffe_en bench (re-measured there) |
| `predriver` | 3 | 2 (6 HBTs) | tx_sizing benches (`pre_main`, `pre_post`) |
| `driver_ffe` | 12 | 1 | tx_sizing benches |
| `mux2to1_cml` | 4 | 2 (8 HBTs) | tx_mos_mux2to1_cml |
| `ffe_en` | 0 | 1 | n/a -- MOS and resistors only |
| `tx_lvl_cml2cmos` | 0 | 1 | n/a -- **no HBT, not applicable to R3 Vce**; CMOS-level evidence is G3-class, see `records/20261110-224611-4092fc2-mos/` (45/45 corners) |
| `pad_esd` | 0 | 1 | n/a -- diodes only |

- 20 unique HBT devices; 27 HBT instances in `tx_top`. The per-device table below has 24 rows: the 19 devices of the tx_sizing bench (1 bias + 3 + 3 predriver instances + 12 driver), the 4 mux HBTs, and the ffe_en bench's bias device.

## R3 per-device table (worst over each grid, transient peaks included)

Limits: collector <= 1.32 V, Vce <= 1.4 V (open-base BVCEO, DR-003), reverse Vbe <= 1.0 V. A value over its limit keeps its row -- violations are marked, not dropped, and not fixed here (out of scope of #242).

| device | vc max (V) @ corner | Vce max (V) @ corner | vbe rev max (V) @ corner |
|---|---|---|---|
| bias.qref | 1.0603 (ffe1_wcs/wcs/1.320V/-40C) | 0.9751 (ffe1_wcs/wcs/1.320V/-40C) | -0.7720 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.q1 | 1.3113 (ffe1_wcs/wcs/1.320V/-40C) | 1.0085 (ffe1_wcs/wcs/1.200V/-40C) | -0.4766 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.q2 | 1.2772 (ffe1_wcs/wcs/1.320V/-40C) | 1.0086 (ffe1_wcs/wcs/1.200V/-40C) | -0.4792 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.qt | 0.5187 (ffe1_bcs/bcs/1.320V/125C) | 0.4220 (ffe0_bcs/bcs/1.320V/27C) | -0.7782 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.q1 | 1.3109 (ffe1_wcs/wcs/1.320V/-40C) | 1.0102 (ffe0_wcs/wcs/1.200V/-40C) | -0.4721 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.q2 | 1.2798 (ffe0_wcs/wcs/1.320V/-40C) | 1.0094 (ffe0_wcs/wcs/1.200V/-40C) | -0.4759 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.qt | 0.5187 (ffe1_bcs/bcs/1.320V/125C) | 0.4220 (ffe0_bcs/bcs/1.320V/27C) | -0.7760 (ffe0_bcs/bcs/1.080V/125C) |
| driver_ffe.qm1 | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.9779 (ffe0_typ/typ/1.320V/-40C) | -0.3603 (ffe1_bcs/bcs/1.320V/125C) |
| driver_ffe.qm2 | 1.2567 (ffe0_wcs/wcs/1.320V/-40C) | 0.9775 (ffe0_typ/typ/1.320V/-40C) | -0.3629 (ffe1_bcs/bcs/1.320V/125C) |
| driver_ffe.qtm | 0.4545 (ffe0_bcs/bcs/1.320V/125C) | 0.4147 (ffe0_wcs/wcs/1.320V/-40C) | -0.7782 (ffe0_bcs/bcs/1.080V/125C) |
| driver_ffe.qp0a | 1.2567 (ffe0_wcs/wcs/1.320V/-40C) | 0.9366 (ffe1_bcs/bcs/1.320V/-40C) | 0.2357 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp0b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.9392 (ffe1_bcs/bcs/1.320V/-40C) | 0.2347 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp0 | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 0.0001 (ffe0_wcs/wcs/1.080V/125C) |
| driver_ffe.qp1a | 1.2567 (ffe0_wcs/wcs/1.320V/-40C) | 0.9366 (ffe1_bcs/bcs/1.320V/-40C) | 0.2357 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp1b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.9392 (ffe1_bcs/bcs/1.320V/-40C) | 0.2347 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp1 | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 0.0001 (ffe0_wcs/wcs/1.080V/125C) |
| driver_ffe.qp2a | 1.2567 (ffe0_wcs/wcs/1.320V/-40C) | 0.9366 (ffe1_bcs/bcs/1.320V/-40C) | 0.2357 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp2b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.9392 (ffe1_bcs/bcs/1.320V/-40C) | 0.2347 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp2 | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 1.0716 (ffe0_bcs/bcs/1.320V/125C) | 0.0001 (ffe0_wcs/wcs/1.080V/125C) |
| mux2to1_cml.qa1 | 1.3185 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.8834 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | -0.4440 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qa2 | 1.3184 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.9489 (tx_mos_mux2to1_cml/fs_typ/1.320V/-40C) | -0.1440 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qb1 | 1.3185 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.9491 (tx_mos_mux2to1_cml/fs_typ/1.320V/-40C) | -0.1443 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qb2 | 1.3184 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.8837 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | -0.4443 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| bias.qref@ffe_en | 1.0574 (tx_mos_ffe_en/ss_wcs/1.320V/-40C) | 0.9716 (tx_mos_ffe_en/ss_wcs/1.320V/-40C) | -0.7096 (tx_mos_ffe_en/fs_typ/1.080V/125C) |

- cells over an R3 limit in these grids: **0** (the mux collector findings at the 1.32 V supply are the known open ones, kept from `records/20261110-224611-4092fc2-mos/`; see the failing-corners list above).

## Grids and caveats

- tx_sizing (HBT set): hbt typ/bcs/wcs ganged with cap + res and the matching resistor sheet scale, one process per deck, x 1.08/1.2/1.32 V x -40/27/125 C = 9 corners per deck, x 6 decks (3 processes x FFE off / all three post slices on) = 54 corners. tx_mos (mux, ffe_en): 5 MOS process pairings x 3 supplies x 3 temperatures = 45 corners. Both include the +10 % supply (1.32 V). Mismatch/Monte Carlo is not run.
- The mux numbers cite the bench's assumed clock swing: 0.4 V per side (0.8 V differential peak-to-peak), an assumption, not a spec value (#98 is the open spec question). If #98 changes the swing, the mux rows are re-recorded after it lands, not before.
- The HBT decks' `rsil` is the behavioural stand-in with the corner sheet scale (see sim/tx/README.md); the mux and ffe_en decks use the real `r3_cmc` resistors via `osdi_preload`.
- Collector (`vc_max_*`) is per node, so devices sharing a collector node (e.g. `driver_ffe.qm2` and `driver_ffe.qp0a` at `cop`) repeat that node's value; Vce and reverse Vbe are per device.
- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not a real upstream eye; the pad network per TX leg is the 4 ohm stand-in + extracted 70.66 fF pad-metal C + PDK ESD clamp diodes (issue #142).

## Headroom cost against the baseline (issue #265)

Baseline is `records/20261123-022802-fedf656-vce/` (no load series resistor). Change: predriver `RS` 10 ohm (vdd to a `vl` return for `RL1`/`RL2`, both instances) and mux `RSm` 8 ohm (vdd to `vlm` for `RLp`/`RLn`). Minima at the 1.08 V corners, from the raw reports:

| quantity | baseline | this record |
|---|---|---|
| `vce_min_pre_main_tail` | 0.0487 V (ffe0_wcs/wcs/1.080V/-40C) | 0.0487 V (same corner) |
| `vce_min_drv_tail_main` | 0.1089 V (ffe1_wcs/wcs/1.080V/-40C) | 0.0959 V (same corner) |
| steady pad differential `r4_steady_hi - r4_steady_lo`, worst (smallest) at 1.08 V | 0.1320 V (ffe1_wcs/wcs/1.080V/-40C) | 0.1238 V (same corner) |

- R4 asks 500 mVppd into 100 ohm; the baseline steady swing was already far under it at 1.08 V. This change lowers the worst-corner swing by about 8 mV (6 %) and does not cause that gap. Not graded here and not relaxed.
- Raw collector peaks, worst per node, all <= 1.32 V: predriver main q1 1.3113 V (ffe1_wcs/wcs/1.320V/-40C), predriver post q1 1.3109 V (ffe0_wcs and ffe1_wcs families, wcs/1.320V/-40C), mux 1.3185 V (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C). The mux margin is 1.5 mV, thin. Reverse Vbe stays negative or below 0.22 V everywhere (limit 1.0 V).
- `tx_mos_mux2to1_cml`: 43 pass, 0 fail, 2 error. The two errors are the baseline's missing rising +-30 mV crossings at `ss_wcs/1.080V/-40C` and `ss_wcs/1.080V/27C` (stress values present, crossing absent). The fixed-threshold edge times are a proxy for R7 only, not a measurement of it.
- The sizing bench's fixed-threshold edge times were not compared in this section.

## Erratum (2026-11-26, PR #270, issue #273)

The maximum reverse Vbe in this run is **0.2357 V** (`vbe_rev_max_drv_post2_p`
= 0.235666 V at `ffe0_bcs/bcs/1.320V/125C`), below R3's 1.0 V limit.
The 0.22 V figure in the headroom summary came from the baseline run, whose
maximum was 0.216057 V.

The open mux collector violations cited below the per-device table belong
to the baseline. Its mux collector peaked at 1.32470 V. With the 8 ohm load
return, the peak was **1.31848 V** at `ss_wcs/1.320V/-40C` over 6–10 ns
with the assumed 0.4 V per-side clock swing. All 45 simulated mux points
had collector results below 1.32 V, including the two `ss_wcs/1.080V` points
at -40 and 27 °C where the differential edge crossings were missing. The
five selected MOS/HBT pairings cover 45 of R3's 135 mux points. The other
90 points remain unverified.
