# Digital partition LVS record, 2026-11-12 (source commit 7fd70b1)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/lvs-regen.sh`). T1 item 4, Digital column (cited as `4.digital`).
Structural check only: no number here is a measurement.

| Item | Value |
|---|---|
| Layout side | `layout/digital/records/2026-11-10-f6fe587/serdes_digital_top.gds`, extracted with `klt extract --deck sg13g2 --abstract-cells 'sg13g2_*' --abstract-cell-lef sg13g2_stdcell.lef --def-net-names` into `serdes_digital_top.gate.spice` (sha256 `b42acd70…`, 33,482 abstracted instances, 0 devices) |
| Reference | `layout/digital/records/2026-11-10-f6fe587/serdes_digital_top_postroute.v`, `reference.form` `gate-level-verilog`, library `sg13g2_stdcell` |
| Request | `lvs.request.json` (template: `layout/digital/lvs.request.json`) |
| Engine | `klayout` 0.30.13 (the pinned klt 0.9.0 was tested against 0.30.12; klt warns, verdict unaffected) |
| Tool / PDK | `klayout-tools==0.9.0` (`layout/toolchain.json`), IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| `status` | `match` |
| `power_connectivity.status` | `match`: 33 masters, 33,482 instances, `expected_nets` `VDD->VDD`, `VSS->VSS`, `unchecked_expected_pins` empty, 0 findings |
| HBT recognition | Not applicable: the digital partition has no HBTs (analog LVS is #128) |

## Warnings (both severity `warning`, listed with the claim)

- `topology.power_only_pruned`: layout-side circuits `SG13G2_FILL_1` and `SG13G2_FILL_2` (filler cells, power pins only) were removed before comparing.
- `topology.top_level_pins_anchored`: the 93 top-level pin names declared on both sides were anchored by name.

## Scope and limits

- The layout netlist lists 5,214 pins against the reference's 93: the extraction exposes every net that carries a DEF name as a pin. The 93 shared names are anchored; the extra layout pins are internal nets. Counts in the report (`nets.matched` 5,399 against 5,223 layout nets) are klt's own and are not reconciled here.
- Power connectivity is per-cell-instance pin-to-net correctness, not a geometric rail or grid check (`klt ring-check`, `klt power` and DRC cover that).
- Timing is not closed (see the place-and-route record); that does not affect LVS.

## Negative and freshness checks (run 2026-11-12, scratch copies, not committed)

- Swapping the `A` and `B` connections of one `sg13g2_nand2_1` instance in a scratch copy of the post-route netlist gave `status: mismatch` (3 mismatches; first: `subcircuit instance could not be matched to a counterpart`), so the compare is live.
- `klt lvs --check` against a layout netlist with one line appended exits 3 (drift).
