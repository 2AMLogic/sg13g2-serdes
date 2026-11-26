# DR-014: Scope of the target-spec ratification

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-11-23 (revised twice: 2026-11-01 after the first two-key review, 2026-11-23 after the second and the operator's send-back)
- **Decided by**: Builder agent, issue #44; the decision is the operator's
- **Fixes rows**: R2, R3, R9 (corrections of unratified rows, see Revision; no other row changes)

Renumbered twice. First from DR-005 to DR-008, then, because `main` has since
taken DR-008 for `DR-008-stage-boundaries` (and DR-009 to DR-013 for the CDR and
pad records), from DR-008 to DR-014, the next unused number (`TEMPLATE.md`).
References in other records to "DR-005" or "DR-008" mean those records, not this
one; a citation of this record is always spelled "DR-014".

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

## Revision after the second two-key review (2026-11-23)

The operator ruled (2026-11-22, round 20261121-r19, q23) **not ratified; changes
requested**, not a release of the hold and not a rejection of the record. The EE
key returned `request-changes` and the market key `uncompetitive` at `6a1a646`.
No row number is changed in this revision; no row is relaxed. Corrections to the
record and the evidence statements:

- **Number collision.** This record was DR-008 while `DR-008-stage-boundaries`
  also existed, so "DR-008" in R2 and elsewhere was ambiguous. This record is now
  DR-014; R2 cites `DR-008-stage-boundaries` and DR-014 by full name. The
  stage-boundaries record proposes B1 (all-CML tree to 625 MHz); R2 as revised
  marks the 1.25 GHz and 2.5 GHz stages and level conversion **OPEN**, so R2
  governs and the B1 proposal is not ratified here.
- **What is ratified** is now identified by content, not by `b347d55` (see
  Decision). The first draft said "every other line is unchanged" since
  `b347d55`; that was false.
- **R3 basis.** Only the product 0.9 × 1.4 V = 1.26 V is arithmetic. The 90 %
  derating is a proposal, and the reverse-Vbe limit is taken at 100 % of BVEBO
  with no derating (also a proposal). Both are flagged for the operator in the
  row; the numbers are unchanged. Basis column now reads proposal accordingly.
- **R9 citation.** The "-10.5 %/+11.8 %, PDK process spec p.11" figure cannot be
  reproduced from anything committed in this repo (no PDK copy, no record), and
  the RX design uses an ideal resistor. The row now says so; the ±15 % target is
  unchanged and is a proposal until gate G1 closes. The −10 dB SDD11 target has no
  supporting record: the pad record covers capacitance only, and a ±15 %
  termination alone gives |Γ| ≈ 0.07 (≈ −23 dB), so SDD11 is set by pad
  capacitance (gate G4).

### Gates that keep rows at "target only"

Each is an evidence gap, not a defect in a number. None is closed by this PR.

| Gate | Row | What closes it |
|---|---|---|
| G1 | R9 | A committed source for the `rppd` window (quoted PDK table or a derivation), plus an `rppd` model run on the RX side over resistor corners |
| G2 | R3 | Per-device Vce (including transients) over PVT-full for every device on RX and TX; mux, FFE enable and level converter are unsimulated; RX records report collector-to-ground, not Vce |
| G3 | R2 | A per-stage clock-domain list and a PVT, post-layout STA or SPICE record for each CMOS stage at ≥ 1.25 GHz and for the level converter; the 625 MHz word domain currently rests on one pre-layout, ideal-clock, single-corner STA (`typ_1p20V_25C`, +0.014 ns) |
| G4 | R9 | An S-parameter or AC record of termination plus extracted pad for SDD11 to 5 GHz (pad capacitance now exists in DR-012 for R18) |

### Market key: R12 (open item for the operator)

The market key graded R12 (≥ 0.15 UIpp above 10 MHz) **uncompetitive**: the one
comparable it found, a TI retimer datasheet, states 0.6 UI SJ over 10 kHz to
250 MHz at BER 1e-15. R12 is unchanged here; an agent does not raise or relax
a row to clear a verdict, and the spec already says the mask is common practice
and **not from a named standard**. Context for the operator, all simulated and
none measured: the comp is a retimer, not a serdes; the key itself says the
datasheet figure was the only one it could fetch; and DR-011 records that the
candidate CDR meets the 0.15 mask at 30 MHz with the weakest margin on slew
(1.36× at 0.3 MHz) while other candidates fall below the mask, so a 4× tighter
target is not supported by any current record. Whether to accept R12 as a
target with that rationale, or to raise it, is the operator's call. The key also
notes that 10.0 Gb/s does not interoperate with 10.3125 Gb/s (10GBASE-R) gear;
R1 is unchanged and the 10 Gb/s figure is the repo's declared target.

## Decision

The PR carrying this record asks for ratification of the following, as
**targets**, at the content of the files named below as they stand on the head
of this PR after the merge of `main` that carries it. Relative to commit
`b347d55`, which the first draft named, the changes in the ratified set are:
R2, R3, R9 and the status lines of `spec/target-spec.md`; the 2026-11-02 refresh
of the sibling comparison in `spec/clock-requirement.md` (commit `dd31205`); the
`spec/README.md` index; and `spec/validation-plan.md`, added after `b347d55`
(it states the basis of each budget and the validation gates, and is ratified as
the plan of record, not as a result). Records DR-005 to DR-013 were added after
`b347d55` and are **not** ratified by this PR; DR-001 to DR-004 are unchanged
since `b347d55`:

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
  exists (a new record will say so). DR-003 §Decision ("no collector node may
  exceed 1.32 V", 94 % of BVCEO) and its Consequences line ("A CML rail above
  1.32 V needs a superseding record") still carry the old ceiling; R3 as revised
  (Vce ≤ 1.26 V, 90 % of the 1.4 V BVCEO, transients included) supersedes that
  node-to-ground ceiling until a superseding record exists. DR-003 is append-only
  and is not edited in place. DR-003's claim that the stack (tail + pair + load)
  fits 1.2 V CML at 0.3–0.5 Vppd is **not** ratified: the cited records contradict
  it at the −10 % corner (RX latch non-regeneration at 1.08 V, `sim/rx/records/20261027-022309-00c2ed7`;
  TX tail Vce 0.049–0.109 V at 1.08 V / −40 °C, `sim/tx/records/20261027-024044-2e55774`),
  and DR-003's "Not simulated" clause is no longer true.

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
  status line and the Status field of DR-001 to DR-004 and DR-014 then change from
  proposed is the operator's call; no agent marks them ratified.
- After ratification, #5 is updated so its items 5–8 can be filed or released.
- A ratified target is not a design result: R1–R22 remain unverified until the
  testbenches and the link chain in `CLAUDE.md` produce evidence.
