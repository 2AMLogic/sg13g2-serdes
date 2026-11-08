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

## Sibling comparison (refreshed 2026-11-02)

Pinned current revisions. The siblings' `spec/target-spec.md` files were
compared byte-for-byte against the revisions the first draft read
(2026-10-17); the clock-relevant statements are cited from the files at the
pins below. Status of the clock table: **PROPOSED**.

| Candidate | Historical pin | Current pin | Change in the spec file |
|---|---|---|---|
| `2AMLogic/sg13g2-vco` | `6e6e830` | `2f8af57623c8098bbb12b7903616f00f10c818bc` | **None**: identical file (band row 1, phase noise row 4, no-buffer row 7 unchanged) |
| `2AMLogic/sg13g2-pll` | `880d797` | `3484d5ed5c25fb65a6694b8ca9254b4b08417a9e` | **None**: identical file (draft, band 445.3–1562.0 MHz) |
| `2AMLogic/sg13g2-lc-pll` | `bd7e585` | `0508e2fdb9c0ab2970716d5f39f587140bc1b261` | **Changed**: no `spec/target-spec.md` existed at `bd7e585` (the first draft cited its README draft). It now holds a spec RATIFIED as targets, "not met" (DR-001 in that repo) |

Each criterion is graded independently; one passing row does not make a
provider.

| Criterion | Requirement | `sg13g2-vco` @ `2f8af57` | `sg13g2-pll` @ `3484d5e` | `sg13g2-lc-pll` @ `0508e2f` |
|---|---|---|---|---|
| Frequency | 5.0 GHz | **Fit (target)**: band 4.5–5.5 GHz, row 1 | **Gap**: 445.3–1562.0 MHz recorded, pre-layout, 3.2× short | **Fit (target)**: row 1, f_out 5.0 GHz (stretch 4.5–5.5 GHz) |
| Phase count | 4 (0/90/180/270°) | **Gap**: a differential tank gives 2 phases; no row | **Gap**: not stated, band already fails | **Not stated**: no phase-count row found in the spec (my reading; the owner should confirm) |
| Duty-cycle error | ≤ ±1 % | **Gap**: no row | **Gap**: reference-input duty 30–70 % is an input, not an output spec | **Not stated** |
| Quadrature error | ≤ ±2° | **Gap**: no row | **Gap**: none | **Not stated** |
| Buffer / load | differential CML into the receiver clock buffer, load stated | **Gap by design**: ratified "no output buffer in v1"; swing ≥ 0.40 Vpp *at the tank nodes*; any added load detunes it (3 % of C_tot shifts f0 by 1.5 %) | n/a | **Open**: its Q1 says a buffer, "if needed", is designed there and supersedes the VCO no-buffer statement; load not stated |
| Jitter definition | RJ rms integrated ≈ 1 MHz–2.5 GHz, ≤ 0.5 ps (above) | **Not comparable**: a single-offset figure, ≤ −105 dBc/Hz @ 1 MHz (and ≤ −125 @ 10 MHz), method open. A single-offset target does not determine an integrated jitter without the whole spectrum | **Not assessed** | **Not comparable**: ≤ 1.0 ps rms integrated **10 kHz–10 MHz** of a locked PLL, linear model; the band excludes everything above 10 MHz that our figure includes, and includes the loop-shaped low-frequency part that a CDR tracks |
| Deterministic jitter | ≤ 3 ps pp | not stated | not stated | not stated (reference spur ≤ −50 dBc is the nearest, a different quantity) |
| Spec maturity | n/a | ratified **targets, not met** | draft | ratified **targets, not met**; pre-design |

**Withdrawn from the first draft**: the "≈ 0.25 ps rms above 1 MHz" derived
from the VCO's 1 MHz phase-noise target. It assumed the noise follows 1/f²
from 1 MHz to infinity with no floor or flicker region, which no sibling
states, and it equated a single-offset target with an integrated jitter. No
integrated figure is claimed for any sibling here.

## Conclusion

**No sibling is a complete clock provider today.** Frequency alone fits
`sg13g2-vco` and `sg13g2-lc-pll`; the four-phase output, duty-cycle and
quadrature error, a specified buffer and load, and a jitter figure on the
same definition as ours are each a gap or unstated, and none of them can be
closed by arithmetic from the siblings' numbers. Changes since the first
draft: the LC PLL canary went from README draft to ratified targets, with
the same 5.0 GHz output and the buffer question still open; the VCO and ring
PLL are unchanged. This document **proposes no `consumes:` edge and selects
no provider**; the manifest remains an operator decision, and whether the
required phases come from a divider, a polyphase stage or a different source
is open (below).

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
> ratified LC PLL targets state neither. Please state in the interface table: phase
> count and generation (divider or polyphase), duty/quadrature error, the
> buffer and its load, and jitter integrated above 1 MHz, so a `consumes:`
> edge can be evaluated.

## What this does not decide

The quadrature-generation method (polyphase filter, divide-by-2 from a 10 GHz
source, or a DLL) — that is a design choice for whichever repo owns the clock
buffer; the requirement above is on the result.
