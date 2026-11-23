# DR-011: Pad + ESD model source for R18/R19, and what the current evidence supports

- **Status**: proposed
- **Date**: 2026-11-12
- **Decided by**: builder (issue #94); ratification needs a human or Champion

Records are append-only. This record does not change R18 or R19 limits or any
ratified spec text. **Every number below is simulated or extracted from a placed,
unrouted layout. None is measured.**

## Context

R18 (pad capacitance at 5 GHz, target <= 100 fF, fallback <= 150 fF) and R19 (ESD)
are graded on an "extracted or EM pad + ESD model". The PDK `bondpad` model is an
empty placeholder, so no number comes from the PDK. Gate G5 in
`spec/validation-plan.md` depends on this model.

Tool evidence gathered for this record:

- **No EM solver** is available on the workers and none can be installed there.
- `klt extract --deck sg13g2 --parasitics` and `klt pex` (with `--mom-rlc-*` lumped
  annotations) are available.
- The pad layout from #24 (`layout/analog/pads/records/2026-11-11-835e58e/pad_esd.gds`)
  is **placed and net-labelled only**. Extracting it (klt `0.9.2.dev805`, deck `sg13g2`,
  PDK 0.3.0, `--parasitics-net padp --parasitics-net padn`) gives: 2 devices (`rsil`
  only), and **0.784 fF to substrate on `padp`**, all on `metal0`. The `diodevdd_2kv`
  and `diodevss_2kv` cells are not recognised (the deck warns that the `Recog.diode`
  99/31 marker is missing, so they extract as no device), and the bondpad layers
  are among the layers the extraction ignores. That 0.784 fF is therefore **not** a pad
  capacitance and must not be quoted as one.
- The PDK ESD diode models themselves can be simulated, but the series `rsil` is an
  OSDI model that `klt sim` does not run here (`sim/README.md`), so the benches below
  omit the 4.57 ohm series resistor.

## Options considered

1. **EM**: rejected; no solver on the workers.
2. **Hand-estimated plate capacitance on the `bondpad` placeholder**: rejected; an
   unsourced number is not evidence (`CLAUDE.md`).
3. **Layout extraction (`klt extract --parasitics` / `klt pex`) of the #24 pad cell,
   with a lumped pad-metal RLC via `--mom-rlc-*`**: chosen as the method.
4. **Diode-model capacitance only**: usable now for the ESD share, but silent on the
   bondpad and pad-metal share. Used as a partial result, not as R18 evidence.

## Decision

- The pad+ESD model source for R18 is **layout extraction** (option 3). It gives a
  lumped C at 5 GHz, not return loss or distributed behaviour; R9 SDD11 stays a
  separate question.
- **Option 3 is not yet executable.** The current pad GDS lacks the diode recognition
  markers and bondpad extraction coverage (see Context), so R18 stays a **declared
  gap**. G5 is **not evaluated** and no pass is claimed.
- The ESD share is recorded now from the PDK diode models
  (`sim/tx/records/20261112-pad/`, below), so the remaining budget for bondpad and
  pad metal is known: target 100 fF minus the ESD share, fallback 150 fF minus it.

| Quantity (simulated, 27 PVT corners, 0.6 V pad bias, one leg, no series R) | Min | Max |
|---|---|---|
| ESD C at 5 GHz, both clamps (`diodevdd_2kv` + `diodevss_2kv`) | 48.8 fF | 55.2 fF |
| `diodevdd_2kv` alone | 22.8 fF | 26.8 fF |
| `diodevss_2kv` alone | 26.0 fF | 28.3 fF |
| ESD C at 0.1 GHz (check: same as 5 GHz) | 48.8 fF | 55.2 fF |

Headroom for bondpad + pad metal at the worst-case ESD value (55.2 fF): about 45 fF
against the 100 fF target, about 95 fF against the 150 fF fallback. The ESD diodes
alone use over half the target. Capacitance is bias-dependent; only 0.6 V was
simulated.

R19: `sim/tx/pad_esd_iv.sp` records DC clamp currents at -0.6, 0.6, 1.2 and 1.8 V pad
bias across PVT (for example 0.47 nA to 74.6 uA at -0.6 V, -0.63 mA to -30 pA at
+1.8 V; sign is the current into the source `Vp`). This is a **DC model IV**, not a
TLP or HBM result, and **no ESD level is claimed**.

## Consequences

- R18 and R19 remain in `unbenched_rows` of `verification/testbench-inventory.json`:
  the extracted-pad bench does not exist yet, and the diode-only benches do not
  satisfy R18 as written. The inventory is left unchanged.
- The R4/R6/R9 benches keep their 50 fF / placeholder pad models. They still use the
  placeholder; this record does not re-point them.
- Required before G5 can be evaluated: a pad cell with the diode recognition markers
  and a bondpad extraction path (a #24 follow-up), then `klt pex` on it with the
  `--mom-rlc-*` annotation, one request per corner.
- Note for the record: the batch report lists only min/max/worst per measurement, and
  every corner id names `hbt_typ` even though the request carries `hbt_bcs`/`hbt_wcs`
  process legs, so per-corner process dependence of the diode C cannot be separated
  from this report.
