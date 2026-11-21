# TX core record, 2026-11-21 (source commit 4ff16d8)

Append-only. Re-run with `layout/analog/tx/scripts/tx-core-regen.sh` into a new
dated directory. New in this record: `tx_lvl_cml2cmos` composes from an
**explicit per-net route plan** (issue #199, first split of #127) — every net
of the subckt is drawn connected, on the same `gen-compose` path as RX's
`lvl_cml2cmos` (chosen over generator-drawn routes so both cells share one
plan vocabulary in `layout_common.compose_routed_cell`). The other five cells
(`bias`, `ffe_en`, `mux2to1_cml`, `predriver`, `driver_ffe`) are unchanged:
shelf-packed, port pins at the cell boundary, **no routing** (#26, #27).
**Routed and LVS-clean in this record: `tx_lvl_cml2cmos` only.**

## tx_lvl_cml2cmos route plan

Full narrative in `layout/README.md` § "Per-cell analog route plans"; the
machine-readable plan is `tx_lvl_cml2cmos/compose.request.json`.

| Item | Value |
|---|---|
| Devices | 8 `mos_array` blocks (nfet row A / pfet row B, 5 columns; nfet/pfet pads co-aligned per column) + 1 `rppd` `res_array` block above the vdd trunk + 1 substrate-tie + 1 well-tie strap |
| Planes | metal2: `vss, s, d1, o1, out`; metal3: `vdd, vbm` (`vbm` rides metal3 so its channel trunk crosses the d1/o1 row-spanning metal2 verticals) |
| Nets drawn | 7/7 multi-terminal nets routed (`plan.json`); `inp`, `inn` labelled single-terminal pins |
| Route length | vdd 106.2, vss 73.6, s 24.5, d1 27.3, o1 59.1, vbm 111.4, out 14.1 um |
| `rppd` body | 3rd netlist node (`vss`) has no `res_array` port; the curated deck ties the drawn rppd body to the substrate, which the vss strap names — LVS shows it matched (9/9 devices incl. the resistor) |
| LVS options | `combine_devices: true` — ng=2 fingers extract as two devices each and the drawn rppd as series segments; the fold makes the layout side 9 devices like the reference (first attempt without it: 14 vs 9, `mismatch`) |
| DRC | `tx_lvl_cml2cmos/drc.report.json`: `status: clean`, 0 violations |
| LVS | `tx_lvl_cml2cmos/lvs.report.json`: `status: match`, engine `klayout`, 9/9 devices, 9/9 nets; `power_connectivity.status: unchecked` (inapplicable, analog `subckt-call` reference) |
| Pins | anchored `INN, INP, OUT, VDD, VSS` = the subckt port set incl. both supplies |
| Reference | `design/tx/netlists/tx_lvl_cml2cmos.spice` (standalone; its definition agrees with `tx_top.spice` as of 4ff16d8) |
| Freshness | `scripts/check-analog-lvs-fresh.sh` → `klt lvs --check` exit 0 on this record |

### Seeded-leg rejections (the plan as written vs what got drawn)

- `out` leg `XMN3.U0_D→XMP3.U0_D`: rejected, `comes within 0.21um of
  already-routed net 'o1'`; the router re-planned the net, same connectivity,
  DRC clean.
- All rejections and the two pad-geometry constraints met on the way
  (trunk-lane/pad-edge slivers, pad-level rail fanout) are posted as generic
  data points on 2AMLogic/klayout-tools#1962:
  https://github.com/2AMLogic/klayout-tools/issues/1962#issuecomment-7054026274

### Negative control (scratch only, not evidence; reproduced 2026-11-21)

On scratch copies of this record's GDS, same LVS request, reference unchanged:

- remove one device instance (`tx_lvl_cml2cmos_XMP3`): `mismatch`
- erase every Metal3 shape (vdd + vbm unrouted): `mismatch`

## What is not routed here

`bias`, `ffe_en`, `mux2to1_cml`, `predriver`, `driver_ffe`, the top-level
interconnect and the core-to-pad seam stay with #127; partition-level LVS
stays with #128. No claim that T1 item 4 (analog) is met.
