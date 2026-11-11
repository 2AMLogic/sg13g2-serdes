# DR-009: CDR dither closes the 1e-12 eye; proposed fix KP=8, KI=0

- **Status**: proposed
- **Date**: 2026-11-11
- **Decided by**: builder (issue #102); ratification needs a human or Champion

Records are append-only. This record does not supersede DR-007 and does not
edit it; it records a defect in DR-007's script (below) and a loop setting that
DR-007 did not consider. It does not relax any ratified spec row (R11, R12, R13,
R15). **Every figure is simulated (behavioural) or extrapolated (dual-Dirac
wall fit). None is measured.** Raw output: `spec/decisions/DR-009-output.txt`
(`link_bench.py r12|r15|r11|r13 [--kp 8 --ki 0]`, `link_sensitivity.py`).

## Context

PR #100's benches report that with the CDR's own dither included the 1e-12 eye
is closed: `link-r15-method` gives recovered-clock error rms 0.1053 UI / peak
0.2188 UI and 27/27 extrapolation failures (bathtub floor 1.3e-5..2.0e-5);
`link-r12-jtol` gives 0.00 UIpp tolerance at every frequency in all four edge
corners. The eye without CDR jitter is +0.35..+0.39 UI, so the loop, not the
channel, closes it.

## Attribution (one unfitted input at a time; `link_sensitivity.py`, 27 corners)

Baseline: RTL KP=16 KI=1, delay 7+1, PD noise 0.02 UI, sampler 2 mV / 0 mV offset.
Full table in the output file, section A. Summary:

| Input changed (unfitted) | CDR rms / peak (UI) | 1e-12 eye, worst of 27 |
|---|---|---|
| baseline | 0.105 / 0.203 | fails 27/27 |
| PD decision noise 0.01 / 0.03 / 0.05 UI | 0.107 / 0.101 / 0.090 | fails 27/27 |
| PD decision noise 0 (at 0 ppm) | 0 / 0 (loop sits still in its dead zone) | +0.350 UI, 27/27 extrapolate |
| analog delay 0 / 2 / 3 words | 0.081 / 0.139 / 0.183 | fails 27/27 |
| RJ and DJ off (eye side) | unchanged | fails 27/27 (floor 8.6e-6) |
| sampler noise 1 / 4 mV, offset 5 / 10 mV | unchanged | fails 27/27 |

Reading: no single unfitted input rescues the eye, so the closure is not an
artefact of one placeholder. The dither is set by the loop gain acting on
decision noise. With noisy votes the bang-bang detector is linearised to
roughly 0.8*k/sigma votes/LSB (k = transitions per word, sigma = decision
noise), about 0.04 at k = 8 and 0.02 UI, which is several times the linear
stability limit DR-007 tabulates for L = 8 (0.0094). The loop therefore
limit-cycles at KP = 16. More PD noise lowers that gain and slightly reduces
the dither, which is why raising the noise does not help and lowering it does
not either. The noise-free 0 ppm row is a dead-zone artefact, not a credible operating point: at +300 ppm noise-free the peak is still 0.23 UI. Analog delay is
the strongest single sensitivity (rms 0.081 -> 0.183 UI for 0 -> 3 words) but
even zero analog delay does not open the eye at the RTL gain. What is
untested: PI nonlinearity, supply and clock jitter, real PD metastability.

Loop gain sweep (section B, baseline inputs): KI = 1 with KP < 10 is unstable
(rms > 0.2 UI, slips); KP 12..32 with KI = 1 gives rms 0.105..0.158 UI and no
eye. KI = 0 has no such instability; the dither falls with KP (0.028 UI rms at
KP = 8, 0.066 at KP = 16). The constraint from below is slew: KP = 4 cannot
hold +-300 ppm (20000 slips), KP = 6 holds +-300 ppm but has peak error
1.67 UI at the R12 mask point (15 UIpp, 100 kHz).

## Grading rule check (R12)

The bench rule ("peak error <= half the 1e-12 eye width of the no-CDR-jitter
eye") compares the maximum of a random dither (about 3.8 sigma over the run)
with a 1e-12 width (about 7 sigma), so for the random part it is
over-conservative against the dual-Dirac treatment R15 uses. It is **not** what
closes the eye: the R15 statistical treatment, which adds only the rms, fails
the same baseline in all 27 corners, and both rules pass the proposed setting
below. The spec row ("SJ amplitude vs frequency to BER 1e-12") is not changed;
the rule is kept, with one fix: the swept amplitude grid is geometric, so the
first grid point above a mask value could mask a pass or fail at the mask
itself. `link_bench.py r12` now always adds the mask amplitude to each
frequency's grid. This changes the graded amplitude at exactly the mask only.

## DR-007 defect found (not edited here)

`scripts/cdr-loop-analysis.py` `simulate()` forms `s = e + (rng.normal(0,
sigma_lsb, nt) if sigma_lsb else 0.0)`; with no noise `s` is a scalar and
`np.sum(np.sign(s))` is one vote per word, not `nt`. DR-007's two noise-free
columns (all-16, Bin(16,.5)) are therefore a 1-vote loop, and its
"L = 8 passes at 0.029 UI" is an artefact. The RTL-filter model of this repo
(`cdrmodel.py`, PRBS-31 transitions, RTL `CdrFilter`) gives a noise-free
+300 ppm peak of 0.23 UI at L = 8 for KP = 16 KI = 1, and its noisy column
(0.22 UI) agrees with DR-007's noisy column (0.2237 UI). Consequence: DR-007's
0.05 UI criterion and its "L <= 10" were derived from the defective column.
This record does not reuse that criterion; the delay budget is re-derived below
from the quantity that matters (slips and the 1e-12 width). Filed as #106.

## Proposed fix (parameter-only)

**KP = 8, KI = 0** in `rtl/serdes_cdr_filter.v` (module parameters; proportional-
only filter; `FMAX` becomes irrelevant). Model results (`--kp 8 --ki 0`):

| Check | RTL KP=16 KI=1 | KP=8 KI=0 |
|---|---|---|
| R15: recovered-clock rms / peak | 0.1053 / 0.2188 UI | 0.0286 / 0.0625 UI |
| R15: 1e-12 width, 27 corners | 27/27 FAILED | +0.200 UI worst (0 failures) |
| R12: 4 edge corners vs mask | BELOW MASK (0.00 everywhere) | meets (15 / 5 / 1.5 / 0.5 / 0.15 UIpp at 0.1/0.3/1/3/10 MHz; 0.23 at 30, 100 MHz) |
| R13: +-300 ppm, 1e6 UI | 0 slips | 0 slips (peak 0.082 / 0.087 UI) |
| R11: lock from 0.4 UI, 0 / +300 / -300 ppm | locks | locks (108 / 419 / 16416 words), 0 slips |
| Delay budget (section D): L = 7..11 | closed for all L | width +0.257 / +0.202 / +0.147 / +0.097 / +0.042 UI; L = 12 -0.007 UI |
| Delay at L = 8 + 2 (analog 3) | n/a | +0.097 UI |

Allowed delay re-derived: with this setting the worst-corner 1e-12 width stays
positive up to L = 11 (analog delay up to 4 words), so DR-007's L <= 10 holds
with margin; the baseline loop has no eye at any L in 7..14.

## Limits (stated, not hidden)

- **Thin slew margin.** R12 passes at 100 kHz / 15 UIpp with peak error 0.113 UI;
  KP = 6 fails it (1.67 UI). The cliff is between KP = 6 and 8; KP = 7 was not
  run. KP = 8 is the smallest value tried that holds the mask. Higher KP
  trades eye for slew: KP = 12 gives +0.002 UI width.
- **Frequency headroom.** With no integrator the loop holds +-300 ppm but
  slips at +-500 ppm (KP = 8 and 7 both, 50000-word runs). R13's ratified
  target (+-300) is met; the stretch column (+-500) is not. The clock
  requirement (`spec/clock-requirement.md`) asks +-100 ppm accuracy.
- **-300 ppm lock is slow** (16416 words, about 26 us) from a 0.4 UI offset.
- Every input behind the margin is an UNFITTED ASSUMPTION (PD noise 0.02 UI,
  analog delay 1, sampler noise/offset, RJ, DJ); none has a transistor-level
  record. Margin under those inputs is not evidence of closure. Fit validation
  on held-out corners (DR-002 step 3) is still not done.
- A noise-free proportional bang-bang loop would rely on PD decision noise for
  linearisation; the model tracks noise-free (+300 ppm peak 0.12 UI), but PI
  nonlinearity and real sampler behaviour are not modelled.
- If the real analog delay, PD noise or PI step differ enough, the attribution
  may change; re-run `link_sensitivity.py` when those records exist.

## Decision

1. Propose KP = 8, KI = 0 (parameter-only) as the spec-conformant fix; no
   ratified row is relaxed, and R12/R15 remain graded as simulated/extrapolated.
2. The RTL parameter change is **not** made in this PR: it invalidates the
   committed synthesis and P&R records and needs their regeneration; filed as
   #105 (`loom:triage`) citing this record. `rtl/serdes_cdr_filter.v`
   and `rtl/tests/serdes_ref.py` are untouched here.
3. The `--kp/--ki` flags on `link_bench.py` are model what-ifs; the benches
   still read the RTL value by default and still fail until the RTL change
   lands.
4. DR-007's analytic script is defective (above); ratification of this record
   should not rely on DR-007's 0.05 UI criterion.
