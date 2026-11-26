# DR-015: TX mux clock swing

- **Status**: proposed
- **Date**: 2026-11-10
- **Decided by**: builder (issue #98); ratification is an operator step

## Context

The `mux2to1_cml` bench drives `ckp` and `ckn` in antiphase from 0.4 to
0.8 V on each node (0.4 Vpp per side, 0.8 Vpp differential). The sibling
specs cover different interfaces from the mux's AC-coupled clock inputs.
The sweep tests how the mux output responds to the assumed input swing.

## Options considered

1. Keep the 0.4 V per side bench, say nothing: a mismatch nobody wrote down.
2. Sweep the per-side clock swing on the existing cell and write down what the
   output does (chosen). Sweep: 0.1, 0.2, 0.3 V per side at a fixed 0.6 V
   centre, same 45 corners (5 process x 3 supply x 3 temperature) as the
   default record, on the batch fleet (klt 0.9.0): record
   `sim/tx/records/20261110-232100-f7361f7-ckswing/`. The 0.4 V point is the
   existing record `20261110-224611-4092fc2-mos`, not repeated.
3. Size a clock buffer here: out of scope (no PLL/VCO/buffer design in this repo).

## Decision

**Result.** The mux output differential peak-to-peak keeps rising with clock
swing across the whole sweep, including 0.3 V to 0.4 V per side; no swept swing
saturates it. **A minimum swing at which the mux is "fully switched" was not
found, and is not claimed.** Output peak-to-peak (mV, simulated, sizing
evidence, not a measurement):

| corner | 0.1 V/side | 0.2 | 0.3 | 0.4 (existing record) |
|---|---|---|---|---|
| tt_typ 1.20 V 27 C | 81 | 211 | 382 | 491 |
| ff_bcs 1.32 V -40 C | 262 | 531 | 602 | 619 |
| ss_wcs 1.20 V -40 C | 5.1 | 16 | 43 | 104 |
| ss_wcs 1.08 V 27 C | 2.4 | 5.5 | 12.7 | 31 |
| ss_wcs 1.08 V -40 C | 0.1 | 0.1 | 0.5 | 4.1 |

**Requirement stated** (per node and differential, with load): the mux clock
input needs **at least 0.4 V per side (0.8 V differential peak-to-peak)**,
centred near 0.6 V, into the mux's clock squarers (AC-coupled, self-biased) and
the load of that cell. This is a **lower bound, not a sufficient figure**: at
0.4 V per side the output at `ss_wcs` is 4.1 mV (1.08 V, -40 C) and 31 mV
(1.08 V, 27 C), i.e. **not switched**. That is recorded as a failing
requirement at the slow corner; the bench was not adjusted to hide it. The
needed swing at the slow corner is above 0.4 V per side and was not swept
(scope: the sweep answers whether 0.4 V is generous; it is not).

**Comparison at the revisions pinned in [the clock requirement](../clock-requirement.md).**

| Sibling | Specified interface and load | Does it establish 0.8 Vpp differential at the 5 GHz mux inputs? |
|---|---|---|
| `sg13g2-vco` | Row 7 targets ≥ 0.40 Vpp differential across the unbuffered tank, equivalent to 0.20 Vpp per node for equal antiphase swings. The grading load is the tank alone. [VCO row 7](https://github.com/2AMLogic/sg13g2-vco/blob/2f8af57623c8098bbb12b7903616f00f10c818bc/spec/target-spec.md#L126) | No. The tank target is half the mux lower bound, and adding the squarers changes the load. |
| `sg13g2-pll` | Row 14 proposes single-ended buffer levels of VOH ≥ 0.9 × VDD and VOL ≤ 0.1 × VDD into ≤ 50 fF. The recorded band tops out at 1562 MHz. [PLL rows 1 and 14](https://github.com/2AMLogic/sg13g2-pll/blob/3484d5ed5c25fb65a6694b8ca9254b4b08417a9e/spec/target-spec.md#L79-L92) | No. The levels apply to one pin, and 5 GHz is outside the recorded band. There is no differential swing specification at the squarers. |
| `sg13g2-lc-pll` | I6 imports the VCO's 0.40 Vpp differential tank target. The first stage and its routing may add at most 2.1 fF differential at 5 GHz. [LC PLL load budget](https://github.com/2AMLogic/sg13g2-lc-pll/blob/0508e2fdb9c0ab2970716d5f39f587140bc1b261/spec/target-spec.md#L42-L70) | No. Q1 leaves the output buffer open, and the spec gives no delivered swing into the squarers. [LC PLL Q1](https://github.com/2AMLogic/sg13g2-lc-pll/blob/0508e2fdb9c0ab2970716d5f39f587140bc1b261/spec/target-spec.md#L191-L192) |

## Consequences

- `spec/clock-requirement.md` "Level / load" row gains this requirement.
- The bench stays at 0.4 V per side; `sim/tx/make_tb.py` gains a swing
  parameter defaulting to today's value (default decks byte-identical), and the
  sweep decks use a separate `tx_mosck_` prefix so `sim/tx/run_sizing.sh mos`
  and its record are unchanged.
- The mux does not close at `ss_wcs`/1.08 V at 0.4 V per side. Whether a larger
  swing closes it, or the squarer/tail sizing must change, is open work on the
  mux cell, not a clock-provider question alone.
- The three sibling issues cite this proposal by its draft filename,
  `DR-009-mux-clock-swing.md`. Its permanent reference is DR-015.
  [VCO #319](https://github.com/2AMLogic/sg13g2-vco/issues/319) · [PLL #312](https://github.com/2AMLogic/sg13g2-pll/issues/312) · [LC PLL #206](https://github.com/2AMLogic/sg13g2-lc-pll/issues/206)
