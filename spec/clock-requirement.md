# Clock requirement and sibling comparison

**Status: PROPOSED.** This repo has no `consumes:` edge and does not design a
PLL or VCO. This document specifies the clock the half-rate architecture
([DR-001](decisions/DR-001-architecture.md)) needs and compares it to the
sibling candidates by name and commit. It does not edit the manifest.

## Required clock

| Item | Requirement (10 Gb/s, half-rate) | Fallback | Basis |
|---|---|---|---|
| Frequency | 5.0 GHz (= line rate / 2), settable within the sibling's band | 5.0 GHz (5 Gb/s runs full-rate on the same clock) | DR-001 |
| Phases | **4**: 0/90/180/270° for the RX samplers; TX uses the 0/180° pair | same | DR-001 |
| Duty-cycle error | ≤ ±1 % of the period (≤ 2 ps at 200 ps) | ≤ ±2 % | proposal; 2 ps is 2 % UI of static DCD in the TX 2:1 mux |
| Quadrature error | ≤ ±2° (≈ 1.1 ps) | ≤ ±5° | proposal |
| Random jitter | ≤ 0.5 ps rms, integrated above the CDR high-pass corner (≈ 1 MHz) to 2.5 GHz | ≤ 0.8 ps rms | proposal: about half the ≈ 1 ps rms total-link RJ that leaves a 14σ ≈ 14 % UI budget at 1e-12 |
| Deterministic jitter (clock path) | ≤ 3 ps peak-peak (3 % UI) | ≤ 5 ps | proposal |
| Frequency accuracy | ±300 ppm tracking range (target-spec R13) | ±100 ppm | R13 |
| Level / load | differential CML levels into the clock buffer; load stated by the receiver and graded at the interface | | to be fixed with the sibling |
| Supply | separate filtered rail, ≤ 1 mV rms noise in 100 kHz–100 MHz *(proposal)* | | DR-003 |

## Sibling comparison

Read at the pinned commits named in the issue; later heads exist and were
**not diffed** (`sg13g2-vco` head `a34857e` as of 2026-10-17; the issue named
`4787248` at curation, and `sg13g2-pll` head `980748a`). Whether either band
changed since the pinned commit is therefore **unchecked**.

| Candidate | Commit | What it offers | Frequency | 4 phases | Duty/quad | Jitter | Verdict |
|---|---|---|---|---|---|---|---|
| `2AMLogic/sg13g2-vco` | `6e6e830cfebf2c79a5164c9d46ae91fa335b0f2f` | LC VCO, ratified as **targets, not met** (`spec/target-spec.md` rows 1, 4, 7): band 4.5–5.5 GHz, ≤ −105 dBc/Hz @ 1 MHz, differential swing ≥ 0.40 Vpp at the tank, **no output buffer** | **Fits** (5.0 GHz inside the band) | **Gap**: differential tank (2 phases) only | **Gap**: no duty or quadrature row | Phase-noise target implies ≈ 0.25 ps rms above 1 MHz if the noise is 1/f² (arithmetic: 2·10^(−10.5)·(1 MHz)²/1 MHz = 6.3e-5 rad², σ = 7.9 mrad = 0.25 ps at 5 GHz); this is the target, not a measurement | Frequency fits; no VCO alone provides 4 phases or a buffered clock |
| `2AMLogic/sg13g2-pll` | `880d797f4ab33655eefc5b88f7cc93c9ca48c095` | Integer-N **ring** PLL; recorded band 445.3–1562.0 MHz pre-layout (`spec/target-spec.md` row 1, DR-005), spec DRAFT | **Gap**: ceiling 1.56 GHz, 3.2× short of 5 GHz | n/a | n/a | not assessed | **Does not fit** |
| `2AMLogic/sg13g2-lc-pll` (the LC PLL canary) | `bd7e58506c65a087f953d3ecbda52bd5818e1832` (main, read 2026-10-17) | Integer-N LC PLL around the `sg13g2-vco` core; its README draft targets 5.0 GHz output, 50 MHz reference, ≤ 1 ps rms jitter 10 kHz–10 MHz (simulated), VCO output buffer "if needed" | **Fits** (draft: 5.0 GHz; full band is its stretch) | **Gap**: not stated | **Gap**: not stated | **Not comparable**: its 1 ps is integrated 10 kHz–10 MHz and mostly low-frequency; ours is RJ above the CDR corner. Its spec is DRAFT and pre-design | **Closest fit; not yet a fit** |

## Conclusion

**No sibling meets the requirement today.** The frequency fits `sg13g2-vco`
and `sg13g2-lc-pll`; the gaps are the phase count (4 vs. 2), the duty-cycle and
quadrature error (no row in either), and a buffered, specified clock output.
The closest sibling is `sg13g2-lc-pll`, which owns the VCO output buffer and
the integrated layout. This document therefore **proposes no `consumes:`
edge**; the edge becomes proposable once the requirement below is met in that
repo's ratified spec (the manifest change remains an operator decision).

At 12.5 Gb/s half-rate the clock would be 6.25 GHz, outside `sg13g2-vco`'s
band: a gap recorded for the stretch only, which shapes nothing.

## Requirement to file on the closest sibling (`sg13g2-lc-pll`)

Not filed by this change (it writes to another repository; the operator or a
later step files it). Text, generic to the interface:

> A downstream 10 Gb/s half-rate SerDes needs a 5.0 GHz clock with four
> phases (0/90/180/270°), duty-cycle error ≤ ±1 %, quadrature error ≤ ±2°,
> random jitter ≤ 0.5 ps rms integrated from ≈ 1 MHz to 2.5 GHz,
> deterministic jitter ≤ 3 ps pp, on a stated differential CML load.
> `sg13g2-vco` provides two phases and no duty/quadrature row, and the
> LC PLL draft states neither. Please state in the interface table: phase
> count and generation (divider or polyphase), duty/quadrature error, the
> buffer and its load, and jitter integrated above 1 MHz, so a `consumes:`
> edge can be evaluated.

## What this does not decide

The quadrature-generation method (polyphase filter, divide-by-2 from a 10 GHz
source, or a DLL) — that is a design choice for whichever repo owns the clock
buffer; the requirement above is on the result.
