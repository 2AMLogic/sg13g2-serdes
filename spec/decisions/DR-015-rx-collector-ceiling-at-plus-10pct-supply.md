# DR-015: RX latch and clock-buffer collector nodes brought under R3's 1.32 V at +10 % supply

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-11-23
- **Decided by**: Builder agent, issue #266 (RX half of the operator ruling on #249)

DR-NNN is the next unused number at merge time and is the permanent ID. `DR-015` is
provisional: open PRs already claim DR-014, so renumber at merge if 015 is taken.

## Context

DR-005 (TX) found that a stage with resistor loads returned to the rail, and an off-side
collector resting at the rail, cannot hold "no collector node > 1.32 V" at +10 % supply,
and said the finding applies to later rail-referenced stages. The RX per-device Vce pass
([`sim/rx/records/20261123-025159-fedf656-vce/`](../../sim/rx/records/20261123-025159-fedf656-vce/record.md),
and first seen in `20261027-022309-00c2ed7`) showed it: latch `qs1/qh1` (qn) at 1.3901 V
and `qs2/qh2` (qp) at 1.3481 V (hbt_bcs/1.320 V/125 C), clock-buffer `qq2a/qq2b` (b270, b90)
at 1.3239/1.3236 V (hbt_bcs/1.320 V/-40 C). Every Vce stayed under BVCEO 1.4 V; only
collector-to-ground exceeded R3. The operator ruled on #249 (option `a`): keep R3 as
written and redesign the over-limit nodes. Option 3 of DR-005 (restate R3 on Vce stress)
is therefore not taken, and R3 is unchanged.

Cause of the latch overshoot, measured at hbt_bcs/1.32 V/125 C before choosing the fix:
when the clock hands current from one pair to the other, the cross-coupled hold pair's
base-collector capacitance carries the 0.45 V swing of one collector (`qp`, 0.73 -> 1.18 V)
into the other (`qn`, resting at the rail with no load current) and lifts it about 70 mV
above the rail (1.30 -> 1.35 V in the 2-3 ns window; 1.39 V peak over the whole run). The
clock-buffer overshoot is the same effect, 4 mV.

## Options considered

1. **Series resistor in the load return** (DR-005 option 1): the load pair returns to a
   node `vl` a few tens of mV below the rail through one shared series R. The off-side
   collector rests at `vl`, so the kick starts lower. Because one side of the pair always
   conducts, the shared R drops a nearly constant I x R and costs little differential
   swing.
2. **Diode-dropped return.** A Vbe (~0.8 V) drop is the whole latch swing; rejected on
   headroom.
3. **Restate R3 on Vce.** Operator ruled against.
4. **`npn13G2V`.** DR-003 fallback, speed cost.

Scratch sweep of the series R (single-corner probes, hbt_bcs/1.32 V at 125 C and -40 C, and
two speed corners; not recorded evidence): latch R of 8 to 12 ohm left qn at 1.35 to 1.36 V
(still over); 14 ohm gave 1.30 V, 16 ohm 1.282 V, 20 ohm 1.244 V, and 25 ohm cost about 12 %
of latch swing; clock-buffer 5 ohm gave 1.303 V. A decoupling cap on `vl` made no useful
difference, so none is added.

## Decision

Option 1: `latch_cml` gets `Rsl` = 16 ohm from `vdd` to a new node `vl`, with `RLp/RLn`
(100 ohm) returned to `vl`. `clk_buf_quad` gets a 5 ohm series resistor (`Rsi2`, `Rsq2`)
in each stage-2 load return (loads 225 ohm). The stage-1 loads are unchanged. R3 is
unchanged. The resistors are ideal in simulation, like the other passives (sim/README.md).

Evidence: [`sim/rx/records/20261123-202156-f5860fa-vce/`](../../sim/rx/records/20261123-202156-f5860fa-vce/record.md)
with the before/after comparison in `comparison.md` there. Baseline for the comparison:
`sim/rx/records/20261123-102613-14d2158/`. All simulated, not measured.

- Worst collector-to-ground over the 27-corner latch/clock run is now 1.3180 V
  (clock-buffer stage 1, `qq1b`, hbt_bcs/1.320 V/-40 C); the latch worst is 1.3007 V and the
  clock-buffer stage-2 worst 1.3059 V. Every node is at or under 1.32 V. The stage-1
  clock nodes were not changed and now have the least margin (2 mV); they are the next
  place to look if the buffer is touched again.
- Reverse Vbe: the worst reverse-Vbe maximum is negative (-0.26 V, latch `qh1`), i.e. no
  device is reverse-biased at all in the run, against the 1.0 V limit.
  CTLE operating-point and driven-transient records show the same maxima as the baseline
  (1.3145 V worst transient collector node, 1.3089 V worst Vce), unchanged.

## Consequences

- Latch speed holds: floor-level (0.10 V) regeneration is 2.2 to 25.2 ps at every corner
  against the 100 ps limit (baseline 1.5 to 17.5 ps). All 27 corners pass.
- Latch swing falls about 10 %. Corners reaching the 0.25 V decision level go from 21 of 27
  to 19 of 27. The baseline's six non-reaching corners (1.08 V, plus wcs/1.080 V) are still
  non-reaching, and two more now miss on swing, not speed: hbt_bcs/1.080 V/27 C (92.5 ps
  before) and hbt_wcs/1.200 V/-40 C (93.9 ps before). Several 1.08 V and 1.20 V corners
  that did reach it are slower (up to 94 ps). This is a real cost of the fix, reported
  rather than traded away: the 0.25 V level is the CMOS converter's need (#253/#251), so
  the converter and latch swing should be re-checked together there. If that needs more
  swing, the lever is a smaller `Rsl` with a smaller margin to 1.32 V (14 ohm: 1.30 V),
  not a change to R3.
- Clock buffer: differential swing falls 0.1 to 1.6 % (largest at 1.32 V: 1.659 -> 1.638 V
  at hbt_bcs/-40 C), duty on both pairs changes by under 0.06 percentage points (worst
  48.76 % to 48.82 %), so R20's duty budget is not affected by this change.
  Quadrature and slew are in the record.
- The latch and clock-buffer layout cells (`layout/analog/rx/`) do not yet carry the new
  resistors, so layout, DRC and LVS for those two cells must be redone from the revised
  netlists; not done here.
