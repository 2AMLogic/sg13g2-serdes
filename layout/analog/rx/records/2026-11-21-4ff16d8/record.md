# RX core record, 2026-11-21 (source commit 4ff16d8)

Append-only. Re-run with `layout/analog/rx/regen.sh` into a new dated directory.
New in this record: `lvl_cml2cmos` composes from an **explicit per-net route
plan** (issue #199, first split of #127) — every net of the subckt is drawn
connected. The other three cells (`ctle`, `latch_cml`, `clk_buf_quad`) are
unchanged: placed and labelled, intra-cell routing partial, nets with an HBT
terminal left unrouted (#26, #27). **Routed and LVS-clean in this record:
`lvl_cml2cmos` only.**

## lvl_cml2cmos route plan

Full narrative in `layout/README.md` § "Per-cell analog route plans"; the
machine-readable plan is `lvl_cml2cmos/compose.request.json`
(`connectivity[]` with per-net `layer_role`, multi-pin nets as named `legs[]`
with `waypoints_um`).

| Item | Value |
|---|---|
| Devices | 9 `mos_array` blocks (nfet row A / pfet row B, 5 columns) + 1 substrate-tie + 1 well-tie strap |
| Planes | metal2: `vss, x, y, z, op`; metal3: `vdd, tl` (crossing nets on separate planes) |
| Nets drawn | 7/7 multi-terminal nets routed (`summary.json`); `ip`, `in` labelled single-terminal pins |
| Route length | vdd 137.9, vss 59.8, tl 26.1, op 15.0, x 37.9, y 61.0, z 44.1 um |
| Bulk terminals | no `mos_array` port at klt 0.9.0; realised by body-tie straps (pSD/nSD-marked Activ the curated deck derives ties from), asserted in `layout_common.assert_ties` |
| DRC | `lvl_cml2cmos/drc.report.json`: `status: clean`, 0 violations (deck sg13g2, curated engine) |
| LVS | `lvl_cml2cmos/lvs.report.json`: `status: match`, engine `klayout`, 9/9 devices, 9/9 nets; `power_connectivity.status: unchecked` (inapplicable for a `subckt-call` analog reference — the reference carries its own power pins, checked by the ordinary compare) |
| Pins | anchored `IN, IP, OP, VDD, VSS` = the subckt port set incl. both supplies (`topology.top_level_pins_anchored.details.pins`) |
| Reference | `design/rx/netlists/lvl_cml2cmos.spice` (standalone; its definition agrees with `rx_top.spice` as of 4ff16d8) |
| Freshness | `scripts/check-analog-lvs-fresh.sh` → `klt lvs --check` exit 0 on this record |

### Seeded-leg rejections (the plan as written vs what got drawn)

- `tl` leg `XMn1.U0_S→XMnt.U0_D`: rejected, `crosses already-routed net 'vdd'`;
  the router re-planned the net (`XMn2↔XMn1↔XMnt` tree), same connectivity.
- Both rejections across the two cells of this split are posted as generic
  data points on 2AMLogic/klayout-tools#1962 (comment 2026-11-21):
  https://github.com/2AMLogic/klayout-tools/issues/1962#issuecomment-7054026274

### Negative control (scratch only, not evidence; reproduced 2026-11-21)

On scratch copies of this record's GDS, same LVS request, reference unchanged:

- remove one device instance (`lvl_cml2cmos_XMpi2`): `mismatch`
- erase every Metal3 shape (vdd + tl unrouted): `mismatch`

## What is not routed here

`ctle`, `latch_cml`, `clk_buf_quad` (HBT cells), the top-level interconnect
and the core-to-pad seam stay with #127; partition-level LVS stays with #128.
No claim that T1 item 4 (analog) is met.
