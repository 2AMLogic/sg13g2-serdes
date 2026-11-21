# Digital partition ERC supply record, 2026-11-20 (source commit 9f98e1e)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/erc-regen.sh`). T1 item 11, Digital column (cited as `11.digital`,
together with the place-and-route and LVS records it builds on). Structural
check only: no number here is a measurement.

**Why this record exists.** Item 11 graded `unmet` / `no_evidence` on the
digital partition: #29 covers both partitions as one deliverable and is parked
on the analog chain (#127, #128), so the digital half — drawable since the
2026-11-14 routed GDS — had never been run. This record supplies the `klt erc`
supply half: a committed supply spec (`layout/erc/digital.erc.json`, copied
verbatim into this directory as `erc.spec.json`, the document `klt signoff`
re-reads), the report of the run against the newest routed GDS, and the
citation wiring in `manifests/sg13g2-serdes.json` (issue #198).

| Item | Value |
|---|---|
| Layout | `layout/digital/records/2026-11-14-d19ba10/serdes_digital_top.gds`, sha256 `1ad0ea6b…` (the newest place-and-route record; `check-erc-fresh.sh` fails drift when a newer one exists) |
| Spec | `erc.spec.json` (canonical: `layout/erc/digital.erc.json`, sha256 `d3698abc…`), `klt erc --validate-spec` `valid` |
| Run | `klt erc <gds> erc.spec.json --top serdes_digital_top --deck sg13g2 --findings-only --omit-antenna-tables` from this directory |
| Tool | `klayout-tools==0.9.0` pinned (`layout/toolchain.json`); deck `sg13g2` (hash in `provenance.deck`); klayout 0.30.13 |
| `erc_status` | `clean` — 0 `erc_findings` of any rule |
| Supplies | `VDD` 1 island (declared 1), `VSS` 1 island (declared 1); no `erc.unconnected_net`, no `erc.supply_short` |
| Ties | `erc.missing_tie` 0. Both declarations checked, none skipped (`erc_coverage.skipped` empty): `nwell_vdd` geometrically derived, `psub_vss` via `well_complement_of` (named in `erc_coverage.checked_by_well_assertion`) |
| Antenna | deliberately not graded: `--findings-only` (item 11 grades the supply rules; the P&R record separately reports OpenROAD antenna 0) |

## The tapless question from #29, answered by running the grader

The P&R response records `power.pdn: true`, `power.tapless: true`,
`power.tapcell_master: null` — the tiers doc's documented-tapless form for
`sg13g2_stdcell` (a null master without `tapless` would read
`no_tapcell_master`). `klt signoff` accepts it for item 11's P&R half; nothing
about the tapless form blocked the `met` verdict.

Tapless here means *no dedicated tap/endcap masters*, not *no taps*: every
standard-cell master in the stream carries its own ties in FEOL geometry. The
spec declares them as two checked `ties[]` entries rather than a disclosure:

- `nwell_vdd` — n-well tie. The well is drawn (`NWell` 31/0, one shape per
  cell, merging across abutting rows); the tap is `Cont ∩ Activ` minus `pSD`
  (n+ is the default doping inside the well, pSD marks the PMOS source/drain
  contacts in the same well), wired up to `Metal1`, reaching `VDD`.
- `psub_vss` — substrate tie. The p-type bulk has no drawn well layer anywhere
  in this stream (the PDK's `Substrate` 40/0 and `PWell` 46/0 are absent), so
  the substrate region is derived as the top-cell extent minus the merged
  `NWell` (`well_complement_of`, issue #3750); the tap is `Cont ∩ Activ ∩ pSD`
  (the p+ regions outside the wells), wired up to `Metal1`, reaching `VSS`.

Verified per master before the run (35/35 masters carry both tap kinds) and by
the run itself: zero `erc.missing_tie`, zero skipped work.

## Spec coverage disclosure (claimant-quoted per item 11)

- `erc_coverage.layers_in_stream_without_declaration` = `["63/0"]`, with
  `provenance.deck` = `sg13g2` (the list is deck-narrowed to the routing
  stack). 63/0 is the PDK's TEXT purpose: it carries exactly two text objects
  in this stream ("dant"/"dpant", the antenna-diode cell's pin names inside
  `sg13g2_antennanp`) and no conductor geometry; a text-bearing layer survives
  the deck narrowing by design (klt erc #4376). The non-deck-narrowed reading
  would additionally list the DEF pin/pin-text purposes (8/2, 30/2, 134/2,
  8/25, 30/25, 134/25 — pin shapes and net-name text, declared as label
  layers or not conductors) and `prBoundary` 189/4 and `Recog.diode` 99/31
  (annotation). No routing level is undeclared: the stackup spans Metal1
  through TopMetal2 and every routing via, covering every
  `power.straps[].layer` of the P&R report (Metal1, TopMetal1, TopMetal2).
- `erc.supply_short` is reported `inapplicable` (`substrate_continuity_not_
  modelled`): with two `kind: "supply"` nets, rails that are one conductor
  through a shared substrate are not observable through the declared stack.
  Disclosed by the tool, `erc_status` unchanged; the independent cross-check
  is the cited LVS report's `power_connectivity: match`.
- `nets[].roles` is not declared: every metal level is shared with signal
  routing, so no supply owns a role outright; `power_delivery.supply_
  unlabelled_islands` is therefore `{}` (not measured), per the tiers doc.

## Freshness and negative control

- Freshness: `scripts/check-erc-fresh.sh` (cheap mode re-hashes layout, spec
  and deck via `klt erc --check`; `--rerun` re-runs and diffs verdicts). It
  exits drift (3) when a newer place-and-route record exists; issue #134's
  RTL change re-runs P&R through `scripts/erc-regen.sh`.
- Negative control (run 2026-11-20, scratch copies, not committed): the PDN
  is a redundant mesh — followpin rails chain across flipped rows and both
  strap layers stitch them — so removing one strap stripe alone does not
  fragment anything. Two live checks instead:
  - Severing the grid (a flattened scratch copy with every conductor layer
    deleted from one full-height vertical band, x 198.9–243.1 um, which
    removes the straps and rails crossing it) fragments both supplies:
    `erc.unconnected_net` fires on `VDD` and on `VSS`, each at 2 labelled
    islands (`nets[].matched_islands` 2), `erc_status` `violations`, exit 3.
    The 2,939 `erc.floating_gate` findings in the same run are the severed
    signal nets, not supply findings.
  - Deleting the 879 n+ tap contacts (Cont on Activ without pSD, 22.5 um2)
    inside one merged NWell band (y 13.08–17.16 um, one of 56) of a
    flattened scratch copy fires exactly one `erc.missing_tie` naming
    `nwell_vdd` at that band's bbox, exit 3, with both supplies still one
    island — the tie check grades drawn tap geometry, not the grid.

