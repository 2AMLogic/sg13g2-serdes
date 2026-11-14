# DR-009: TX mux clock swing: what the mux needs, and who provides it

- **Status**: proposed
- **Date**: 2026-11-10
- **Decided by**: builder (issue #98); ratification is an operator step

DR-NNN is the next unused number at merge time (DR-008 was the highest on
`main` at `f7361f7`) and is the permanent ID. This record adds a requirement
to `spec/clock-requirement.md`; it edits no ratified row.

## Context

The `mux2to1_cml` bench drives `ckp`/`ckn` with 0.4 V to 0.8 V per side (0.4 V
per side, 0.8 V differential peak-to-peak), an assumption
(`sim/tx/make_tb.py`, `sim/tx/README.md`). The only written clock figure is the
`sg13g2-vco` row "swing >= 0.40 Vpp at the tank nodes", with per-node vs
differential not stated. Nothing derived the swing the mux needs.

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

**Comparison** (my reading of each sibling's spec as pinned in
`spec/clock-requirement.md`; owner to confirm):

| Sibling | States a clock swing at an interface the mux can use? | Meets >= 0.4 V/side? |
|---|---|---|
| `sg13g2-vco` | "swing >= 0.40 Vpp at the tank nodes"; per node vs differential not stated; ratified "no output buffer in v1", so no buffered output | Not stated: 0.40 Vpp at the tank nodes is the only figure; per node vs differential is unstated and no buffered output or load exists |
| `sg13g2-pll` | No swing row | Not stated |
| `sg13g2-lc-pll` | No swing row found; buffer is "if needed", load not stated | Not stated |

No sibling states or meets it. Requirements are filed on each sibling (links
in Consequences).

## Consequences

- `spec/clock-requirement.md` "Level / load" row gains this requirement.
- The bench stays at 0.4 V per side; `sim/tx/make_tb.py` gains a swing
  parameter defaulting to today's value (default decks byte-identical), and the
  sweep decks use a separate `tx_mosck_` prefix so `sim/tx/run_sizing.sh mos`
  and its record are unchanged.
- The mux does not close at `ss_wcs`/1.08 V at 0.4 V per side. Whether a larger
  swing closes it, or the squarer/tail sizing must change, is open work on the
  mux cell, not a clock-provider question alone.
- Sibling requirement issues filed: `2AMLogic/sg13g2-vco#319`, `2AMLogic/sg13g2-pll#312`, `2AMLogic/sg13g2-lc-pll#206`.
