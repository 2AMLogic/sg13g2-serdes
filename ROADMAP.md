# Roadmap

`sg13g2-serdes` is a single-lane 10 Gb/s-class SerDes on IHP SG13G2: HBT
current-mode logic at the serial edge, CMOS behind it.

Status as of 2026-11-15, `main` @ `15dcde0`.

## Where it stands

The README's "nothing is designed yet" is out of date: design sources, layout
and testbenches for both partitions are on `main`. The spec is still
**PROPOSED** (#2), so results are graded against draft rows, never measured.

Position on the T1 checklist (`manifests/design-evidence-tiers.md`, tracker #5),
read from the verdict of record `manifests/sg13g2-serdes.signoff.json`
(klt 0.9.0, kept current by CI): **11 of 22 items met**.

| Item | Analog | Digital | Evidence or reason |
|---|---|---|---|
| 1 Design sources | met | met | `manifests/evidence/item1.json` re-attested against the current netlist `08b90805…`, 73/73 checks pass (#157) |
| 2 Layout | met | met | `layout/analog/top/records/2026-11-12-0193777/`, `layout/digital/records/2026-11-14-d19ba10/` |
| 3 DRC clean | met | met | `drc.json` beside each GDS; coverage gaps listed in `layout/README.md` |
| 4 LVS clean | unmet | met | digital: `manifests/evidence/item4.json` (#136); analog: #128 |
| 5 Corner verification vs a ratified spec | unmet | unmet | no ratified spec (#2) |
| 6 Monte Carlo | unmet | unmet | no ratified spec (#2) |
| 7 Post-layout verification | unmet | unmet | not started |
| 8 Characterization report | unmet | unmet | not started |
| 9 Testbenches shipped | met | met | `manifests/evidence/item9.json` pins the current `verification/testbench-inventory.json`, 66/66 checks pass (#157) |
| 10 Repo hygiene | met | met | `manifests/evidence/item10.json` |
| 11 Power delivery | unmet | met | digital: `layout/digital/erc-records/2026-11-20-9f98e1e/` (#198); analog: #29 |

Three qualifications the table does not show:

- **The analog layout is placed, not routed.** Item 2 and item 3 are met for the
  geometry that exists; nets with an HBT terminal are deliberately left unrouted
  (`layout/README.md`). Routing is #127.
- **Digital layout lineage.** The superseded 2026-11-10 record
  (`layout/digital/records/2026-11-10-f6fe587/`) was built from the
  synthesized netlist with sha256 `d6591244…`; the current record
  (`layout/digital/records/2026-11-14-d19ba10/`, #151 via PR #166) re-ran
  place-and-route, DRC and LVS on the netlist now on `main`, `08b90805…`, and
  items 2, 3 and 4 (digital) cite it.
- **Post-route timing is not closed.** The 2026-11-14 record reports setup
  slack of -0.0318 ns (typ), -0.0258 ns (slow 1.35 V, 125 C) and -1.007 ns
  (slow 1.08 V, 125 C) at the 1.6 ns word clock, one violating endpoint; hold
  is met in all six corners.

Outside the checklist:

- Spec proposal: `spec/target-spec.md` (R1 to R22), DR-001 to DR-013 (all
  `proposed`), gates G1 to G6 in `spec/validation-plan.md`; both review-key
  directories are installed (`ratification/`, PR #45).
- Benches: every simulation-graded row has one (`sim/README.md`). R18 and R19
  run on devices extracted from `pad_esd.gds` (DR-012, DR-013); the TX R4/R6
  benches carry the extracted pad load (#145).
- CDR: the first-order loop does not hold the 1e-12 eye once dither is included
  (#102, DR-009, DR-010); DR-011 proposes a second-order loop (#133).

## Now

Startable today. Each item names its issue and PR, so an entry stays true as
its PR lands; items whose deliverable is already committed are dropped, not
carried. The two prior Now items landed on `main` since the last snapshot:
the digital P&R/DRC/LVS re-run (#151, PR #166) and the latch-regeneration
record (#152, PR #156).

1. **Correct the status text** — #153, PR #160 approved and awaiting merge.
   README still opens "Nothing is designed yet", `spec/README.md` stops its
   decision list at DR-008, `manifests/README.md` does not yet mark its 0.8.0
   sentences historical (the pin is 0.9.0), and `sim/README.md` does not yet
   separate the extracted R6 pad model from the R9 placeholder (#143). Done
   when each statement matches `main` and `scripts/check-ci.sh` passes.
2. **G3 verdict on post-route timing** — the record it grades now exists:
   `layout/digital/records/2026-11-14-d19ba10/` (#151, PR #166). The gate's
   stop condition is negative slack after one restructure round, and DR-006
   was that round. Done when a decision record states the multi-corner
   post-route slack of that record and which branch of G3 applies.

## Next

- **Second-order CDR loop in RTL**, #134 (after the DR-011 ruling below). It
  regenerates synthesis, so the digital P&R/DRC/LVS re-run (#151, PR #166)
  repeats after it.
- **Analog routing, then LVS, then power**: #127, then #128 and #143, then the
  analog half of #29. All wait on the router gap `2AMLogic/klayout-tools#1962`.
- **Items 5 to 8** (after ratification). Not filed; there are no ratified rows
  to grade against yet.

## Later

- **Behavioural-model fit validation** (DR-002 step 3, G4). Not done: there is
  no transistor-level link-level result to validate against (DR-011). Question
  first: which transistor-level run can serve as the held-out reference?
- **Sampler offset and noise statistics.** The link benches print these as
  unfitted assumptions (`sim/README.md`). Question first: can the PDK's HBT
  mismatch sections be run through the batch simulator at the latch?
- **Clock provider and R20 random jitter** (G6, `spec/clock-requirement.md`).
  No sibling is selected. Question first: does any sibling state phases, duty
  and quadrature error and a jitter figure comparable to the budget?
- **Level-converter seam at 625 MHz** (G2). DR-008 records it as unresolved.
- **Pad capacitance.** DR-012: the 100 fF target is not met, the 150 fF fallback
  is. Question first: shrink the pad network or accept the fallback reading.

## Blocked and waiting

| Waiting on | What | Where |
|---|---|---|
| Operator | Ratify the target spec; the PR is review-approved and held | #2, #44, PR #47 |
| Operator | Accept DR-011's loop, and renumber one of the two records named DR-005 and one of the two named DR-011 | #134 |
| Operator | Merge decision on the mux clock swing requirement | #98, PR #99 |
| Upstream tool | Multi-layer routing for composed analog cells | #127, `klayout-tools#1962` |
| #127 | Analog LVS, RX pad bench on the extracted pad, power delivery | #128, #143, #29 |

The forge, not this document, is the source of truth for what is ready to
build; a snapshot of a moving tracker decays in hours. The live queues are
`gh issue list --label loom:issue` and `gh pr list`, and the entries above
carry their issue and PR numbers so each claim can be checked against them
instead of trusted.

## Not planned

- A PLL or VCO here; the repo specifies the clock it needs.
- Line coding (8b/10b, 64b/66b) or any protocol layer.
- Letting the 12.5 Gb/s stretch drive architecture, or relaxing a spec row.
