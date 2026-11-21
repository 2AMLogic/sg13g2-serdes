# Digital partition P&R record, 2026-11-21 (source commit eec180f)

Append-only. Do not edit; a new run goes in a new dated directory
(`scripts/pnr-regen.sh`).

**Why this record exists.** Issue #197, one bounded post-route timing-closure
round on the 1.6 ns word clock. The previous record
(`layout/digital/records/2026-11-14-d19ba10/`) implemented against the nominal
`typ_1p20V_25C` deck, so OpenROAD's `repair_timing` passes never saw the corner
the clock actually misses: post-route setup slack was -0.03180 ns at typ and
-0.02580 ns at slow 1.35 V (that record's `report.json` `corners[]`). This
record changes exactly one request field: `pdk.corner` is now
`slow_1p08V_125C`, so the `place`/`cts`/`route` repair passes size against the
slow deck (the pinned klt 0.9.0 `pdk.corner` semantics: the single liberty the
repair passes see). The netlist, floorplan, PDN, IO layers, clock target and
seed are unchanged. The 2026-11-14 record is untouched.

| Item | Value |
|---|---|
| Request | `layout/digital/place-and-route.request.json` (`pdk.corner` `typ_1p20V_25C` -> `slow_1p08V_125C`, the only change) |
| Input netlist | `rtl/synth/serdes_digital_top_synth.v`, sha256 `08b90805…` (unchanged; equals `netlist_sha256` in `rtl/synth/serdes_digital_top.synth.json` and `provenance.input.content_hash` in `report.json`) |
| Liberty / LEF | `sg13g2_stdcell`, implementation corner `slow_1p08V_125C`, interconnect corner `nom`, PDK IHP-Open-PDK v0.3.0 (`sim/pdk.json`) |
| Tool | `klayout-tools==0.9.0` (pinned, `layout/toolchain.json`), OpenROAD 26Q3-1510-g6cb3f2b704, KLayout 0.30.13 |
| Furthest `target_stage` | `route` (floorplan, place, cts, route) |
| Die / core area | 195404 / 177029 um2 (die unchanged from the request's `utilization_pct: 40`); utilization 49.3 % (was 44.1 %: repair at 1.08 V upsized cells), wirelength 156649 um (was 147530 um), 5628 signal nets (was 4805: repair buffers/diodes) |
| Route DRC (OpenROAD) | 0 violations; antenna 0; global-route total overflow 0; detailed route converged in 7 iterations (2068 -> 979 -> 930 -> 20 -> 2 -> 2 -> 0) |
| Routing completeness | 5628 signal nets, 0 unrouted |
| Files | `serdes_digital_top.gds`, `.def`, `serdes_digital_top_postroute.v` (as-built netlist; LVS reference), `report.json` (verbatim `klt place-and-route --format json`, `portable_paths`), `drc.json` (`klt drc --deck sg13g2` on this GDS), `sta-corners.json` + `sta-corners.request.json` (standalone `klt sta` per-corner path report, below) |

## Timing: typ and slow 1.35 V now close; slow 1.08 V still misses

All six corners from post-route STA (`report.json` `corners[]`,
`timing_status: constrained` in every corner), against the 2026-11-14 baseline
(same netlist, same seed, implementation corner `typ_1p20V_25C`):

| corner | setup 2026-11-14 | setup this record | hold this record | setup TNS this record |
|---|---|---|---|---|
| fast_1p32V_m40C | +0.52135 | +0.63951 | +0.13524 | 0 |
| fast_1p65V_m40C | +0.85175 | +0.92507 | +0.09988 | 0 |
| slow_1p08V_125C | **-1.00712** | **-0.73221** | +0.31988 | -108.556 |
| slow_1p35V_125C | **-0.02580** | **+0.13260** | +0.20860 | 0 |
| typ_1p20V_25C | **-0.03180** | **+0.13280** | +0.20191 | 0 |
| typ_1p50V_25C | +0.53083 | +0.62616 | +0.13953 | 0 |

Hold slack is >= 0 in all six corners (worst +0.09988 ns, fast_1p65V_m40C —
above zero in every corner, as in the baseline). Transition and capacitance
violation counts are 0 in every corner, against the request and against the
library limits. This closes the typ_1p20V_25C and slow_1p35V_125C setup misses
(the partial-closure branch of issue #197's acceptance criteria) and improves
the slow_1p08V_125C miss from -1.00712 ns / TNS -229.673 ns to -0.73221 ns /
TNS -108.556 ns, without closing it. It is still **not** a full timing-closure
claim and not a clock-frequency claim; the 1.6 ns target is a synthesis
constraint from the (still PROPOSED) spec.

### Trial matrix (issue #197 step 2/3; all trials scratch, outside the records tree)

Every trial is one full local P&R run of the pinned flow, same netlist, seed 1,
clock 1.6 ns; values are that route's own six-corner post-route sweep
(`timing_status: constrained` in every row):

| trial | implementation corner | extra settings | typ setup | slow 1.35 V setup | slow 1.08 V setup / TNS | worst hold |
|---|---|---|---|---|---|---|
| baseline (2026-11-14 record) | typ_1p20V_25C | — | -0.03180 | -0.02580 | -1.00712 / -229.673 | +0.10047 |
| T1 | slow_1p35V_125C | — | +0.01463 | +0.02089 | -0.93288 / -224.504 | +0.09812 |
| **T2 (= this record)** | **slow_1p08V_125C** | **—** | **+0.13280** | **+0.13260** | **-0.73221 / -108.556** | **+0.09988** |
| T3 | slow_1p08V_125C | `route_critical_nets_percentage: 30`, `placement_density: 0.5` | +0.08115 | +0.08285 | -0.80868 / -126.405 | +0.09843 |

T2 dominates: repairing against the slow 1.35 V deck (T1) closes the two
near-zero corners but with < 25 ps margin, while repairing against 1.08 V (T2)
buys ~130 ps at both and halves the slow-corner TNS. T3's timing-driven
routing flag plus lower placement density made every corner worse (wirelength
163855 um vs 156649 um), so they are not adopted. The floorplan
(`utilization_pct: 40`), PDN and seed are unchanged in the committed request.

### Per-corner path report and what limits slow 1.08 V (issue #197 steps 1 and 6)

`sta-corners.json` is a standalone `klt sta` (pinned 0.9.0) multi-corner run on
this record's routed DEF (`sta-corners.request.json`; `constraints`:
`clk` at 1.6 ns; **ideal** clock, matching the in-flow sweep's clock model;
parasitics from the loaded LEF/DEF only — no SPEF, so no routed wire RC; the
in-flow sweep cited above uses ideal clocks and global-routing RC estimates).
Per corner (worst setup path identity, violating-endpoint count):

| corner | worst setup path | standalone WNS | standalone TNS | violating endpoints |
|---|---|---|---|---|
| slow_1p08V_125C | `u_pd/_699_/Q -> u_pd/_721_/D` (setup) | -0.47660 | -39.1535 | 217 |
| slow_1p35V_125C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.28679 | 0 | 0 |
| typ_1p20V_25C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.28402 | 0 | 0 |
| typ_1p50V_25C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.73045 | 0 | 0 |
| fast_1p32V_m40C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.73587 | 0 | 0 |
| fast_1p65V_m40C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.99410 | 0 | 0 |

On the 2026-11-14 baseline DEF the same diagnostic reports worst path
`u_flt/_1028_/Q -> u_flt/_1037_/D` at all six corners (316 violating endpoints
at slow 1.08 V, WNS -0.65431): the slow-driven repair fixed the CDR filter
path that used to be worst, and the residual critical structure is in the CDR
phase detector (`u_pd`, `rtl/serdes_cdr_pd.v`) — not in the filter #134 will
rewrite. `u_pd` had the third-best pre-layout margin (+0.19 ns typ,
`rtl/synth/sta/serdes_digital_top.paths.txt`), so the miss there is
cell-delay-at-1.08 V, not a wiring accident.

**What limits the slow 1.08 V corner** (issue #197 step 6 account):

- **Cell delay dominates, wires contribute ~0.26 ns of the 0.73 ns miss.**
  Standalone STA on this DEF (no routed wire RC) reports WNS -0.47660 ns at
  slow 1.08 V; the in-flow sweep (global-routing RC estimates) reports
  -0.73221 ns. The 0.25561 ns delta is the wire-parasitics share of the worst
  path; the remaining 0.47660 ns exists with no wire RC at all, i.e. logic
  depth times 1.08 V cell delay.
- **217 violating endpoints** (standalone count; 394 by the in-flow model,
  `report.json` `setup_violation_count`, the implementation corner's own
  count). All register-to-register inside the digital partition; hold met at
  every one of them.
- **Module split of the 217 endpoints is not measurable with the pinned klt
  0.9.0**: `klt sta` reports one worst path per corner and a total count;
  worst-N endpoint lists shipped upstream *after* 0.9.0
  (2AMLogic/klayout-tools#5424, `worst_paths_by_group`), and per-stage
  cell/wire increments likewise (2AMLogic/klayout-tools#5783, merged as
  2AMLogic/klayout-tools#6014). A klt pin bump would unlock both; neither is
  in scope for this round.
- **Why no RTL restructure this round**: the residual worst path is in
  `u_pd`, whose restructure is in scope per issue #197 — but with 217
  endpoints and -39.15 ns standalone TNS spread across the partition, one
  path's restructure cannot close the corner, and the #134 filter rewrite
  (still open) will change the netlist underneath any restructure landed now.
  The numbers above are the input to that decision.

## DRC

`klt drc --deck sg13g2` on this record's GDS: `status: clean`,
`violation_count: 0` (`drc.json`, with `provenance.input.content_hash` equal
to the GDS sha256
`2d781d749448a8b2607b2ca3fb576767b0fddd6a8f231715cd6306fc077c2182`). Deck
content hash `sha256:1c95db40…`, unchanged from the 2026-11-14 report, and the
coverage lists (`layers_in_stream_without_rules`, `rules_skipped`,
`deck_scope`) are byte-identical to it — the coverage gaps quoted in
`layout/README.md` carry over unchanged. `klayout_version_mismatch: true` as
in every committed report here (KLayout 0.30.13 vs the engine's tested
0.30.12); it changes no verdict. T1 item 3, Digital.

## Reproducibility

`scripts/check-pnr-fresh.sh` runs `klt place-and-route --check` (cheap mode:
re-hash the netlist and liberty against `report.json` provenance). The GDS is
checked for existence and by the item-2 attestation
(`manifests/evidence/item2.json`, hash of this GDS). The run was a single
local OpenROAD process (`--backend local`), never fanned out as a grid. A
batch-fleet attempt for the trial matrix was submitted
(`pdk.rebuild_corners` via `klt place-and-route --backend batch`) and failed
deterministically: the fleet runner image reports
`could not launch openroad: No such file or directory` (both jobs, exit 1 in
~9 s — a runner-image capability gap, not capacity; the known fleet gap, filed
as 2AMLogic/2am#6548 — an OpenROAD executor for the Spot batch fleet, with the
klt-side context in 2AMLogic/klayout-tools#4440 and its merged #4442).
