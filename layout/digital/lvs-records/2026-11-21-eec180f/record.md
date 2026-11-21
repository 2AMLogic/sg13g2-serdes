# Digital partition LVS record, 2026-11-21 (source commit eec180f)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/lvs-regen.sh`). T1 item 4, Digital column (cited as `4.digital`).
Structural check only: no number here is a measurement.

**Why this record exists.** Issue #197's timing round re-ran
place-and-route with the implementation corner set to `slow_1p08V_125C`
(`layout/digital/place-and-route.request.json`, the only change), so the
routed GDS and post-route netlist are new
(`layout/digital/records/2026-11-21-eec180f/`). The 2026-11-14 LVS record
compares the 2026-11-14 route; this record compares the new one against the
as-built netlist of that same record. The 2026-11-14 record is untouched.

| Item | Value |
|---|---|
| Layout side | `layout/digital/records/2026-11-21-eec180f/serdes_digital_top.gds`, extracted with `klt extract --deck sg13g2 --abstract-cells 'sg13g2_*' --abstract-cell-lef sg13g2_stdcell.lef --def-net-names` into `serdes_digital_top.gate.spice` (sha256 `2995f15b…`, 31,905 abstracted instances, 0 devices; was 33,481 — the 1.08 V repair pass upsizes cells, so fewer, larger instances carry more nets: 6,057 extracted nets vs 5,234) |
| Reference | `layout/digital/records/2026-11-21-eec180f/serdes_digital_top_postroute.v` (sha256 `b8a10d07…`), `reference.form` `gate-level-verilog`, library `sg13g2_stdcell` |
| Request | `lvs.request.json` (template: `layout/digital/lvs.request.json`) |
| Engine | `klayout` 0.30.13 (the pinned klt 0.9.0 was tested against 0.30.12; klt warns `klayout_version_mismatch: true`, verdict unaffected) |
| Tool / PDK | `klayout-tools==0.9.0` (`layout/toolchain.json`), IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| `status` | `match` (`error_count` 0) |
| `power_connectivity.status` | `match`: 46 masters (was 33: the repair passes reach more cell types), 31,905 instances, `expected_nets` `VDD->VDD`, `VSS->VSS`, `unchecked_expected_pins` empty, 0 findings |
| HBT recognition | Not applicable: the digital partition has no HBTs (analog LVS is #128) |

## Warnings (all severity `warning`, listed with the claim)

- `topology.power_only_pruned`: layout-side circuits `SG13G2_FILL_1` and
  `SG13G2_FILL_2` (filler cells, power pins only) were removed before
  comparing.
- `topology.reference_port_alias_joined` (5): the post-route Verilog declares
  ports `pi_code[0]`..`pi_code[3]` and `spi_miso_oe` via plain
  `assign <port> = ...;` aliases; klt joined each onto its canonical net
  (`pi_code[0]2078`, `pi_code[1]2075`, `pi_code[2]2074`, `pi_code[3]2071`,
  `spi_miso_oe1855`) before comparing, matching a layout with a single
  physical net for these names, instead of reporting them unmatched. New
  relative to 2026-11-14: OpenROAD's post-route writer emits the aliases
  after the timing-repair rewiring.
- `topology.top_level_pins_anchored`: the 88 remaining top-level pin names
  declared on both sides were anchored by name (2026-11-14 anchored 93; the 5
  above are now joined instead, 88 + 5 = 93 declared).

`mismatch_count` is 7 and all seven entries are these warnings;
`error_count` is 0.

## Scope and limits

- The layout netlist lists 6,048 pins against the reference's 93: the
  extraction exposes every net that carries a DEF name as a pin. The 93 shared
  names are anchored or alias-joined; the extra layout pins are internal
  nets. Counts in the report (`nets.matched` 6,303 against 6,057 layout nets)
  are klt's own and are not reconciled here.
- Power connectivity is per-cell-instance pin-to-net correctness, not a
  geometric rail or grid check (`klt ring-check`, `klt power` and DRC cover
  that).
- `body_verification.status` is `unchecked`: the request supplies a
  pre-extracted `layout.netlist` and no `layout.deck`, so nothing establishes
  this layout's substrate/well-tap convention. This run verified nothing
  about device bodies either way.
- Timing is not closed at slow 1.08 V (see the place-and-route record beside
  the GDS this record extracts); that does not affect LVS.

## Negative and freshness checks (run 2026-11-21, scratch copies, not committed)

- Swapping the `.A` and `.B` net connections of one `sg13g2_nand2_1`
  instance (`\u_chk/_1116_`) in a scratch copy of this record's post-route
  netlist, then re-comparing against this record's committed extraction,
  gave `status: mismatch` (`mismatch_count` 8, `error_count` 1; first error
  category `topology`, "subcircuit instance could not be matched to a
  counterpart"), exit 3. The compare is live, not vacuous.
- `klt lvs --check lvs.report.json` run from this record's directory exits 0
  (`[OK]` on both `environment.layout_sha256` and
  `environment.reference_sha256`); appending one line to a scratch copy of
  `serdes_digital_top.gate.spice` and pointing a scratch copy of the report
  at it makes `--check` exit 3 (`[DRIFTED] environment.layout_sha256`). The
  freshness gate is live.
