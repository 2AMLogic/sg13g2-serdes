# RX core record, 2026-11-23 (source commit 9f3e17c)

Append-only. Re-run with `layout/analog/rx/regen.sh` into a new dated directory.
Supersedes `2026-11-21-4ff16d8` for `lvl_cml2cmos` (review of PR #212, issue
#199): that record's `tl` leg `XMn1.U0_S→XMnt.U0_D` was rejected
(`crosses already-routed net 'vdd'`) and the router substituted a connection of
its own, so the plan as written was not what was drawn. Here **every planned
leg is drawn as planned**: 0 unrouted legs in
`lvl_cml2cmos/compose.response.json`, and `layout_common.assert_plan_followed`
fails the build on any rejected or router-substituted leg of a net that supplies
legs, even when the net reports `routed`. The other three cells (`ctle`,
`latch_cml`, `clk_buf_quad`) are unchanged from the earlier record.

## What changed in the plan

The `tl` trunk now runs below row A (metal3, y = -1.2 um, west lane to the
column-3 east lane) instead of through the channel. The vdd feed from `XMnt.G`
to the well tie rises through the channel on metal3, so a channel `tl` trunk
whose last vertical drops to `XMnt.D` had to cross it on the same layer. Below
row A nothing on metal3 is in the way (vss rides metal2).

| Item | Value |
|---|---|
| Planes | metal2: `vss, x, y, z, op`; metal3: `vdd, tl` |
| Route length | vdd 137.9, vss 59.8, tl 40.7, op 15.0, x 37.9, y 61.0, z 44.1 um |
| Body ties / well | 1 substrate tie, 1 well tie, 1 merged NWell polygon: `compose_routed_cell` raises before writing the GDS on any other count |
| DRC | `lvl_cml2cmos/drc.report.json`: `status: clean`; `.provenance.input.content_hash` is the sha256 of `lvl_cml2cmos.gds` in this record |
| LVS | `lvl_cml2cmos/lvs.report.json`: `status: match`, engine `klayout`, devices 9/9, nets 9/9; `environment.layout_sha256` is that same GDS, `reference_sha256` is `design/rx/netlists/lvl_cml2cmos.spice`; `power_connectivity.status: unchecked` (inapplicable for a `subckt-call` analog reference) |
| Evidence gates | `scripts/check-ci.sh fresh` axes 7-8 and `scripts/check-analog-lvs-fresh.sh` select this (newest) record first and bind both reports to its GDS and the reference |

Engine note: the reports record KLayout 0.30.14 against the 0.30.12 the pinned
klt 0.9.0 was tested with (`klayout_version_mismatch: true`); the verdicts are
unaffected, counts and deck hashes may differ from a 0.30.12 run.

## What is not routed here

`ctle`, `latch_cml`, `clk_buf_quad` (HBT cells), the top-level interconnect and
the core-to-pad seam stay with #127; partition-level LVS stays with #128. No
claim that T1 item 4 (analog) is met.
