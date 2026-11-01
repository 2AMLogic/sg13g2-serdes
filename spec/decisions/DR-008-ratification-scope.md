# DR-008: Scope of the target-spec ratification

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-11-01 (revised from the 2026-10-27 draft after the two-key review)
- **Decided by**: Builder agent, issue #44; the decision is the operator's
- **Fixes rows**: R2, R3, R9 (corrections of unratified rows, see Revision; no other row changes)

Renumbered from DR-005: `main` now holds two other DR-005 files (digital timing
budget, TX collector ceiling), DR-006 and DR-007; DR-008 is the next unused
number (`TEMPLATE.md`). References in other records to "DR-005" mean those, not this.

## Context

`spec/target-spec.md` has been `PROPOSED — not ratified` since issue #2, so
nothing downstream has a ratified bound and items 5–8 of #5 are blocked. The
operator ruled (2AMLogic/2am#5346) that this repo's spec is ratified by the
standard path: the EE key and the market key review the PR, then the operator
approves it. The key directories (`ratification/ee-key/`,
`ratification/market-key/`) landed in #45. The marker grammar and release
mechanism are in 2AMLogic/2am `ratification/protocol.md`.

## Options considered

- **Ratify everything as one block, targets and evidence alike.** Rejected:
  some rows have simulated sizing or pre-layout STA records (`sim/rx/records/`,
  `sim/tx/records/20261027-024044-2e55774`, `rtl/synth/sta/`; DR-005 TX
  collector ceiling, DR-005/DR-006 digital timing) and none is a measurement, and
  several fail their row. Ratifying "met" would claim evidence that does not exist.
- **Ratify a subset of rows.** Rejected for this PR: the rows are coupled
  (R1/R14/R15 fix the link; R10/R12 depend on R14), and a partial ratification
  can be requested by the operator or a key verdict row by row without
  splitting the document.
- **Ratify the spec as a set of targets (chosen).** Each row is a binding
  target, not a result.

## Revision after the two-key review (2026-11-01)

The EE key returned `request-changes` at `a83f588` and the operator sent the PR
back (round 20261031-r5, r5-q35). The premise above was wrong in its first draft
("no row is simulated"); records exist and bear on R2, R3 and R9. Corrections,
each to a row that has never been ratified, so none is a relax (nothing was
measured FAIL against a ratified number):

- **R2**: the first draft said CMOS ≤ 625 MHz, but a 16:1 tree has stages clocked
  at 1.25 GHz and 2.5 GHz, and `design/rx/netlists/rx_top.spice` hands 5 Gb/s
  streams to CMOS through `lvl_cml2cmos`. R2 now ratifies only 5 GHz CML, the
  625 MHz CMOS word domain and the 16:1 / 16-bit shape; the 1.25 GHz and 2.5 GHz
  stages and the level conversion are **OPEN**, with the gate: a per-stage
  clock-domain list and an STA or SPICE record for every CMOS stage at ≥ 1.25 GHz.
- **R3**: "no collector node > 1.32 V" equals the +10 % rail, so a rail-loaded CML
  stage fails it by construction and the committed RX and TX records exceed it.
  BVCEO is a collector–emitter limit, so R3 is restated as Vce ≤ 1.26 V
  (90 % of the 1.4 V `npn13G2` BVCEO, arithmetic) on every device at every corner,
  transients included, with the reverse-Vbe ≤ 1.0 V clause unchanged. This is
  option 3 of the TX collector-ceiling DR-005; the operator chose it by this
  send-back. The 1.26 V margin is a proposal for the operator to confirm.
- **R9**: untrimmed `rppd` spans about −10.5 %/+11.8 % over the row's corners
  (PDK process spec p.11), outside ±10 %. The target becomes ±15 % untrimmed;
  ±10 % moves to stretch and needs a named trim mechanism. The −10 dB SDD11 target
  is unchanged.
- The 13 `insufficient-evidence` rows are ratified as targets only, each open to a
  named gate by its Verification column; R1, R11, R14, R15, R20 and R21 were
  graded sound as written.

Both key reviews re-run on the revised head before the operator ratifies.

## Decision

The PR carrying this record asks for ratification of the following, as
**targets**, at the content of `spec/target-spec.md` in commit `b347d55` as
revised above (R2, R3, R9 and the status line change; every other line is
unchanged):

- `spec/target-spec.md` rows R1–R22 (R2, R3, R9 as revised), their targets, fallbacks (5 Gb/s) and
  stretch values (12.5 Gb/s), and the binding conditions and corner sets
  written in the rows.
- `spec/clock-requirement.md` as the clock interface this block needs from a
  sibling; the comparison against `sg13g2-vco`, `sg13g2-pll` and the LC PLL
  canary stays as written there.
- `spec/channel/` CH-A and CH-B as the declared channel (DR-004).
- DR-001 to DR-004, as the reasoning behind the rows. DR-001 §Decision 3 and its
  16:1 table still say the last two stages are CML and the boundary is at the first
  divided clock; R2 as revised supersedes that wording until a per-stage record
  exists (a new record will say so).

This record does **not** ratify: any measured or simulated result, any BER or eye figure (never "measured", DR-002), or any change to a
number. Apart from the R2, R3 and R9 corrections above, no spec number, corner or fallback
is edited by this PR; the status line now points here and still says `not ratified`. A key verdict of `request-changes`, `uncompetitive` or
`escalate` leaves the spec proposed; the fix goes in a later PR, and agents do
not relax a row to obtain approval.

## Consequences

- The two `RATIFY-KEY` markers (protocol §1–2) must be posted on this PR by the
  key holders, who are neither the PR author nor each other (protocol §3). The
  Builder cannot post them and has not.
- Only the operator's approval of this PR ratifies the spec. Whether the
  status line and the Status field of DR-001 to DR-004 and DR-008 then change from
  proposed is the operator's call; no agent marks them ratified.
- After ratification, #5 is updated so its items 5–8 can be filed or released.
- A ratified target is not a design result: R1–R22 remain unverified until the
  testbenches and the link chain in `CLAUDE.md` produce evidence.
