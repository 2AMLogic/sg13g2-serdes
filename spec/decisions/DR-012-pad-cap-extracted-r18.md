# DR-012: R18 pad capacitance from extracted pad metal, and the G5 reading

- **Status**: proposed
- **Date**: 2026-11-12
- **Decided by**: builder (issue #94); ratification needs a human or Champion

Records are append-only. This record follows `DR-011-pad-model-source.md` (the
`DR-011-cdr-loop-architecture.md` file shares its number; this is the next free one). It does
not change R18 or R19 limits or any ratified spec text. **Every number is simulated, or
extracted from a placed, partly unrouted layout. None is measured.**

## Context

DR-011 chose layout extraction as the R18 pad model source but could not execute it: the #24
pad GDS extracted 0.784 fF and no diodes. Issue #131 fixed the layout
(`layout/analog/pads/records/2026-11-12-fc8a7fa/record.md`): `pad_esd.gds` now extracts the
diodes and the `padp`/`padn` nets with bondpad TM2 carry **70.66 fF** of interconnect
capacitance to substrate (45.25 fF without the bondpad).

## Decision

R18 is evaluated as: extracted pad-metal C (70.66 fF, lumped on the pad node) plus the PDK ESD
clamp diode models, per pad leg, AC at 0.1 and 5 GHz, 27 PVT corners
(`sim/tx/pad_cap_extracted_5ghz.sp`, record `sim/tx/records/20261112-pad-extracted/`).

| Per pad leg, 27 PVT corners | Min | Max | R18 target 100 fF | R18 fallback 150 fF |
|---|---|---|---|---|
| Total at 5 GHz | 119.5 fF | 125.9 fF | exceeded by 19.5..25.9 fF | met, 24.1..30.5 fF margin |
| of which pad metal | 70.66 fF | 70.66 fF | | |
| of which ESD clamps | 48.8 fF | 55.2 fF | | |

## G5 reading

Gate G5 returns to the operator only if the capacitance exceeds the 150 fF fallback. It does
not, on this model, so that trigger is **not** hit. The 100 fF target is **not** met. Neither
is a pass claim: this model is a lower bound on what a real pad presents, because it leaves out
bondwire/package capacitance, pad-to-pad coupling and the series resistor, and the metal figure
is a quasi-static substrate-capacitance extraction, not a 5 GHz one. The margin to 150 fF is
24 fF at best. R18 limits are unchanged and nothing is relaxed.

## Consequences

- R18 moves from `unbenched_rows` to bench `pad-cap-extracted` in the inventory. R19 stays
  unbenched: only the PDK-model DC IV from DR-011 exists, and an extracted clamp IV needs LVS-grade
  diode recognition (#27 scope; the extracted `dantenna`/`dpantenna` are not the `diodevdd_2kv` models).
- The ESD diodes are 41..44 % of the total; the pad metal is the larger share. Cutting the
  bondpad TM2 stack (25.41 fF) or the M1/M2 area is the lever, a layout change outside this issue.
- R4/R6/R9 benches are **not** re-pointed and still use their placeholder pad models (the TX
  loads an ideal 100 ohm, the RX a 50 fF `Cpad`). The extracted 119.5..125.9 fF is about 2.4x the RX
  placeholder; re-pointing R9 would change its result and is a separate step.
- Open: replace the lumped metal C with a `klt pex` extraction that keeps pad-to-pad coupling
  and R/L (`--mom-rlc-*`), and add package parasitics from a declared source.
