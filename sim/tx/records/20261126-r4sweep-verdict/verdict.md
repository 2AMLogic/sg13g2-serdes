# TX R4 swing-shortfall verdict (issue #286)

**Sizing evidence, not a spec result and not a measurement.** Simulated, FFE off, fixed external 100 ohm
differential load behind the R18 pad stand-in (4 ohm + 70.66 fF extracted pad C + PDK ESD diodes). No
`spec/` row is edited or graded; R3 and R4 are as ratified.

Circuit revision: `main` at `5c4eac5` (driver back-termination RT1/RT2 = 50 ohm typical, load return as on
main). PR #270's revised load return is **not** simulated here, so nothing below is a conclusion about it.
The #270 numbers in the issue (194.1 mVppd FFE-off worst) were taken from the issue text and not re-derived.

Records (all raw reports under `batch/`, request and deck hashes in each `record.md`):

| record | set |
|---|---|
| `20261126-093716-5c4eac5-r4sweep-wcs` | 11 candidates, WCS x 3 V x 3 T (single-variable and first combinations) |
| `20261126-094722-5c4eac5-r4sweep-wcs-stage3` | control + RT 3x/4x/6x at +80 mV bias, WCS |
| `20261126-095030-5c4eac5-r4sweep-typ`, `...-bcs` | same four candidates, TYP and BCS |

## Swing quantity

`v(padp) - v(padn)`, settled high minus settled low, at the 100 ohm load. Static sample 1.35 ns / 2.55 ns
(end of 12-bit runs); PRBS cross-check = levels 10 ps before the end of the longest one run (4 bits) and
zero run (6 bits) of the PRBS-7 slice. The two agree to within 1.2 mV in every row, so with FFE off the
static figure is the same quantity the R4 PRBS-7 method would read as a settled level; it is a VOD-style
quantity only in FFE-off mode. The all-slices-on level (de-emphasised, 132.0 mVppd worst on main) is a
de-emphasis measurement and is not compared with R4's VOD.
Control reproduction: WCS/1.08 V/-40 C FFE off, 207.1 mVppd recorded on main; the instrumented control
gives 208.3 (+1.2 mV). The instrumented deck routes the main-tail base through a bench buffer and adds a
0 V sense source, so a 1 mV shift is expected; not otherwise isolated. TYP/1.20 V/27 C: 416.9 recorded,
419.8 here. The FFE-on control rows were not re-run (out of scope; recovered from the raw reports only).

## What the sweep establishes (WCS, 1.08 V, -40 C, FFE off, static mVppd)

| change | main tail mA | tail Vce min mV | swing |
|---|---:|---:|---:|
| control | 4.63 | 107.6 | 208.3 |
| tail bias -40 mV | 2.82 | 132.8 | 127.7 |
| tail bias +40 / +80 / +120 mV | 5.59 / 6.26 / 6.88 | 97.7 / 90.2 / 85.8 | 249.3 / 271.1 / 273.8 |
| RT x1.25 / x1.5 / x2.0 (bias unchanged) | 4.63 | ~107 | 233.3 / 253.8 / 285.0 |
| +80 mV bias, RT x2 / x3 / x4 / x6 | 6.25 / 6.24 / 6.23 / 5.67 | 89 / 89 / 88.5 / 87 | 370.3 / 421.7 / 452.8 / 421.2 |

- Bias alone is **not** enough and shows diminishing return: current +48 % (4.63 -> 6.88 mA) buys only +31 %
  swing, and from +80 to +120 mV bias the swing moves 2.7 mV while the tail Vce falls 90 -> 86 mV. This is
  consistent with a tail-headroom limit on the current axis, but the tail Vce is already 108 mV in the
  control, so the sweep does not isolate headroom from the tail's own large-signal limit.
- Back-termination alone is also not enough: RT x2 reaches 285.0 mVppd, still under the 300 fallback.
- The shortfall at this corner is mostly mA x ohm: 4.63 mA into the 50 ohm differential equivalent is about
  231 mV before pad losses. Both levers together reach 421.7 mVppd at WCS (RT x3, +80 mV).
- RT x4 raises the WCS/-40 C level to 452.8 but the worst tested corner moves to WCS/1.08 V/125 C (346.0 mVppd),
  and RT x6 collapses (421 at the cold corner, 187.5 at 125 C) with the driver pair's minimum Vce down to
  0.10 V, plus two corners (1.20 V/27 C, 1.32 V/27 C) that ngspice aborts with `timestep_too_small` for every
  process. RT x6 is outside the usable range and the aborts are kept, not reported as results.

## Best supported operating point (tested range only)

Main-tail bias +80 mV and RT1 = RT2 = 3 x the main value (about 150 ohm typical), FFE off, "c_p80_r300":

| process | worst static mVppd over 9 corners (corner) | margin to 500 | margin to 300 |
|---|---:|---:|---:|
| WCS | 421.7 (1.08 V, -40 C) | -78.3 | +121.7 |
| TYP | 486.2 (1.08 V, 125 C); 487.7 at 1.08 V, -40 C | -13.8 | +186.2 |
| BCS | 539.0 (1.08 V, 125 C) | +39.0 | +239.0 |

(Values from the R3 table's "min static" column of each record.) It clears the 300 mVppd fallback at every
tested sizing corner and the 500 mVppd target everywhere except WCS and TYP at 1.08 V. R7 20-80 % rise and fall,
as measured by the existing fixed-threshold cards, stay at 3 to 5 ps in this set (no bandwidth penalty is seen
at this load; the thresholds are not a conforming 20-80 % at low swing, see `sim/tx/README.md`).

## R3 at the best supported point

- driver_ffe cards (collector <= 1.32 V, Vce <= 1.4 V, reverse Vbe <= 1.0 V): smallest margin 0.345 V (WCS),
  0.351 V (TYP), 0.352 V (BCS), all `vc_max_drv_out_n` at 1.32 V / -40 C. The control's driver margin was
  0.025 V, so the larger load and the extra bias reduce the driver stress here.
- predriver / bias cards **fail**, as they already do on main: control worst -8 mV (`vc_max_pre_post_outn`,
  1.32 V). In the best supported point the worst moves to -7 mV (WCS), -16 mV (TYP) and **-76 mV (BCS,
  1.32 V, -40 C, `vc_max_pre_post_outn`)**. The nodes are the driver's own base nodes (rp/rn, pp/pn). A plausible
  cause, not verified here, is feed-through from the larger driver collector swing; the sweep does not
  establish it. In the control and in this point, the three 1.32 V corners of each process fail R3 on those cards.

## Verdict

- The headroom hypothesis is **partly supported and not sufficient**: more tail current has diminishing
  return as tail Vce falls toward 86 mV, and the shortfall is not removed by bias alone; at least one other
  factor, the load seen by the tail current, is equally large. It is not refuted as a contributor.
- **500 mVppd at 1.08 V is not shown reachable at every sizing corner within the tested range**: the best point misses
  it by 78 mV at WCS and 14 mV at TYP, and the one candidate exceeding it at WCS/-40 C (RT x4) falls to 346 mVppd at
  WCS/125 C. 500 mVppd is not shown unreachable either: the tested designs are two single knobs and a few
  combinations, not an optimisation, and the PVT-full R4 coverage was not run (this is the HBT sizing grid,
  3 x 3 per process pairing at three pairings, not R4's PVT-full).
- **Conflict with R3**: the swing gains in this range come with predriver-node R3 overshoot that is already
  open on main and gets worse at BCS (-8 -> -76 mV). That bound is recorded on #249, which owns the R3
  collector-overshoot decision; no spec row is relaxed here. The R4 question stays open pending that decision and
  a PVT-full run of any chosen point. An operator decision is needed on whether to size the driver to the 300 mVppd
  fallback with R3 deferred, or to pursue a termination/bias change together with a predriver R3 fix.
- Not done / out of scope: FFE-on behaviour of the candidates, the revised #270 load return, the mux and clock
  margin, PVT-full coverage, and any production circuit or layout change.
