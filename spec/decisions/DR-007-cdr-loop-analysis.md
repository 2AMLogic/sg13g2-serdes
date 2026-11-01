# DR-007: CDR loop delay budget (analytical, word-rate model)

- **Status**: proposed
- **Date**: 2026-11-01
- **Decided by**: builder (issue #62); ratification needs a human or Champion

Records are append-only: a ratified record is never rewritten; a new record
says what it supersedes. This record does not supersede any record and does not
change the ratified spec (R11 half-rate bang-bang, R13 +-300 ppm, 16:1 /
625 MHz). **Every number below is analytical / simulated. None is measured.**

## Context

DR-006 pipelined the digital partition for the 1.6 ns word clock. That put 7
word clocks of digital delay in the CDR loop (RX register 1, phase detector 3,
filter to `pi_code` 3). A bang-bang loop with a lot of latency limit-cycles
harder and can lose lock, and nothing yet checked whether 7 is acceptable. The
loop is the named link risk (CLAUDE.md). This record sets the allowed delay and
checks 7 against it.

## Model

Reproduced by `scripts/cdr-loop-analysis.py` (numpy only, ~20 s,
`python3 -I scripts/cdr-loop-analysis.py`). Raw output of the run recorded here:
`spec/decisions/DR-007-output.txt`.

- Word-rate (625 MHz) loop of `rtl/serdes_cdr_filter.v`: `f[n+1] = sat(f[n] + KI*u[n])`,
  `phi[n+1] = phi[n] + KP*u[n] + f[n]`, `pi_code = phi[13:7]`.
- **KP = 16, KI = 1, FMAX = 1023** (phase LSB per vote / freq LSB per vote).
- Units: 1 phase LSB = 1/16384 clock period = 1/8192 UI (half-rate); half a UI
  = 4096 LSB; one word = 16 UI, so 1 ppm = 0.131 LSB per word.
- `u[n]` is the PD vote sum measured L-1 words earlier. **L = total delay in
  word clocks** from a data word to the `pi_code` that reflects it = digital +
  analog.
- Two views: (a) linearised stability, largest effective PD gain g (votes/LSB)
  for which `(z-1)^2 z^(L-1) + g(KP(z-1)+KI) = 0` stays inside the unit circle;
  (b) time-domain bang-bang simulation at +300 ppm (R13), 120 000 words,
  statistics over the last 60 000 (after lock).
- Vote statistics: all 16 sites vote (best case), or each site votes with
  probability 1/2 (`Binomial(16, 0.5)`, a transition-density-0.5 data pattern),
  and the latter again with 3 % UI rms noise on each decision.

## Delay inputs

| Part | Clocks | Source |
|---|---|---|
| Digital | **7** | DR-006: RX reg 1, PD 3, filter -> `pi_code` 3. **Single source of truth for the DR-002 statistical CDR model: it must read this value and cite this record.** |
| Analog (PI, sampler, deserialiser) | **1** | **ASSUMED, not traced.** No PI or sampler delay record exists yet. Sensitivity to this value is in the table below. |

## Margin criterion

Chosen before the run: peak phase error with `Binomial(16, 0.5)` votes, no
noise, at +300 ppm, must stay **<= 0.05 UI** and the loop must not slip (error
reaching 0.5 UI). Why: 0.05 UI of deterministic limit-cycle error is a
sizeable but bounded share of the jitter budget, and it is a clean separator.
The error grows slowly with delay up to 9 and then climbs steeply
(0.046 -> 0.062 -> 0.082 -> 0.14 -> 0.28 -> 1.0 UI for L = 9..14), so the
conclusion is not sensitive to the exact threshold within 0.04..0.06 UI.

## Results (simulated)

Linearised g_max (votes/LSB): L=2 0.0622, 4 0.0256, 6 0.0148, 8 0.0094,
10 0.0061, 12 0.0036, 14 0.0017. Peak |e| in UI, +300 ppm:

| L | all-16 votes | Bin(16,.5) | Bin + 3 % UI noise | slip | criterion |
|---|---|---|---|---|---|
| 2 | 0.0132 | 0.0132 | 0.0626 | no | pass |
| 4 | 0.0135 | 0.0135 | 0.1118 | no | pass |
| 6 | 0.0241 | 0.0241 | 0.1822 | no | pass |
| 7 | 0.0291 | 0.0293 | 0.2237 | no | pass |
| **8 (7 digital + 1 analog)** | 0.0407 | **0.0407** | 0.2690 | no | **pass** |
| 9 | 0.0455 | 0.0462 | 0.3381 | no | pass |
| 10 | 0.0623 | 0.0623 | 0.4990 | no | fail |
| 11 | 0.0816 | 0.0817 | 0.7114 | YES (noisy) | fail |
| 12 | 0.1402 | 0.1409 | 1.2286 | YES | fail |

-300 ppm at L = 8: peak 0.0409 UI, final integrator -43; 0 ppm: 0.0000 UI.

## Decision

1. **Allowed total delay L <= 9 word clocks** under the criterion above.
   With the assumed analog delay of 1 that is **an allowed digital delay of
   <= 8 clocks**.
2. **The 7-clock digital loop passes** (L = 8: 0.041 UI peak, no slip, +300 and
   -300 ppm). KP = 16 and KI = 1 are kept; `rtl/` and its tests are unchanged
   and no latency-cut record is needed.
3. Digital delay of 7 is the single value the DR-002 statistical CDR model
   reads; when that model is filed it cites this record.

## Consequences and limits

- **Headroom is one clock.** If the real analog delay is 2 or more, L >= 9 and
  the loop is at or past the edge; at 3+ it fails. The assumed analog delay is
  the weakest link of this record and needs a PI/sampler/deserialiser delay
  record. Until then a pass here means "passes if analog <= 2 words".
- **With noise the margin is thin.** At L = 8 and 3 % UI rms decision noise the
  noise-free criterion passes but the peak error is 0.27 UI (sd ~0.13 UI), no
  slip. The 3 % figure is a placeholder, not a fitted value; the real noise
  comes from the sampler/jitter records (DR-002). Re-run the script with those
  values when they exist, and revisit if the peak approaches 0.5 UI.
- The model is a word-rate abstraction: no PI nonlinearity (INL/step), no
  sampler metastability, no supply or clock jitter, no real data patterns or
  channel ISI. The bang-bang PD gain is taken from the vote statistics, not
  from a fitted latch record. It bounds the digital contribution; it is not
  link evidence and does not replace the behavioural model fitted to
  transistor-level records (R11, DR-002).
- Everything here is simulated/analytical, never measured.
- Out of scope, unchanged: RTL pipelining (#36), P&R (#25), the behavioural CDR
  model, the PI or clock source, PVT characterisation of the analog delay.
