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

Per-trial six-corner rows (setup WNS / setup TNS / hold WNS in ns, from each
route's own `report.json` `corners[]`; every row `timing_status: constrained`).
T2 is the committed `report.json`; T1 and T3 were re-run in scratch space
outside the repository on the same netlist, seed 1, clock 1.6 ns with the
pinned klt 0.9.0, and reproduce the headline values in the matrix above
(T3 wirelength 163855 um, T1 147177 um, T2 156649 um).

| corner | T1 status | T1 setup WNS | T1 setup TNS | T1 hold WNS | T2 status | T2 setup WNS | T2 setup TNS | T2 hold WNS | T3 status | T3 setup WNS | T3 setup TNS | T3 hold WNS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fast_1p32V_m40C | constrained | +0.55389 | 0 | +0.13276 | constrained | +0.63951 | 0 | +0.13524 | constrained | +0.60563 | 0 | +0.13318 |
| fast_1p65V_m40C | constrained | +0.86609 | 0 | +0.09812 | constrained | +0.92507 | 0 | +0.09988 | constrained | +0.90678 | 0 | +0.09843 |
| slow_1p08V_125C | constrained | -0.93288 | -224.504 | +0.31291 | constrained | -0.73221 | -108.556 | +0.31988 | constrained | -0.80868 | -126.405 | +0.31406 |
| slow_1p35V_125C | constrained | +0.02089 | 0 | +0.20420 | constrained | +0.13260 | 0 | +0.20860 | constrained | +0.08285 | 0 | +0.20494 |
| typ_1p20V_25C | constrained | +0.01463 | 0 | +0.19798 | constrained | +0.13280 | 0 | +0.20191 | constrained | +0.08115 | 0 | +0.19864 |
| typ_1p50V_25C | constrained | +0.55293 | 0 | +0.13689 | constrained | +0.62616 | 0 | +0.13953 | constrained | +0.59561 | 0 | +0.13735 |

Reading the table: T3 has a lower setup WNS and a lower hold WNS than T2 in
every one of the six corners, so the "every corner worse" statement above holds
for both metrics; T1 is lower than T2 in setup WNS at all six corners.

### Per-corner path report and what limits slow 1.08 V (issue #197 steps 1 and 6)

`sta-corners.json` is a standalone `klt sta` (pinned 0.9.0) multi-corner run on
this record's routed DEF (`sta-corners.request.json`, run from its committed
location; `def` is the sibling file). Timing model of this report: `clk` at
1.6 ns, **ideal** clock, `geometry_source: routed`, no SPEF and no wire-load
model, i.e. cell delays and pin loading from the LEF/DEF only. The in-flow
sweep in `report.json` is a different model (ideal clocks, `interconnect_corner:
nom`, global-routing RC estimates). Its worst path is **not named** in
`report.json`.

| corner | standalone worst setup path | standalone WNS | standalone TNS | violating endpoints |
|---|---|---|---|---|
| slow_1p08V_125C | `u_pd/_699_/Q -> u_pd/_721_/D` | -0.47660 | -39.1535 | 217 |
| slow_1p35V_125C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.28679 | 0 | 0 |
| typ_1p20V_25C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.28402 | 0 | 0 |
| typ_1p50V_25C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.73045 | 0 | 0 |
| fast_1p32V_m40C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.73587 | 0 | 0 |
| fast_1p65V_m40C | `u_pd/_699_/Q -> u_pd/_721_/D` | +0.99410 | 0 | 0 |

**What was measured.**

- At slow 1.08 V the standalone model gives WNS -0.47660 ns / TNS -39.1535 ns
  / 217 violating endpoints; the in-flow model gives WNS -0.73221 ns / TNS
  -108.556 ns / 394 violating endpoints (`report.json`
  `setup_violation_count`). Both are register-to-register setup misses at the
  1.6 ns constraint; hold is met in both.
- On the 2026-11-14 baseline DEF the standalone model's worst path was
  `u_flt/_1028_/Q -> u_flt/_1037_/D` at all six corners (316 violating
  endpoints, WNS -0.65431 ns at slow 1.08 V).
- In the standalone model the worst path at slow 1.08 V is in `u_pd`
  (CDR phase detector, `rtl/serdes_cdr_pd.v`). Its slack at the five other
  corners is positive (table above).

**What is not established by this record** (earlier text drew these
conclusions; they are withdrawn):

- *A wire-delay contribution.* The two WNS values come from different timing
  models and, for the in-flow one, an unnamed path. Their 0.25561 ns difference
  cannot be attributed to wire delay on `u_pd/_699_ -> _721_`: wire
  capacitance also changes cell delay, and the models may disagree on other
  inputs. No measurement here separates cell delay from wire delay.
- *The old filter path's current slack.* The standalone model reports only the
  single worst path per corner; whether the `u_flt` path that was worst on the
  baseline is now repaired, or merely no longer worst, is unmeasured.
- *Path types or module distribution of the failing endpoints.* 217 (or 394)
  is a count only; klt 0.9.0 reports one worst path per corner plus totals, so
  how the endpoints split across `u_pd`, `u_flt` or other modules is unmeasured.
  Worst-N endpoint lists (2AMLogic/klayout-tools#5424) and per-stage cell/wire
  increments (2AMLogic/klayout-tools#5783, merged as
  2AMLogic/klayout-tools#6014) shipped after 0.9.0; a klt pin bump would give
  the path-level data this account needs. That tooling gap is a fallback for
  measurement, not evidence of closure.
- *A cause for the residual miss.* This record therefore states no RTL
  rationale. No RTL change was made in this round; the pre-layout `u_pd`
  margin (+0.19 ns typ, `rtl/synth/sta/serdes_digital_top.paths.txt`) is from a
  different model (synthesis STA) and is not evidence about the 1.08 V route.

The -0.73221 ns slow 1.08 V miss remains unexplained at path level; this
record claims partial closure only (typ and slow 1.35 V setup met, slow 1.08 V
open per issue #197's allowance).

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

Clarification (2026-11-23, issue #239): the timing-model disclosure above
(`sta-corners.json`: "ideal clock, `geometry_source: routed`, no SPEF and no
wire-load model") and the "What is not established" list omit one limit of
that standalone report. Every corner of `sta-corners.json` carries
`constraint_completeness.status: incomplete`,
`unconstrained_endpoints.count: 43`, `unclocked_registers.count: 0` — all six
corners identical, re-measured from the committed file with
`jq -r '.corners[] | [.corner, .constraint_completeness.status, .constraint_completeness.unconstrained_endpoints.count, .constraint_completeness.unclocked_registers.count] | @tsv'`.
Read as: `unclocked_registers.count == 0` means no register escapes the setup
check, so the register-to-register framing of the slow_1p08V_125C miss above
holds; 43 endpoints — the report's sample is `eye_ph_off[*]`, `eye_smp_off[*]`,
`pi_code[*]`, all top-level output ports (sample limited to 20,
`truncated: true`) — carry no setup check in this model. The 217 violating
endpoints above is therefore a count over the constrained endpoint set only.
Nothing in the original text is corrected. In particular the record's decline
to attribute the 217-vs-394 gap against the in-flow model stands: whether
these 43 endpoints account for any of it is unmeasured. Appended per the
append-only rule; the original text above is unchanged.
