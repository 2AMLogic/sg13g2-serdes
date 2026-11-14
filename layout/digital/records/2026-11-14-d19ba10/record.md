# Digital partition P&R record, 2026-11-14 (source commit d19ba10)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/pnr-regen.sh`).

**Why this record exists.** The previous record
(`layout/digital/records/2026-11-10-f6fe587/`) was built from the synthesized
netlist with sha256 `d6591244…`. The committed netlist moved to `08b90805…`
in `506b37e` (the `klayout-tools` 0.9.0 pin bump), so that record — and the DRC
report and LVS record derived from it — described a layout of a superseded
netlist. `scripts/check-pnr-fresh.sh` exited 3 (`[DRIFTED]
provenance.input.content_hash`) on `d19ba10` before this run. This record
re-runs the same committed request on the current netlist; the 2026-11-10
record is untouched (issue #151).

| Item | Value |
|---|---|
| Request | `layout/digital/place-and-route.request.json` (unchanged) |
| Input netlist | `rtl/synth/serdes_digital_top_synth.v`, sha256 `08b90805…` (full hash: `provenance.input.content_hash` in `report.json`, equal to `netlist_sha256` in `rtl/synth/serdes_digital_top.synth.json`) |
| Liberty / LEF | `sg13g2_stdcell`, corner `typ_1p20V_25C`, PDK IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| Tool | `klayout-tools==0.9.0` (pinned, `layout/toolchain.json`), OpenROAD 26Q3-1510-g6cb3f2b704, KLayout 0.30.13 |
| Furthest `target_stage` | `route` (all four stages ran: floorplan, place, cts, route) |
| Die / core area | 195404 / 177029 um2, utilization 44.1 % |
| Route DRC (OpenROAD) | 0 violations; antenna 0; global-route total overflow 0; detailed route converged in 5 iterations (1923 → 933 → 822 → 33 → 0) |
| Routing completeness | 4805 signal nets, 0 unrouted |
| Files | `serdes_digital_top.gds` (routed GDS), `.def`, `serdes_digital_top_postroute.v` (as-built netlist; the LVS reference), `report.json` (verbatim `klt place-and-route --format json`, `portable_paths`), `drc.json` (`klt drc --deck sg13g2` on this GDS) |

## Power delivery

Explicit PDN straps in the request: Metal1 followpins rail, TopMetal1 and
TopMetal2 stripes (same values as klt's `sg13g2` preset, spelled out so the
request is self-contained). `sg13g2_stdcell` has no tap/endcap cells in the
open PDK, so none are placed. Power-delivery ERC is #29.

## Timing: NOT a closure claim

The flow reached `route`, but setup timing at the 1.6 ns clock target is **not
met** in the typical and slow corners. All six corners from post-route STA
(`report.json` `corners[]`, `timing_status: constrained` in every corner):

| corner | setup slack (ns) | hold slack (ns) |
|---|---|---|
| fast_1p32V_m40C | +0.52135 | +0.13607 |
| fast_1p65V_m40C | +0.85175 | +0.10047 |
| slow_1p08V_125C | **-1.00712** | +0.32220 |
| slow_1p35V_125C | **-0.02580** | +0.21008 |
| typ_1p20V_25C | **-0.03180** | +0.20323 |
| typ_1p50V_25C | +0.53083 | +0.14042 |

Summary fields: `worst_setup_slack_ns` -1.00712, `worst_hold_slack_ns`
+0.10047, `setup_violation_count` 1, `hold_violation_count` 0. Hold slack is
positive in all six corners. Transition and capacitance violation counts are 0
in every corner, both against the request and against the library limits.

This record is evidence of layout provenance for T1 item 2 only. It is **not** a
timing signoff and **not** a clock-frequency claim; the 1.6 ns target is a
synthesis constraint from the (still PROPOSED) spec. Closure work (period,
floorplan, CTS tuning) is out of scope for #151, as it was for #25.

Against the 2026-11-10 record the setup picture is substantially the same —
worst setup -1.00712 ns vs -0.99182 ns, same `setup_violation_count` of 1,
hold still met everywhere. The small differences are the new netlist plus
router nondeterminism at a fixed `seed: 1`; neither direction is a closure or a
regression claim.

## DRC

`klt drc --deck sg13g2` on this record's GDS: `status: clean`,
`violation_count: 0`, report in `drc.json` beside the GDS, with
`provenance.input.content_hash` equal to the GDS sha256
(`1ad0ea6b707cfa50cce60525ceb99c4cd77b347ace6b6c551d8e88b074400ae0`). Deck
content hash `sha256:1c95db40…`, unchanged from the previous record's report,
and the coverage lists (`layers_in_stream_without_rules`, `rules_skipped`,
`deck_scope`) are byte-identical to it — so the coverage gaps quoted in
`layout/README.md` carry over unchanged. `klayout_version_mismatch: true` as in
every committed report here (KLayout 0.30.13 vs the engine's tested 0.30.12);
it changes no verdict. T1 item 3, Digital.

## Reproducibility

`scripts/check-pnr-fresh.sh` runs `klt place-and-route --check` (cheap mode:
re-hash the netlist and liberty against `report.json` provenance). The GDS is
checked for existence and by the item-2 attestation
(`manifests/evidence/item2.json`, hash of this GDS); `--rerun` diffs
verdict-bearing report fields, not GDS bytes. The run was a single local
OpenROAD process (`--backend local`), never fanned out as a grid.
