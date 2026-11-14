# Roadmap

`sg13g2-serdes` is a single-lane 10 Gb/s-class SerDes on IHP SG13G2: HBT
current-mode logic at the serial edge, CMOS behind it.

Status as of 2026-11-13, `main` @ `eb34d10`.

## Where it stands

The README's "nothing is designed yet" is out of date: design sources, layout
and testbenches for both partitions are on `main`. The spec is still
**PROPOSED** (#2), so results are graded against draft rows, never measured.

Position on the T1 checklist (`manifests/design-evidence-tiers.md`, tracker #5),
read from the verdict of record `manifests/sg13g2-serdes.signoff.json`
(klt 0.9.0, kept current by CI): **7 of 22 items met**.

| Item | Analog | Digital | Evidence or reason |
|---|---|---|---|
| 1 Design sources | unmet (stale) | unmet (stale) | `manifests/evidence/item1.json` predates the regenerated `rtl/synth/` netlist |
| 2 Layout | met | met | `layout/analog/top/records/2026-11-12-0193777/`, `layout/digital/records/2026-11-10-f6fe587/` |
| 3 DRC clean | met | met | `drc.json` beside each GDS; coverage gaps listed in `layout/README.md` |
| 4 LVS clean | unmet | met | digital: `manifests/evidence/item4.json` (#136); analog: #128 |
| 5 Corner verification vs a ratified spec | unmet | unmet | no ratified spec (#2) |
| 6 Monte Carlo | unmet | unmet | no ratified spec (#2) |
| 7 Post-layout verification | unmet | unmet | not started |
| 8 Characterization report | unmet | unmet | not started |
| 9 Testbenches shipped | unmet (stale) | unmet (stale) | the manifest's item-9 hash pin lags `verification/testbench-inventory.json` |
| 10 Repo hygiene | met | met | `manifests/evidence/item10.json` |
| 11 Power delivery | unmet | unmet | #29 |

Three qualifications the table does not show:

- **The analog layout is placed, not routed.** Item 2 and item 3 are met for the
  geometry that exists; nets with an HBT terminal are deliberately left unrouted
  (`layout/README.md`). Routing is #127.
- **The digital layout describes an older netlist.** The routed GDS, its DRC and
  its LVS were built from the synthesized netlist with sha256 `d6591244…`; the
  netlist on `main` is `08b90805…` since the klt 0.9.0 regeneration (`506b37e`).
- **Post-route timing is not closed.** The 2026-11-10 record reports setup slack
  of -0.033 ns (typ), -0.048 ns (slow 1.35 V) and -0.992 ns (slow 1.08 V, 125 C)
  at the 1.6 ns word clock; hold is met everywhere.

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

Startable today. None has an issue yet; drafts accompany this roadmap.

1. **Bring the signoff verdict back to fresh for items 1 and 9.**
   Done when `klt signoff` grades neither item `stale_evidence`, the committed
   record matches, and `scripts/check-ci.sh --regen` re-attests item 1 and
   updates the manifest pins so the next change does not strand them again.
2. **Re-run digital place-and-route, DRC and LVS on the current netlist.**
   Done when a new dated record under `layout/digital/records/` reports the
   committed netlist hash, `scripts/check-pnr-fresh.sh` and
   `scripts/check-lvs-fresh.sh` exit 0, and items 2, 3 and 4 (digital) are cited
   from the new records and still graded `met`.
3. **Make the RX latch regeneration record complete.**
   The newest RX record (`sim/rx/records/20261110-222737-506b37e/`) has
   `latch_regen` at 12 of 27 corners passing with 6 in error and "not reached"
   at 1.08 V cold. Done when a new append-only record has no `error` corner and
   `sim/rx/README.md` says, per failing corner, whether regeneration is slow or
   the output swing never reaches the threshold. No resizing in this step.
4. **Correct the status text.** README ("nothing is designed yet", "pre-spec"),
   `spec/README.md` (decision list stops at DR-008), `manifests/README.md`
   (names klt 0.8.0 as the pin) and the pad sentence in `sim/README.md`.
   Done when each statement matches `main` and `scripts/check-ci.sh` passes.

## Next

- **G3 verdict on post-route timing** (after Now 2). The gate's stop condition
  is negative slack after one restructure round, and DR-006 was that round.
  Done when a decision record states the multi-corner post-route slack of the
  refreshed record and which branch of G3 applies.
- **Item 11, digital half** (after Now 2). #29 covers both partitions and is
  parked on the analog one. Done when a `klt erc` supply report for the routed
  digital GDS is committed and `11.digital` is cited; the curator's note on #29
  about the missing tap cell in `sg13g2_stdcell` has to be settled against the
  grader first.
- **Second-order CDR loop in RTL**, #134 (after the DR-011 ruling below). It
  regenerates synthesis, so Now 1 and Now 2 repeat after it.
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
| Operator | Accept DR-011's loop, and renumber one of the two records named DR-011 | #134 |
| Operator | Merge decision on the mux clock swing requirement | #98, PR #99 |
| Upstream tool | Multi-layer routing for composed analog cells | #127, `klayout-tools#1962` |
| Upstream tool | Routing stubs landing inside the `npn13G2` via array | `klayout-tools#5398` |
| #127 | Analog LVS, RX pad bench on the extracted pad, power delivery | #128, #143, #29 |

On the tracker as read today, **no open issue is ready to build**: each one is
held, blocked or has an approved PR waiting. The Now items are the dispatchable
work once filed.

## Not planned

- A PLL or VCO here; the repo specifies the clock it needs.
- Line coding (8b/10b, 64b/66b) or any protocol layer.
- Letting the 12.5 Gb/s stretch drive architecture, or relaxing a spec row.
