# DR-013: R19 evaluated as a DC clamp IV on the extracted pad_esd devices

- **Status**: proposed
- **Date**: 2026-11-12
- **Decided by**: builder (issue #94); ratification needs a human or Champion

Records are append-only. This follows `DR-011-pad-model-source.md` and
`DR-012-pad-cap-extracted-r18.md` (DR-011 is numbered twice; this is the next free number). It does
not change R18 or R19 limits or any ratified spec text. **Every number is simulated from extracted
device geometry. None is measured.**

## Context

DR-012 left R19 unbenched: only the PDK-model DC IV (`sim/tx/pad_esd_iv.sp`, schematic
`diodevdd_2kv`/`diodevss_2kv`) existed. Issue #131 made the layout extract its diodes
(`dpantenna`/`dantenna`, 35.0028 um2, 58.08 um each) and seam resistors (5.12 ohm). R19's
allowed grading is "extracted clamp characteristics only; no ESD qualification claim".

## Decision

R19 is graded by `sim/tx/pad_esd_iv_extracted.sp`: the extracted devices of the `padp` leg, driven
with a DC pad sweep, 27 PVT corners, record `sim/tx/records/20261112-pad-esd-iv-extracted/`. The
R19 row moves from `unbenched_rows` to bench `pad-esd-iv-extracted`. The schematic-side IV from
DR-011 stays as a cross-check. No ESD level (HBM/TLP) is claimed and none is implied.

## Consequences

- Limits: PDK `dantenna`/`dpantenna` are reverse-bias fits; forward currents are a lower bound.
  The diode corner sections do not move them. The extracted `rx_term_pad` is unrouted, so only the TX pad cell is covered.
  Whether the extracted `dantenna`/`dpantenna` equal the `diodevdd_2kv` clamp is not established
  (LVS is #27 scope); the two benches are not compared quantitatively here.
- R4/R6/R9 benches are **not** re-pointed and still use their placeholder pad models (DR-012
  explains why: re-pointing R9 changes its result, and the RX pad cell is unrouted). Their bench
  `limitations` already state the placeholder.
- G5 reading is unchanged from DR-012 (`spec/validation-plan.md`).
