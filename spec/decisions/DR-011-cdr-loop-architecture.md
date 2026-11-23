# DR-011: CDR loop architecture: second-order loop with a fractional integral path

- **Status**: proposed
- **Date**: 2026-11-12
- **Decided by**: builder (issue #125); acceptance needs the operator

Records are append-only. This record does not edit DR-007, DR-009 or DR-010. It
states that **DR-009's proposed fix (KP = 8, KI = 0) was not adopted** (operator
ruling 2026-11-11 on #105, "let's try to do better") and that **DR-009's
attribution is kept**: at the RTL gain (KP = 16, KI = 1) the CDR's own dither
closes the 1e-12 eye, and no single unfitted input rescues it. No ratified row
(R11, R12, R13, R15) is relaxed or re-graded. **Every figure here is simulated
(behavioural bang-bang model) or extrapolated (dual-Dirac wall fit). None is
measured.** Raw output: `spec/decisions/DR-011-output.txt` (`link_bench.py
r15|r12|r11|r13 --corners full`, one block per candidate, and
`link_sensitivity.py --section arch`). `rtl/` is unchanged.

## Context

DR-009's KP = 8, KI = 0 passes at one point: KP = 6 fails the R12 mask, KP = 12
leaves +0.002 UI, there is no integrator so +-500 ppm slips, and -300 ppm lock
takes 16 416 words. The ruling asks for a loop that passes with room on both
sides. Candidates were run through the unchanged benches on all 27 corners.
The model options are in `sim/bench/cdrmodel.py` (`ArchFilter`, `vote`,
`digital_delay`, `pi_shift`) and exposed as `link_bench.py` flags; with every
option off the model reproduces DR-009 bit for bit (test
`test_arch_defaults_reproduce_dr009`).

## Candidates (baseline inputs, 27 corners; `DR-011-output.txt`)

R15 width = worst 1e-12 width of 27 (extrapolated). R12 = `link_bench.py r12`
against the mask, 27 corners. Slips = R13 run, 1e6 UI, +-300 (ratified) and
+-500 ppm (stretch, reported not graded). Lock = words from 0.4 UI at 0 / +300 /
-300 ppm (R11 definition).

| # | Candidate | R15 width | R12 mask | slips +-300 / +-500 | lock (words) |
|---|---|---|---|---|---|
| 0 | RTL KP = 16, KI = 1 | fails 27/27 | below mask 27/27 | 0 / 0 | never locks (>35 000) |
| 1 | DR-009 KP = 8, KI = 0 (baseline) | +0.200 UI | meets 27/27 | 0 / **all words slip** | 108 / 419 / 16 416 |
| 2 | **KP = 8, KI = 1, 6 integral fraction bits, integral updated every 16 words** | **+0.205 UI** | **meets 27/27** | 0 / **0** | **104 / 264 / 155** |
| 3 | Shorter latency, RTL gain (digital 7 to 3 words) | +0.180 UI | **below mask 6/27** (30 MHz: 0.11 vs 0.15 UIpp, bcs corners) | 0 / 0 | 49 / 85 / 39 |
| 4 | Sign (majority) vote, KP = 8 or 16, KI = 0 | +0.34 UI | not run (see below) | every word slips at +-300 | 200-385 / never / never |
| 5 | Finer PI step (1/256 UI) | no change (rms 0.0283 vs 0.0284 UI) | n/a | as 1 / 2 | as 1 / 2 |
| 6 | Gear shift (24, 2 for 2000 words, then 8, 1) on 2 | as 2 | n/a | 0 / 0 | 59 / 83 / 46 |

Reading, by candidate:

- **2 (recommended).** The integral path carries the ppm offset while KP stays
  at the dither-friendly value. The integral gain is 1/64 LSB per vote, about
  64 times smaller than the RTL's KI = 1. Dither equals DR-009's (rms 0.0281 UI),
  the eye is +0.205 UI, +-500 ppm holds with no slip, and lock from 0.4 UI takes
  under 300 words in both directions (DR-009: 16 416 at -300 ppm).
- **What each part does** (section E1): the **fractional bits are essential**.
  With KI = 1 and no fraction bits (RTL resolution) the loop is unstable
  (rms 6.8 UI, slips). **Decimation is not needed in the model**: updating the
  integral every word (+0.198 UI), every 16 (+0.205) or every 64 (+0.202) gives
  the same result. It is kept only as a hardware choice (the integral adder runs
  at 1/16 of the word rate), not as a result.
- **3, shorter latency.** Strongest single lever on dither, as DR-009 found,
  and it fixes lock, but at the RTL gain it still fails the R12 mask at 30 MHz
  in 6 corners. Combined with 2 at 4 digital words the width is +0.323 UI. The
  pipeline is 7 words (DR-007 delay table, from DR-006); cutting it to 3-4 is a
  restructure with a timing cost this record does not assess. Not recommended
  as the fix, listed as the margin lever if the analog delay turns out larger.
- **4, sign vote** fails on slew: +-1 per word cannot follow +-300 ppm without an
  integrator. KP = 16 with the integral path of 2 holds ppm but fails the R12
  mask at 100 kHz (peak 10.7 UI) and locks in 3 238 words. Only KP 8 and 16 were
  tried; a larger KP was not. Adaptive PD gain (transition-density) was not
  modelled; it needs a PD model the benches do not have.
- **5, finer PI step** does nothing in this model because dither is set by loop
  gain and latency, not by PI quantisation. Its cost (more PI control bits,
  interpolator linearity) is not assessed. Rejected.
- **6, gear shift** shortens lock from about 260 to about 80 words but 2 already
  locks in under 300; it costs a lock detector or timer. Not recommended.

## Recommended loop and its passing region

**KP = 8, KI = 1, integral accumulator with 6 fractional bits (frequency step
1/64 LSB per vote), integral path updated every 16 words, FMAX = 1023 unchanged.**

Region (section E2, E4; a point passes when width > 0 in 27/27 corners, no slip
at +-300 ppm, 100 kHz / 15 UIpp peak within half the no-CDR-jitter eye, and lock
under 20 000 words; "margin" adds width >= 0.10 UI, a threshold of this record,
not a spec row):

- **Eye side**: KP 5 to 10 pass with margin at every integral gain tested up to
  1/64 per vote (frac 6). Width falls with KP: +0.328 (KP 5), +0.257 (7), +0.205
  (8), +0.152 (9), +0.103 (10), +0.003 (12). KP = 12 passes without margin and
  KP = 16 fails (27/27).
- **Slew side** (E4, slip-free SJ bound over the R12 mask amplitude, worst of
  0.1 to 10 MHz): KP 5 0.94x (slips at the 1 MHz mask), 6 1.11x, 7 1.25x, **8
  1.36x**, 9 1.47x, 10 1.58x, 12 1.80x. The weakest point is 0.3 to 1 MHz.
  DR-009's own setting is 1.11x (at 100 kHz).
- **Integral gain**: frac 3 to 8 (1/8 to 1/256 per vote) all pass with margin at
  KP 7 to 10; at frac 10 or more with KP below 8 the integral is too slow to
  help at 100 kHz and the mask fails (KP 6, frac 8: peak 0.52 UI at the mask).
- Overall, **KP 7 to 10 by frac 3 to 8** passes with margin and with 1.25x
  slew or better: 16 grid points, a factor 1.4 in KP and 32 in integral gain.
  KP = 8, frac = 6 is inside it, not at its centre: KP = 9 balances slew (1.47x)
  against eye (+0.152 UI) more evenly; KP = 8 was chosen for the larger eye
  (+0.205 UI) while keeping 1.36x slew. The implementation issue can move to
  KP = 9 without leaving the region.

**Weakest margin**: slew, 1.36x the mask amplitude at 0.3 MHz (slip-free bound
6.78 UIpp vs 5.00). The R12 bench itself reports 6.66 at 0.3 MHz and 1.50 at
1 MHz because its amplitude grid is coarse; the bisection in E4 gives 2.14 UIpp
at 1 MHz.

Sensitivity to the unfitted inputs (E3, same ranges as DR-009 section A; all
27 corners; verdict includes lock time):

| Input | 2nd-order (rec.) worst width | DR-009 KP 8, KI 0 |
|---|---|---|
| baseline | +0.205 UI | +0.202 UI |
| PD decision noise 0 / 0.01 / 0.03 / 0.05 UI | +0.350 / +0.156 / +0.295 / +0.324, all pass | eye same; **lock fails** (-300 ppm: 32 790 words at 0.01 and 0.05; +300: 39 950 at 0) |
| analog delay 0 / 2 / 3 / 5 words | +0.259 / +0.149 / +0.098 / **-0.007** | +0.257 / +0.147 / +0.097 / **-0.007** |
| RJ at grid floor (0.008 UI), DJ 0 | +0.317 | +0.313 |
| sampler noise 1 / 4 mV | +0.209 / +0.164 | +0.206 / +0.161 |
| sampler offset 5 / 10 mV | +0.160 / +0.114 | +0.157 / +0.111 |

The margin is therefore not owed to one placeholder for noise, RJ, DJ or
sampler. It **is** owed to the analog delay: the second-order loop buys no
delay tolerance (the eye closes at analog delay 5, loop delay 12, as in
DR-009). The second-order loop's gain over DR-009 is on frequency offset, lock
time, no dependence on PD noise to lock, and slew at 100 kHz (2.31x vs 1.11x),
not on dither or delay.

## Not modelled (stated, not hidden)

- PI nonlinearity (INL/DNL), supply and clock jitter, PD metastability. The
  model has a 1/64 UI PI step but ideal step sizes.
- The PD decision noise (0.02 UI), analog delay (1 word), sampler noise and
  offset, RJ and DJ are **unfitted assumptions**; none has a transistor-level
  record. Fitting them is separate work. Fit validation on held-out corners
  (DR-002 step 3) is still not done.
- PVT enters only through the eye (the 27 latch/CTLE fits); the loop model has
  no per-corner input.
- Costs are estimates for sizing only: the frequency register grows from 11 to
  17 signed bits (FMAX 1023 at 6 fraction bits), plus a vote accumulator
  (about 10 bits) and a 4-bit decimation counter. These change the committed
  synthesis and P&R records, so they need regeneration.
- DR-007's 0.05 UI criterion is not used (DR-010).

## Decision (proposed)

1. Adopt the second-order loop of candidate 2 as the architecture: **KP = 8,
   KI = 1 with 6 integral fraction bits, integral decimated by 16** (parameters
   to be confirmed inside the region above by the implementation issue).
2. DR-009's KP = 8, KI = 0 is not adopted; its attribution stands.
3. `rtl/` and the synthesis and P&R records are not changed here. The
   implementation issue is filed at `loom:triage` and cites this record.
4. The model options are what-ifs; the benches still read the RTL value by
   default and still report the RTL loop as failing until the RTL change lands.

```decision
{
  "question": "Accept DR-011's second-order CDR loop (KP = 8, KI = 1, 6 integral fraction bits, integral updated every 16 words) as the architecture for the RTL change?",
  "context": "Simulated, not measured. In all 27 corners it holds the 1e-12 eye (+0.205 UI), meets the R12 mask, has no slip at +-300 or +-500 ppm and locks in under 300 words; the weakest margin is slew, 1.36x the mask at 0.3 MHz. The unfitted analog delay still owns the eye margin.",
  "options": [
    {"id": "a", "label": "Accept the second-order loop (candidate 2)",
     "why": "Only candidate that passes R12, R15 and R13 with +-500 ppm and fast lock at once; costs a wider frequency register and an RTL and synthesis regeneration."},
    {"id": "b", "label": "Accept it and also open the latency cut (digital 7 to 4 words)",
     "why": "Widens the eye to +0.323 UI and buys analog-delay tolerance, but needs a timing restructure not assessed here; worse than (a) because it adds an unscoped change."},
    {"id": "c", "label": "Return DR-009's KP = 8, KI = 0 to consideration",
     "why": "Smallest RTL change (parameters only); worst of these because it slips at +-500 ppm, locks in 16 416 words at -300 ppm and has 1.11x slew margin, the cliff the ruling rejected."}
  ],
  "recommended": "a",
  "context_links": ["#125", "#105", "#102", "#106"]
}
```
