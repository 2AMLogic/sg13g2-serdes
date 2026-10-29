# Verdict rubric

Three tokens, applied per row (`SKILL.md` Step 4) and rolled up to one
overall `approve`/`request-changes` verdict (`SKILL.md`'s "Output format").

Deliberately self-contained: nothing below names, numbers, or references
this repo's own internal fleet-operations detail — only device physics, the target
repo's own cited evidence, and `klayout-tools`' public
`docs/design-evidence-tiers.md`.

## `sound`

The row's claim is independently re-derivable from cited design sources
(schematic, netlist, sizing table) and/or backed by `sim/` evidence that
passes the relevant `design-evidence-tiers.md` T1 items for that row
(provenance-fresh, corner coverage matching the claim, Monte Carlo present
if the row is statistical). A row whose value is a **mechanical consequence**
of an already-ratified row plus the merged design's own structure — with no
new measurement needed — is also `sound`, provided the derivation is
actually checked against the source rather than merely asserted.

## `insufficient-evidence`

The row's value is not physically implausible, but the evidence backing it
falls short of what `design-evidence-tiers.md`'s T1 checklist requires for
the claim being made — an "informal, uncommitted" sanity check the design
doc itself disclaims as non-evidentiary, a single-corner/single-temperature
check standing in for a PVT claim, a plumbing-only `sim/` record (the DUT
never completed simulation) standing in for a design measurement, or a
statistical row backed only by a deterministic corner sweep. This is not a
verdict that the value is wrong — it is a statement that this key cannot
certify it as `sound` on the evidence actually on record, and the row should
stay unratified (or be flagged) until the gap closes.

## `unsound`

The row's claim contradicts what the cited design source, PDK physics, or
existing `sim/` evidence actually shows — a re-derivation that does not
match the PR's stated conclusion, a claim that ignores a device limit or
corner-dependent effect the block's own topology is known to be sensitive
to, or a row ratified on the back of evidence that itself failed (see the
relax-after-measured-FAIL check, `SKILL.md` Step 5) without an independent
physical justification for why the weaker value still holds. Absence of any
evidence at all for a claim with no plausible mechanical derivation is
`unsound` by default, the same way the market key's own rubric treats an
uncited value as `uncompetitive` by default rather than extending it the
benefit of the doubt.

## The EE-key / market-key jurisdiction boundary

This key reviews **every** row a ratification PR proposes for technical
soundness — unlike the market key, there is no row-classification split
into "in scope"/"out of scope" here, because every spec row makes a physical
engineering claim whether or not a buyer could observe it externally. What
this key does **not** do is rule on whether a technically sound value is
*competitive* — a row can be `sound` (physically well-derived, adequately
evidenced) and still be weak against the market, or `unsound` and still
happen to beat every public comp; the two questions are independent by
design.
Scoring competitiveness,
favorably or unfavorably, is itself a rubric violation for this key — it
lets the EE key exercise judgment over ground the two-key design reserves
for the market key, defeating the incentive-separation the mechanism exists
to protect.

## This block: `sg13g2-serdes` row classes

Applies to `spec/target-spec.md`'s parameter table (R1–R22). Block class:
single-lane 10 Gb/s-class SerDes; kind: `mixed-signal` (HBT current-mode logic
at the high-speed edge, CMOS logic behind it). Row numbers below are the spec's
own; a row named here that does not resolve in the spec is a defect in this
file, not in the spec.

| Class | Rows | What `sound` needs beyond the generic definition |
|---|---|---|
| Structure, no measurement | R2, R21, R22 | Netlist/RTL or clock-domain review against DR-001 for R2; `klt drc` / `klt lvs` records for R21; RTL tests for R22. A structural row with no artefact behind it is `insufficient-evidence`. |
| Device limits | R3 | Node-voltage extraction per corner from transient runs, including the +10 % supply point, checked against the DR-003 breakdown table. A nominal-corner check alone is `insufficient-evidence`. |
| Stage-level analog | R4, R6, R7, R9, R16, R18 | `PVT-full` record per the row's corners column; R4/R6 loaded by the R18 pad model. R18's value cannot come from the PDK `bondpad` model (an empty placeholder per the spec), so a pad row with no extracted or EM-derived model is `insufficient-evidence`, not `sound`. |
| Equalisation | R5, R10 | AC/pulse-response per setting and the combined channel + FFE + CTLE pulse response against the committed R14 channel model. |
| Statistical link | R1, R8, R12, R13, R15 | The full evidence chain `CLAUDE.md` requires: transistor-level PVT records for each stage → behavioural models fitted to those records, each citing the record it was fitted to → statistical link simulation over the declared channel → extrapolated bathtub. A link figure with a broken link in that chain is `insufficient-evidence`; one that cites no record is `unsound` by default. R8's sampler offset/noise must come from Monte Carlo records, not a corner sweep. |
| CDR | R11, R12, R13 | Behavioural loop model fitted to latch records (DR-002); lock and hold from simulation. The CDR loop is a stated failure point: a CDR claim backed only by an ideal-sampler model is `insufficient-evidence`. |
| Interface to a sibling | R20 | Compare the stated clock requirement against the named sibling candidates; a mismatch must be written down in the spec, not left implicit. |
| Channel assumption | R14 | The committed `channel/channel_model.py` and DR-004; the row is a model, so check the model reproduces the stated loss at the stated frequency. |

Standing rules for this block, each checked by re-derivation rather than
accepted from the PR's prose:

- BER is simulated and extrapolated, never measured (DR-002). Any row or
  record that labels it otherwise is `unsound`.
- 10 Gb/s is the target; a row verified only at the 5 Gb/s fallback is
  `insufficient-evidence` for the target column. 12.5 Gb/s stretch values are
  not a basis for any verdict.
- A relaxed value is reviewed under `SKILL.md` Step 5 even if the PR describes
  it as a clarification.
