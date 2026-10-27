# DR-005: Scope of the target-spec ratification

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-27
- **Decided by**: Builder agent, issue #44; the decision is the operator's
- **Fixes rows**: none (R1–R22 are unchanged by this record)

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
  no row is simulated or measured yet (the spec says so), so ratifying
  "met" would claim evidence that does not exist.
- **Ratify a subset of rows.** Rejected for this PR: the rows are coupled
  (R1/R14/R15 fix the link; R10/R12 depend on R14), and a partial ratification
  can be requested by the operator or a key verdict row by row without
  splitting the document.
- **Ratify the spec as a set of targets (chosen).** Each row is a binding
  target, not a result.

## Decision

The PR carrying this record asks for ratification of the following, as
**targets**, at the content of `spec/target-spec.md` in commit `b347d55`
(every line except the status line, which this PR changes):

- `spec/target-spec.md` rows R1–R22, their targets, fallbacks (5 Gb/s) and
  stretch values (12.5 Gb/s), and the binding conditions and corner sets
  written in the rows.
- `spec/clock-requirement.md` as the clock interface this block needs from a
  sibling; the comparison against `sg13g2-vco`, `sg13g2-pll` and the LC PLL
  canary stays as written there.
- `spec/channel/` CH-A and CH-B as the declared channel (DR-004).
- DR-001 to DR-004, as the reasoning behind the rows.

This record does **not** ratify: any measured or simulated result (none
exists), any BER or eye figure (never "measured", DR-002), or any change to a
number. No spec number, corner or fallback is edited by this PR; the only
change to `target-spec.md` is the status line, which now points here and still
says `not ratified`. A key verdict of `request-changes`, `uncompetitive` or
`escalate` leaves the spec proposed; the fix goes in a later PR, and agents do
not relax a row to obtain approval.

## Consequences

- The two `RATIFY-KEY` markers (protocol §1–2) must be posted on this PR by the
  key holders, who are neither the PR author nor each other (protocol §3). The
  Builder cannot post them and has not.
- Only the operator's approval of this PR ratifies the spec. Whether the
  status line and the Status field of DR-001 to DR-005 then change from
  proposed is the operator's call; no agent marks them ratified.
- After ratification, #5 is updated so its items 5–8 can be filed or released.
- A ratified target is not a design result: R1–R22 remain unverified until the
  testbenches and the link chain in `CLAUDE.md` produce evidence.
