# TX R3 per-device Vce record 20261123-022802-fedf656-vce

**Sizing evidence, not a spec result and not a measurement.** This is the R3 evidence pass of issue #242 (gate G2, row R3 of tracker #238): per-device Vce, collector and reverse-Vbe maxima, transient peaks included, over each bench family's full PVT grid including the +10 % supply (1.32 V). Nothing here is measured, and no `spec/` row is graded.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- `tx_sizing_ffe0_bcs.sp` sha256 `600dd5436b364e09207c97e68e12a4f0e1bbdebcfd3107fe3504e181b58c3506`, `tx_sizing_ffe0_bcs.request.json` sha256 `3355c21c9d32f326980ee546791508d8a3f375986d344c8f0dc8bf213cc0173d`
- `tx_sizing_ffe0_typ.sp` sha256 `24360593f58cd5e7bfa717540efd141206b5b0f7f248f30495f1ec9647c0968a`, `tx_sizing_ffe0_typ.request.json` sha256 `03b106b815609bc010c25d868c6d8296cc802c07a25911fc67dd78550c461aa6`
- `tx_sizing_ffe0_wcs.sp` sha256 `cdb0218f3556c17712c3b45aa2dfa476af037f62c8c02164f995014002ae949a`, `tx_sizing_ffe0_wcs.request.json` sha256 `cb93ad45c7e18dafbbb6185895fef46179f9629861e43fb7728c39ac71a31b5e`
- `tx_sizing_ffe1_bcs.sp` sha256 `4fe912016a82e230aea26ad6104feffe3dfa5936cee38d29b448ec43b7269707`, `tx_sizing_ffe1_bcs.request.json` sha256 `0b7ec62999b6616d13b802ab699f9b3d4a162db0fe3c5751474eb193095ed43d`
- `tx_sizing_ffe1_typ.sp` sha256 `d1e5eb2486b47558699e1e6285e0b96ad3fa3219d7845973e2e51effb6a046dd`, `tx_sizing_ffe1_typ.request.json` sha256 `09561f8af23db2130bc102c44b06accc9c7cb763915d0581458de3dedc886238`
- `tx_sizing_ffe1_wcs.sp` sha256 `838a35d7a5dee596845ca051eac31f3eb27172e45fe3db55ed8e10acfce58a9b`, `tx_sizing_ffe1_wcs.request.json` sha256 `fafe5717e56b2c23032a23e563a054a65087b1cca0284e37be2f5ec37049b6fb`
- `tx_mos_mux2to1_cml.sp` sha256 `d2fb5ffc8337849ed1fb2d95228b30c09ac5878006eb8035aa1e36d9ffe37ba0`, `tx_mos_mux2to1_cml.request.json` sha256 `db5f3400639d5d17a914887a4ab5b23504e6680b17f1a185efe63f07e39adcf8`
- `tx_mos_ffe_en.sp` sha256 `aff84b6e7f59fb900b9e523f8df3be6a2b2b5683cac8050255c8ebe7ab9aac97`, `tx_mos_ffe_en.request.json` sha256 `3dec90f406e3447e04609f83d5cc649f66220c93fd40dd5633119b5f010d3365`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `0108584d4e4bbe0272aecca85ad475ad71d4db36d445283a6c98549d3efe1f6d`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`
- netlist `design/tx/netlists/mux2to1_cml.spice` sha256 `612cb14e2bb4526e87ed79c5799034d8993f7c936f58c00f38fc622c92a22adc`
- netlist `design/tx/netlists/ffe_en.spice` sha256 `1d3f8b9d5b58779edb3aa9776a635327dc42f69739bf2ae0d920ffecff4f1094`
- the mux bench also inlines `bias` + `predriver` (main); their HBTs are the tx_sizing / ffe_en rows above -- the same cells in a loaded context.

## Run
- tx_sizing_ffe0_bcs exit=3; tx_sizing_ffe0_typ exit=3; tx_sizing_ffe0_wcs exit=3; tx_sizing_ffe1_bcs exit=3; tx_sizing_ffe1_typ exit=3; tx_sizing_ffe1_wcs exit=3; tx_mos_mux2to1_cml exit=4; tx_mos_ffe_en exit=0
- ffe0_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-84d27b089602`
- ffe0_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-955af88861fc`
- ffe0_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-f449e44e337a`
- ffe1_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-a8997424f4c8`
- ffe1_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-b07ac2465e5f`
- ffe1_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-4f14f92365c5`
- tx_mos_mux2to1_cml: status **error** (36/45 corners pass, 7 fail, 2 error), backend job `klt-sim-723e97841b9f`
- tx_mos_ffe_en: status **pass** (45/45 corners pass, 0 fail, 0 error), backend job `klt-sim-b1362601e2b8`

## Failing or erroring corners (kept, not dropped)

- ffe0_bcs/bcs/1.320V/-40C: fail
- ffe0_bcs/bcs/1.320V/125C: fail
- ffe0_bcs/bcs/1.320V/27C: fail
- ffe0_typ/typ/1.320V/-40C: fail
- ffe0_typ/typ/1.320V/125C: fail
- ffe0_typ/typ/1.320V/27C: fail
- ffe0_wcs/wcs/1.320V/-40C: fail
- ffe0_wcs/wcs/1.320V/125C: fail
- ffe0_wcs/wcs/1.320V/27C: fail
- ffe1_bcs/bcs/1.320V/-40C: fail
- ffe1_bcs/bcs/1.320V/125C: fail
- ffe1_bcs/bcs/1.320V/27C: fail
- ffe1_typ/typ/1.320V/-40C: fail
- ffe1_typ/typ/1.320V/125C: fail
- ffe1_typ/typ/1.320V/27C: fail
- ffe1_wcs/wcs/1.320V/-40C: fail
- ffe1_wcs/wcs/1.320V/125C: fail
- ffe1_wcs/wcs/1.320V/27C: fail
- tx_mos_mux2to1_cml/ff_bcs/1.320V/-40C: fail
- tx_mos_mux2to1_cml/fs_typ/1.320V/-40C: fail
- tx_mos_mux2to1_cml/sf_typ/1.320V/-40C: fail
- tx_mos_mux2to1_cml/sf_typ/1.320V/27C: fail
- tx_mos_mux2to1_cml/ss_wcs/1.080V/-40C: error measurement measurement 'rise_pm30mv_s' produced no value -- ngspice reported: out of interval
- tx_mos_mux2to1_cml/ss_wcs/1.080V/27C: error measurement measurement 'rise_pm30mv_s' produced no value -- ngspice reported: out of interval
- tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C: fail
- tx_mos_mux2to1_cml/ss_wcs/1.320V/27C: fail
- tx_mos_mux2to1_cml/tt_typ/1.320V/-40C: fail

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
| bias.qref | 1.0618 (ffe0_wcs/wcs/1.320V/-40C) | 0.9758 (ffe0_wcs/wcs/1.320V/-40C) | -0.7718 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.q1 | 1.3492 **>1.32** (ffe1_bcs/bcs/1.320V/125C) | 1.0539 (ffe1_wcs/wcs/1.320V/-40C) | -0.4759 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.q2 | 1.3491 **>1.32** (ffe1_bcs/bcs/1.320V/125C) | 1.0539 (ffe1_wcs/wcs/1.320V/-40C) | -0.4790 (ffe0_bcs/bcs/1.080V/125C) |
| pre_main.qt | 0.5196 (ffe0_bcs/bcs/1.320V/125C) | 0.4223 (ffe0_bcs/bcs/1.320V/27C) | -0.7785 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.q1 | 1.3283 **>1.32** (ffe0_wcs/wcs/1.320V/27C) | 1.0518 (ffe0_wcs/wcs/1.320V/-40C) | -0.4715 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.q2 | 1.3282 **>1.32** (ffe0_wcs/wcs/1.320V/27C) | 1.0515 (ffe0_wcs/wcs/1.320V/-40C) | -0.4759 (ffe0_bcs/bcs/1.080V/125C) |
| pre_post.qt | 0.5196 (ffe1_bcs/bcs/1.320V/125C) | 0.4223 (ffe0_bcs/bcs/1.320V/27C) | -0.7762 (ffe0_bcs/bcs/1.080V/125C) |
| driver_ffe.qm1 | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.9334 (ffe0_typ/typ/1.320V/-40C) | -0.3797 (ffe1_bcs/bcs/1.320V/125C) |
| driver_ffe.qm2 | 1.2566 (ffe0_wcs/wcs/1.320V/-40C) | 0.9327 (ffe0_wcs/wcs/1.320V/-40C) | -0.3808 (ffe1_bcs/bcs/1.320V/125C) |
| driver_ffe.qtm | 0.5175 (ffe0_bcs/bcs/1.320V/125C) | 0.4242 (ffe0_wcs/wcs/1.320V/-40C) | -0.7762 (ffe0_bcs/bcs/1.080V/125C) |
| driver_ffe.qp0a | 1.2566 (ffe0_wcs/wcs/1.320V/-40C) | 0.8906 (ffe1_bcs/bcs/1.320V/-40C) | 0.2161 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp0b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.8933 (ffe1_bcs/bcs/1.320V/-40C) | 0.1966 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp0 | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 0.0000 (ffe0_wcs/wcs/1.080V/125C) |
| driver_ffe.qp1a | 1.2566 (ffe0_wcs/wcs/1.320V/-40C) | 0.8906 (ffe1_bcs/bcs/1.320V/-40C) | 0.2161 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp1b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.8933 (ffe1_bcs/bcs/1.320V/-40C) | 0.1966 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp1 | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 0.0000 (ffe0_wcs/wcs/1.080V/125C) |
| driver_ffe.qp2a | 1.2566 (ffe0_wcs/wcs/1.320V/-40C) | 0.8906 (ffe1_bcs/bcs/1.320V/-40C) | 0.2161 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qp2b | 1.2961 (ffe0_bcs/bcs/1.320V/-40C) | 0.8933 (ffe1_bcs/bcs/1.320V/-40C) | 0.1966 (ffe0_bcs/bcs/1.320V/125C) |
| driver_ffe.qtp2 | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 1.1248 (ffe0_bcs/bcs/1.320V/125C) | 0.0000 (ffe0_wcs/wcs/1.080V/125C) |
| mux2to1_cml.qa1 | 1.3247 **>1.32** (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.8876 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | -0.4430 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qa2 | 1.3247 **>1.32** (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.9757 (tx_mos_mux2to1_cml/fs_typ/1.320V/-40C) | -0.1430 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qb1 | 1.3247 **>1.32** (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.9759 (tx_mos_mux2to1_cml/fs_typ/1.320V/-40C) | -0.1434 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| mux2to1_cml.qb2 | 1.3247 **>1.32** (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | 0.8878 (tx_mos_mux2to1_cml/ss_wcs/1.320V/-40C) | -0.4434 (tx_mos_mux2to1_cml/ff_bcs/1.320V/125C) |
| bias.qref@ffe_en | 1.0574 (tx_mos_ffe_en/ss_wcs/1.320V/-40C) | 0.9716 (tx_mos_ffe_en/ss_wcs/1.320V/-40C) | -0.7096 (tx_mos_ffe_en/fs_typ/1.080V/125C) |

- cells over an R3 limit in these grids: **8** (the mux collector findings at the 1.32 V supply are the known open ones, kept from `records/20261110-224611-4092fc2-mos/`; see the failing-corners list above).

## Grids and caveats

- tx_sizing (HBT set): hbt typ/bcs/wcs ganged with cap + res and the matching resistor sheet scale, x 1.08/1.2/1.32 V x -40/27/125 C = 27 corners per deck, x 6 decks (FFE off / all three post slices on). tx_mos (mux, ffe_en): 5 MOS process pairings x 3 supplies x 3 temperatures = 45 corners. Both include the +10 % supply (1.32 V). Mismatch/Monte Carlo is not run.
- The mux numbers cite the bench's assumed clock swing: 0.4 V per side (0.8 V differential peak-to-peak), an assumption, not a spec value (#98 is the open spec question). If #98 changes the swing, the mux rows are re-recorded after it lands, not before.
- The HBT decks' `rsil` is the behavioural stand-in with the corner sheet scale (see sim/tx/README.md); the mux and ffe_en decks use the real `r3_cmc` resistors via `osdi_preload`.
- Collector (`vc_max_*`) is per node, so devices sharing a collector node (e.g. `driver_ffe.qm2` and `driver_ffe.qp0a` at `cop`) repeat that node's value; Vce and reverse Vbe are per device.
- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not a real upstream eye; the pad network per TX leg is the 4 ohm stand-in + extracted 70.66 fF pad-metal C + PDK ESD clamp diodes (issue #142).
