# Digital partition P&R record, 2026-11-10 (source commit f6fe587)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/pnr-regen.sh`).

| Item | Value |
|---|---|
| Request | `layout/digital/place-and-route.request.json` |
| Input netlist | `rtl/synth/serdes_digital_top_synth.v`, sha256 `d6591244…` (full hash: `provenance.input.content_hash` in `report.json`, equal to `netlist_sha256` in `rtl/synth/serdes_digital_top.synth.json`) |
| Liberty / LEF | `sg13g2_stdcell`, corner `typ_1p20V_25C`, PDK IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| Tool | `klayout-tools==0.8.0` (pinned, `layout/toolchain.json`), OpenROAD 26Q3-1510-g6cb3f2b704, KLayout 0.30.13 |
| Furthest `target_stage` | `route` (all four stages ran: floorplan, place, cts, route) |
| Die / core area | 195404 / 177029 um2, utilization 44.1 % |
| Route DRC (OpenROAD) | 0 violations; antenna 0; global-route overflow 0 |
| Files | `serdes_digital_top.gds` (routed GDS), `.def`, `serdes_digital_top_postroute.v` (as-built netlist; use this, not the synth netlist, as the LVS reference for #27), `report.json` (verbatim `klt place-and-route --format json`, `portable_paths`) |

## Power delivery

Explicit PDN straps in the request: Metal1 followpins rail, TopMetal1 and
TopMetal2 stripes (same values as klt's `sg13g2` preset, spelled out so the
request is self-contained). `sg13g2_stdcell` has no tap/endcap cells in the
open PDK, so none are placed. Power-delivery ERC is #29.

## Timing: NOT a closure claim

The flow reached `route`, but setup timing at the 1.6 ns clock target is **not
met** in the slower corners (post-route STA in `report.json` `corners[]`):

| corner | setup slack (ns) |
|---|---|
| typ_1p20V_25C | -0.033 |
| slow_1p35V_125C | -0.048 |
| slow_1p08V_125C | -0.992 |
| fast / typ_1p50V | positive |

Hold is met in every corner. This record is evidence of layout provenance for
T1 item 2 only. It is not a timing signoff and not a clock-frequency claim;
the 1.6 ns target is a synthesis constraint from the (still PROPOSED) spec.
Closure work (period, floorplan, CTS tuning) is out of scope for issue #25.

## Reproducibility

`scripts/check-pnr-fresh.sh` runs `klt place-and-route --check` (cheap mode:
re-hash the netlist and liberty against `report.json` provenance). The GDS is
checked for existence and by the item-2 attestation
(`manifests/evidence/item2.json`, hash of this GDS); `--rerun` diffs
verdict-bearing report fields, not GDS bytes.
