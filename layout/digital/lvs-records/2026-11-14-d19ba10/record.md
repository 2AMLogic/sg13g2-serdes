# Digital partition LVS record, 2026-11-14 (source commit d19ba10)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/lvs-regen.sh`). T1 item 4, Digital column (cited as `4.digital`).
Structural check only: no number here is a measurement.

**Why this record exists.** The 2026-11-12 record compared against
`layout/digital/records/2026-11-10-f6fe587/serdes_digital_top_postroute.v`,
whose place-and-route record was built from a superseded synthesized netlist
(`d6591244…`; the committed netlist is `08b90805…`). That record's own verdict
was `match` — it was the *reference* that had gone stale. This record compares
against the 2026-11-14 place-and-route record, which is built from the current
netlist. The 2026-11-12 record is untouched (issue #151).

| Item | Value |
|---|---|
| Layout side | `layout/digital/records/2026-11-14-d19ba10/serdes_digital_top.gds`, extracted with `klt extract --deck sg13g2 --abstract-cells 'sg13g2_*' --abstract-cell-lef sg13g2_stdcell.lef --def-net-names` into `serdes_digital_top.gate.spice` (sha256 `aba8e150…`, 33,481 abstracted instances, 0 devices) |
| Reference | `layout/digital/records/2026-11-14-d19ba10/serdes_digital_top_postroute.v` (sha256 `5030bb0b…`), `reference.form` `gate-level-verilog`, library `sg13g2_stdcell` |
| Request | `lvs.request.json` (template: `layout/digital/lvs.request.json`) |
| Engine | `klayout` 0.30.13 (the pinned klt 0.9.0 was tested against 0.30.12; klt warns `klayout_version_mismatch: true`, verdict unaffected) |
| Tool / PDK | `klayout-tools==0.9.0` (`layout/toolchain.json`), IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| `status` | `match` (`error_count` 0) |
| `power_connectivity.status` | `match`: 33 masters, 33,481 instances, `expected_nets` `VDD->VDD`, `VSS->VSS`, `unchecked_expected_pins` empty, 0 findings |
| HBT recognition | Not applicable: the digital partition has no HBTs (analog LVS is #128) |

## Warnings (both severity `warning`, listed with the claim)

- `topology.power_only_pruned`: layout-side circuits `SG13G2_FILL_1` and `SG13G2_FILL_2` (filler cells, power pins only) were removed before comparing.
- `topology.top_level_pins_anchored`: the 93 top-level pin names declared on both sides were anchored by name.

`mismatch_count` is 2 and both entries are these warnings; `error_count` is 0.
Same two categories, same counts, as the 2026-11-12 record.

## Scope and limits

- The layout netlist lists 5,225 pins against the reference's 93: the extraction exposes every net that carries a DEF name as a pin. The 93 shared names are anchored; the extra layout pins are internal nets. Counts in the report (`nets.matched` 5,410 against 5,234 layout nets) are klt's own and are not reconciled here.
- Power connectivity is per-cell-instance pin-to-net correctness, not a geometric rail or grid check (`klt ring-check`, `klt power` and DRC cover that).
- `body_verification.status` is `unchecked`: the request supplies a pre-extracted `layout.netlist` and no `layout.deck`, so nothing establishes this layout's substrate/well-tap convention. This run verified nothing about device bodies either way.
- Timing is not closed (see the place-and-route record); that does not affect LVS.

## Negative and freshness checks (run 2026-11-14, scratch copies, not committed)

- Swapping the `.A` and `.B` net connections of one `sg13g2_nand2_1` instance (`\u_chk/_1108_`) in a scratch copy of this record's post-route netlist, then re-comparing against this record's committed extraction, gave `status: mismatch` (`mismatch_count` 16, `error_count` 14; first error category `topology`, "subcircuit instance could not be matched to a counterpart"), exit 3. The compare is live, not vacuous.
- `klt lvs --check lvs.report.json` on an unmodified scratch copy exits 0 (`[OK]` on both `environment.layout_sha256` and `environment.reference_sha256`); appending one line to the scratch copy's `serdes_digital_top.gate.spice` makes it exit 3 (`[DRIFTED] environment.layout_sha256`). The freshness gate is live.
