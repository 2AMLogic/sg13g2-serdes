# DR-010: CDR loop analysis corrected: noise-free columns were a 1-vote loop

- **Status**: proposed
- **Date**: 2026-11-11
- **Decided by**: builder (issue #106); ratification needs a human or Champion

Records are append-only. This record **supersedes the conclusions of DR-007**
(delay budget, the 0.05 UI criterion result, "L <= 10", "the 7-clock loop
passes") and does not edit DR-007 or `DR-007-output.txt`. It does not change the
ratified spec (R11, R12, R13, R15), RTL, KP/KI, or the delay inputs. **Every
number is simulated. None is measured.** Raw output of the corrected script:
`spec/decisions/DR-010-output.txt` (`python3 -I scripts/cdr-loop-analysis.py`).

## Context

DR-009 found that `simulate()` in `scripts/cdr-loop-analysis.py` formed
`s = e + (rng.normal(0, sigma_lsb, nt) if sigma_lsb else 0.0)`. With no noise
`s` is a scalar, so `np.sum(np.sign(s))` is one vote per word instead of `nt`.
Both noise-free columns of DR-007 (all-16, Bin(16,.5)) were a 1-vote loop, a
~16x (all-16) or ~8x (Bin) weaker correction than intended. The noisy column
draws `nt` samples and was correct.

## Fix

`simulate()` now uses `np.zeros(nt)` for the noise-free term, so `nt` votes are
summed. The noisy path, the linearised g_max table and every parameter are
unchanged (the g_max table and the noisy column in `DR-010-output.txt` are
identical to DR-007's).

## Corrected results (simulated, +300 ppm, KP=16 KI=1, peak |e| in UI)

| L | all-16 (DR-007 -> corrected) | Bin(16,.5) (DR-007 -> corrected) | Bin + 3 % noise (unchanged) | slip |
|---|---|---|---|---|
| 2 | 0.0120 -> 0.0721 | 0.0120 -> 0.0600 | 0.0447 | no |
| 4 | 0.0132 -> 0.1503 | 0.0132 -> 0.1053 | 0.0758 | no |
| 6 | 0.0184 -> 0.2464 | 0.0190 -> 0.1561 | 0.1426 | no |
| **8 (7 digital + 1 analog)** | 0.0291 -> **0.3664** | 0.0293 -> **0.2309** | 0.2237 | no |
| 9 | 0.0407 -> 0.4568 | 0.0407 -> 0.2941 | 0.2690 | no |
| 10 | 0.0455 -> 0.5625 | 0.0462 -> 0.3867 | 0.3381 | YES (all-16) |
| 11 | 0.0623 -> 0.7570 | 0.0623 -> 0.5101 | 0.4990 | YES |

-300 ppm at L = 8: 0.2268 UI (DR-007: 0.0296). 0 ppm: 0.0000 UI.

Cross-check, `sim/bench/cdrmodel.py` (RTL `CdrFilter`, PRBS-31 transitions,
no vote noise, analog delay 1, +300 ppm, last 60 000 of 120 000 words): peak
0.2373 UI, sd 0.109 UI. The corrected Bin(16,.5) column gives 0.2309 UI (sd
0.109). They agree to about 3 %; the residual is the data pattern (PRBS
transition counts vs i.i.d. Binomial). Not adjusted.

## Which DR-007 conclusions survive

- **Withdrawn**: "L = 8 passes at 0.029 UI" (0.231 UI corrected, 0.37 UI with
  all 16 sites voting); "the 7-clock digital loop passes the criterion"; "allowed
  total delay L <= 10" and "allowed digital delay <= 9" (with the stated
  criterion no L from 2 to 14 passes; max contiguous L is None); "two clocks of
  headroom".
- **Withdrawn as a derived number, kept as text**: the 0.05 UI criterion was the
  builder's stated choice, never ratified, and DR-007 derived the budget from
  it. It is not a spec row and is **not relaxed here to make results pass**. At
  KP = 16, KI = 1 even L = 2 gives 0.060 UI, so the criterion cannot be used to
  allocate delay at this loop gain. DR-009 re-derives the budget from slips and
  the 1e-12 eye width instead; use that, not a peak-error threshold on this
  script.
- **Survive**: the linearised g_max table (L = 8: 0.0094 votes/LSB); the noisy
  column and its observation that the loop is thin at 3 % UI rms noise
  (0.22 UI at L = 8); the model limits (word-rate abstraction, no PI
  nonlinearity, sampler metastability, supply or clock jitter, channel ISI);
  the unresolved analog-delay assumption; the single digital-delay value 7 from
  DR-006.
- **Gain that is now consistent with DR-009**: the effective noise-free loop
  gain at nt votes per word is several times g_max at L = 8, so the loop
  limit-cycles hard (and slips for L >= 10 noise-free), matching DR-009's
  finding that KP = 16 dithers the eye closed.

## Consequences and limits

- The statement "no latency-cut record is needed" in DR-007 no longer rests on
  this analysis. The delay budget is owned by DR-009's slip and 1e-12-width
  analysis and its proposed KP/KI change; this record only withdraws DR-007's
  numbers and does not propose a gain.
- `sim/bench/linkcore.py` regex-parses DR-007's delay table (`| Digital | **7**`,
  `| Analog... | **1** | **ASSUMED`). DR-007 is untouched, so that parser keeps
  working. The delay table (7 digital, 1 assumed analog) is not changed by this
  record. Moving that parser to a newer source is a separate step.
- Simulated / analytical only. Not link evidence.
