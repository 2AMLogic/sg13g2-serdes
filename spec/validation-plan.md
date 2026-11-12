# Basis, budget traceability and bounded validation plan

**Status: PROPOSED.** Companion to `target-spec.md`; changes no number.

## 1. What kind of claim each budget is

Every row of `target-spec.md` carries exactly one of these. None is
**demonstrated** today; there is no measurement and no completed
transistor-level corner run in this repo.

| Basis | Meaning | Rows today |
|---|---|---|
| **PDK** | Cited from a PDK document | R3 breakdown limits (process spec Rev. 1.2 §3) |
| **arith** | Arithmetic written out in a record | DR-001 stage rates; R14 loss values from the committed model |
| **sibling** | A sibling's ratified target at a pinned commit (itself "not met") | R20's frequency row |
| **model assumption** | A value inside a model that has no fit yet | R14 channel coefficients; R15 dual-Dirac tails; R12 mask shape |
| **proposal** | An engineering judgement, reasoning in a record | R4–R13, R16–R19, R22, the clock RJ/DJ/duty/quadrature budget |
| **demonstrated** | Backed by a corner-graded simulation record or silicon | none (625 MHz digital: a pre-layout single-corner estimate only, DR-008) |

## 2. Gaps in the use-case and primary-source trace

The first draft named no intended use case and no standard; the shape of
R12 is stated to be "common practice, not taken from a named standard".
This proposal does not invent one. For the engineering and market reviews the
open trace items are:

- **Use case**: the target channel (CH-A, 10.18 dB at 5 GHz) is an analytic
  skin-plus-dielectric curve chosen for an equalizer of 2-tap FFE plus CTLE
  (DR-004), with no reflections or crosstalk. Which board or cable class it
  stands for is unrecorded.
- **Primary sources to be checked and cited before ratification** (named,
  not yet read into the record): the jitter-tolerance and BER conventions of
  an open serial standard for 10 Gb/s class links (for R12, R15 and the
  1e-12 target); IHP's published SG13G2 process specification for the
  supply and temperature ranges (R3 tolerance is still **unconfirmed**); a
  datasheet of at least one commercial 10 Gb/s transceiver for the market
  comparison table (`ratification/market-key/comp-table-format.md`).
- **Clock RJ ≤ 0.5 ps**: derived as about half of a ≈ 1 ps rms total-link RJ
  that leaves 14σ ≈ 14 % UI at 1e-12. The 1 ps is itself a proposal, so the
  0.5 ps is a budget split, not a derived limit.
- **Error-rate conditions**: the 1e-12 figure holds only for CH-A, PRBS-31,
  the fitted behavioural models and the dual-Dirac tail fit, and is always
  labelled `extrapolated`, never `measured` (DR-002).

## 3. Remaining limits, named rather than guessed

| Area | Limit |
|---|---|
| PDK / device | VBIC HBT corner behaviour in ngspice at 5 GHz and breakdown modelling unknown until #3 |
| Pads / parasitics | `bondpad` model is an empty placeholder; the 100 fF budget has no source (R18); the core-to-pad seam is untested |
| Supply / model validity | ±10 % rail tolerance unconfirmed; model validity above the fT-related region and under +10 % supply is unchecked (DR-005 collector ceiling record) |
| Statistics | Dual-Dirac extrapolation from ≈ 1e-9 to 1e-12 assumes Gaussian tails; held-out validation tolerances (10 % eye height, 0.05 UI) are proposals |
| Clock | No provider has a four-phase, duty/quadrature-specified, comparable-jitter output (`clock-requirement.md`) |

## 4. Bounded validation and resource plan

No simulation is authorized by this plan; each gate needs its own approval
and a declared compute budget. Multi-corner and Monte Carlo runs go through
`klt sim` to the batch fleet, not local grids.

| Gate | Question | Evidence required | Stop condition |
|---|---|---|---|
| G1 | Does ngspice simulate `npn13G2` CML at 5 GHz across PVT-edge? | #3 smoke results; convergence and runtime per corner | Cannot converge at TT-27 → file a tool/model issue; hold R2–R4 as "not simulated" |
| G2 | Does the level converter seam close at the 625 MHz boundary? | Transistor-level converter record at PVT-edge, delay spread vs. the 1.6 ns budget | Delay spread consumes more than half the word period → B3 (superseding record) |
| G3 | Does the digital partition hold 625 MHz post-layout? | Routed STA at several corners (#25) | Negative slack after one restructure round → B3 |
| G4 | Do the per-stage records support fitted behavioural models? | Fit on a subset, validate held-out within DR-002 tolerances | Validation error out of tolerance → no BER claim from that model |
| G5 | Does the pad network meet R18? | Extracted or EM pad + ESD model | Cap > fallback 150 fF → return to the operator with a 5 Gb/s proposal |

G5 status (2026-11-12, DR-011): **not evaluated.** The ESD diodes alone add 48.8 to 55.2 fF per leg (simulated, 27 PVT corners); the bondpad and pad-metal share has no extracted value because the current pad GDS does not extract the diodes or bondpad. No pass or fail is claimed.
| G6 | Is a clock provider available for the clock table? | A sibling spec stating phases, duty/quadrature and a comparable jitter | None after the requirement is filed → remain "no provider"; no design here |

Per-gate resource caps are set when each gate is approved, not here.
