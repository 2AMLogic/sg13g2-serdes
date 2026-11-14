# spec

Target specification for `sg13g2-serdes`. **Status: PROPOSED — not ratified.**
Ratification is the operator's act on merge (issue #2); until then nothing
here binds design work, and agents do not relax a ratified row to make
results pass (`CLAUDE.md`).

| File | Content |
|---|---|
| [`target-spec.md`](target-spec.md) | Every parameter: target / fallback / stretch, verification, PVT corners, basis; pads and ESD; open-question dispositions |
| [`clock-requirement.md`](clock-requirement.md) | The clock this block needs, compared with `sg13g2-vco`, `sg13g2-pll` and `sg13g2-lc-pll` at pinned commits |
| [`channel/`](channel/README.md) | The channel model (`channel_model.py`) and its loss at Nyquist |
| [`decisions/`](decisions/) | Decision records, append-only (all proposed) — every record present is listed under "Decision records" below |
| [`validation-plan.md`](validation-plan.md) | Basis of each budget, remaining limits, bounded validation gates with stop conditions |

Spec changes go through a new decision record; a ratified record is
superseded, never edited.

## Decision records

Every file in [`decisions/`](decisions/) that is a record, in filename order.
All fifteen are **proposed** — none is ratified.

| Record | Subject |
|---|---|
| [`DR-001-architecture.md`](decisions/DR-001-architecture.md) | Line rate, rate architecture, HBT/CMOS split, serialization ratio |
| [`DR-002-error-rate-methodology.md`](decisions/DR-002-error-rate-methodology.md) | Error-rate methodology and labelling |
| [`DR-003-supplies-and-hbt-breakdown.md`](decisions/DR-003-supplies-and-hbt-breakdown.md) | Supplies, device flavours and HBT breakdown limits |
| [`DR-004-channel-model.md`](decisions/DR-004-channel-model.md) | Channel model |
| [`DR-005-digital-timing-budget.md`](decisions/DR-005-digital-timing-budget.md) | Digital partition misses the 1.6 ns word-clock budget |
| [`DR-005-tx-collector-ceiling-at-plus-10pct-supply.md`](decisions/DR-005-tx-collector-ceiling-at-plus-10pct-supply.md) | TX stages with resistor loads to the rail cannot meet "no collector node > 1.32 V" at +10 % supply |
| [`DR-006-digital-timing-restructure.md`](decisions/DR-006-digital-timing-restructure.md) | Digital partition restructured to meet the 1.6 ns word clock (pre-layout); does not supersede DR-005 |
| [`DR-007-cdr-loop-analysis.md`](decisions/DR-007-cdr-loop-analysis.md) | CDR loop delay budget (analytical, word-rate model); its conclusions are superseded by DR-010 |
| [`DR-008-stage-boundaries.md`](decisions/DR-008-stage-boundaries.md) | Serializer/deserializer stage boundaries and the 625 MHz assumption; clarifies DR-001 decision 3 and R2 |
| [`DR-009-cdr-dither-closure.md`](decisions/DR-009-cdr-dither-closure.md) | CDR dither closes the 1e-12 eye; proposed fix KP = 8, KI = 0 — not adopted, see DR-011 |
| [`DR-010-cdr-loop-analysis-corrected.md`](decisions/DR-010-cdr-loop-analysis-corrected.md) | CDR loop analysis corrected: the noise-free columns were a 1-vote loop |
| [`DR-011-cdr-loop-architecture.md`](decisions/DR-011-cdr-loop-architecture.md) | CDR loop architecture: second-order loop with a fractional integral path |
| [`DR-011-pad-model-source.md`](decisions/DR-011-pad-model-source.md) | Pad + ESD model source for R18/R19, and what the present evidence supports |
| [`DR-012-pad-cap-extracted-r18.md`](decisions/DR-012-pad-cap-extracted-r18.md) | R18 pad capacitance from extracted pad metal, and the G5 reading |
| [`DR-013-r19-extracted-clamp-iv.md`](decisions/DR-013-r19-extracted-clamp-iv.md) | R19 evaluated as a DC clamp IV on the extracted `pad_esd` devices |

**Two numbers are each carried by two different records**: DR-005 and DR-011.
The collisions happened when records landed concurrently. The permanent ID is
the filename, and an append-only record is never renumbered in place, so both
pairs stay as they are; cite records by filename, not by number alone.

`decisions/` also holds `TEMPLATE.md` and the analysis-script outputs
`DR-007-output.txt`, `DR-009-output.txt`, `DR-010-output.txt` and
`DR-011-output.txt`. Those are artifacts of the records above, not records.
