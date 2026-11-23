# Source note: the `rppd` tolerance window (R9, gate G1 of #238, issue #240)

**Committed source for the `rppd` process-tolerance window.** This note quotes
the PDK's own process specification so R9's resistor-corner column can cite a
committed, page-level source instead of an unreproducible figure. It is a
quotation plus labelled arithmetic; nothing here is a measurement, and no
number in `spec/target-spec.md` is changed by it (agents do not relax the
ratified spec; a mismatch is reported, not edited in).

## Source

`SG13G2_os_process_spec.pdf` as shipped inside the pinned PDK tarball of
`sim/pdk.json` (IHP-GmbH/IHP-Open-PDK `v0.3.0`, tarball sha256
`f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`), path
`ihp-sg13g2/libs.doc/doc/SG13G2_os_process_spec.pdf`. Document title
"SG13G2 Process Specification Rev. 1.2", **page 11 of 26, section 2.8 Rppd**
(page 11 checked out of the pinned tarball on 2026-11-23; two independent
text extractors, pypdf and pdfminer.six, agree on every figure below. The
Ω glyph linearizes as `W` in text extraction; units are restored by hand and
marked).

Quoted verbatim (table linearized; `§2.8` intro sentence first):

> Rppd utilizes unsalicided, p-doped gate polysilicon as resistor material.
> For realizing precision resistors, a line width of 2µm or higher is
> recommended.
>
> | Parameter | Name | Unit | Min | Target | Max | Meas. Cond. | Comment |
> |---|---|---|---|---|---|---|---|
> | Sheet Resistance | RSRPPD | Ω [extracts as `W`] | 235 | 260 | 285 | A.i | |
> | Line Width Delta | DWRPPD | nm | -24 | 6 | 36 | A.i | |
> | Temperature Coefficients | TC1NRPPD TC2NRPPD | ppm/K ppm/K² | | 170 | | A.af | two parameters, one value each |
> | Matching Coefficient | MATRPPD | nm | | 15 | | A.ac | |
> | Metal-to-Body-Resistance | RCRPPD | Ω·µm [extracts as `W*µm`] | | 35 | | A.ae | |
> | Temperature Coefficient Metal-toBody-Resistance | TC3NRPPD | ppm/K | | -950 | | | |
> | Max. Current Density | IMRPPD | mA/µm | | 1.2 | | | 11 years @105°C |

(The two-parameter rows carry one value per parameter in the Min/Target/Max
band; the original layout is preserved above, empty cells and all.)

## The window, three ways

All percentages are relative to the 260 Ω/sq target. **arith** basis unless
marked **PDK**.

1. **Sheet resistance only (PDK, p.11):** 235/260 = **−9.62 %**, 285/260 =
   **+9.62 %**. This is the window on `rsh` alone.
2. **Simulation library corners (PDK, `cornerRES.lib`, quoted 2026-11-23
   from the pinned tarball):** `.param rsh_rppd` = 234.0 (`res_bcs`),
   260.0 (`res_typ`), 286.0 (`res_wcs`) Ω/sq, i.e. **−10.00 %/+10.08 %**.
   The library corners sit ~1 Ω outside the p.11 window at each edge and
   envelope it. The two PDK sources therefore do not agree exactly; both are
   recorded, neither is rounded into the other.
3. **Drawn resistance at the recommended width (arith, derived):** a drawn
   resistor's value is `rsh · l/(w + DW)`. At the p.11-recommended precision
   width w = 2 µm, with the target DW = 6 nm (the `r3_cmc` model's own `xw`
   offset — see cross-check below), folding the p.11 min/max columns of both
   `rsh` and `DW` into one effective sheet resistance:
   - low edge: `235/(2.036)` vs `260/(2.006)` → **−10.95 %**, `rsh_eff` =
     235 · 2.006/2.036 = **231.537 Ω/sq**
   - high edge: `285/(1.976)` vs `260/(2.006)` → **+11.28 %**, `rsh_eff` =
     285 · 2.006/1.976 = **289.327 Ω/sq**

   This derived window is what a termination resistor's as-drawn value spans;
   it is wider than the sheet-only window because DWRPPD is asymmetric
   (−24/+36 nm). The `r3_cmc` model has no width-delta parameter (`xw` is
   fixed at 6 nm = the p.11 target), so a simulation can only reach this
   window by overriding `rsh` with the folded values above — which is what
   the window members of the RX record do (`corners.params` on `rsh_rppd`).

## Cross-check: the model card encodes the p.11 target column

`resistors_mod.lib`'s `.model res_rppd r3_cmc` (same pinned tarball) carries
`tc1=170e-6` (170 ppm/K), `tc2=0.4e-6` (0.4 ppm/K²), `tc1rc=-950e-6`
(−950 ppm/K), `rzspec=35e-6` (35 Ω·µm), `xw=0.006` (6 nm) — each equal to
the p.11 target column it corresponds to, and `rsh=rsh_rppd` reads the
corner parameter. The library's nominal model and the process spec's target
column are the same numbers (observed match, quoted 2026-11-23).

## Discrepancy versus R9's cited window (reported, not reconciled)

R9's resistor-corner basis as filed in DR-014 (PR #47 head `8f213e3`, not on
`main`; the PR's own second-key revision already flags it as
non-reproducible) reads "untrimmed `rppd` spans about −10.5 %/+11.8 % …
(PDK process spec p.11)". From the quoted p.11 table:

- the sheet-only window is −9.62 %/+9.62 %, and
- the width-delta-folded window at the recommended 2 µm width is
  −10.95 %/+11.28 %;

neither reproduces −10.5 %/+11.8 %, and no width in the p.11-recommended
≥ 2 µm range does (the folded window converges to the sheet-only window as
w grows and widens below 2 µm). The DR-014 figure therefore has no
committed derivation; this note supersedes it as R9's citable source. R9's
numbers are unchanged here (±10 % target / ±15 % fallback as they stand in
`spec/target-spec.md`); reconciling the row with this source is the
spec-change process's business, not this note's.

## What cites this note

- `sim/rx/pad_ac_rppd*.request.json` / `sim/rx/run_rppd_corners.sh`: the RX
  termination bench whose `rppd` instances and window members trace their
  tolerance values to the figures above.
- The dated record that run writes under `sim/rx/records/`.
