# sim/rx

Sizing benches for the RX path in `design/rx/` (issue #22). **Sizing evidence,
not spec results**: `spec/target-spec.md` is PROPOSED, resistors are ideal (the
`rppd` termination-corner bench of issue #240 is the exception), the
pad capacitance and the CTLE load are placeholders, the clock source is ideal.

| File | What |
|---|---|
| `ctle_ac.sp` | 8 copies of `ctle`, one per peaking code; AC gain at 0.1, 2.5, 5 GHz |
| `ctle_op.sp` | same circuit at its operating point: output common mode, max collector V and reverse Vbe per HBT |
| `ctle_tran.sp` | 16 copies of `ctle` (8 codes x 2 input levels): transient max Vc, Vce and reverse Vbe per HBT over a driven run (both polarities of a settled long run, each followed by 5 GHz alternation) |
| `latch_regen.sp` | clock buffer + latch at 5 GHz: regeneration time to two fixed \|q\| levels (0.25 V decision, 0.10 V floor), collector/Vbe stress |
| `pad_ac.sp` | termination + pad + CTLE: differential drive current, so \|Zdiff\| at 0.1 and 5 GHz |
| `pad_ac_rppd.sp` | `pad_ac` with the two ideal 50 Ω termination legs replaced by PDK `rppd` instances (`r3_cmc` OSDI, w=2 µm as p.11 recommends), over the RES library corners ganged with the same-index HBT/CAP/DIO sections (issue #240, R9 gate G1) |
| `pad_ac_rppd_p11win.sp` | same circuit with `rsh_rppd` overridden to the process-spec p.11 window edges folded at w=2 µm (derived in `spec/sources/rppd-tolerance-window.md`) |
| `*.request.json` | `klt sim` requests: HBT corners (ganged with CAP and DIO sections) x 1.08/1.2/1.32 V x -40/27/125 C; the two `*_rppd*` ones add the RES sections and `osdi_preload` |
| `run_sizing.sh [vce]` | submits the five requests (batch fleet) and writes `records/<id>/`; `vce` suffixes the record id `-vce` (R3 per-device Vce pass, issue #242) |
| `run_rppd_corners.sh` | submits the two rppd requests (batch fleet) and writes `records/<id>-rppd-corners/` (issue #240) |
| `tools/gen_requests.py` | generates the `.sp` bodies and requests; the node-stress `.meas` cards follow the exported netlists |
| `tools/make_record.py` | renders `record.md` from the reports |
| `tools/make_record_rppd.py` | renders `record.md` for the rppd-corner record family |

Requests and bodies are generated: edit `tools/gen_requests.py`, rerun it,
commit the output.

Every HBT now carries three stress cards per bench: `*_vc_max` (collector to
ground, <= 1.32 V), `*_vce_max` (collector to emitter through a B source,
<= 1.4 V open-base BVCEO) and `*_vbe_rev_max` (<= 1.0 V). The renderer's
per-device table aggregates the 8 CTLE code copies into 36 rows (ctle 22,
clk_buf_quad 8, latch_cml 6), matching the `npn13G2` instances of the exported
netlists; first `-vce` record: `records/20261123-025159-fedf656-vce/` (issue #242,
gate G2 / row R3 of tracker #238).
Caveat: in the `-vce` record above the 22 `ctle.*` rows come from `ctle_op`,
a zero-input DC operating point (`.meas dc ... at=0`), so they are
quiescent-only; only `clk_buf_quad` and `latch_cml` (and all TX) rows are
transient maxima there. The `ctle_tran` bench (issue #256) supplies the CTLE
transient maxima, and the renderer folds its rows into the same `ctle.*` rows
whenever a record carries a `ctle_tran` report.

## Records (append-only)

`records/20261123-102613-14d2158` is the newest record and the one the
behavioural link benches should fit to: it re-runs the four benches of
`records/20261114-050716-eb34d10` (identical latch verdicts: 0 `error`
corners, 12 `not_reached`, the nine 1.32 V collector findings unchanged) and
adds the CTLE transient node-stress bench of issue #256 — see "CTLE transient
node stress" below. `records/20261114-050716-eb34d10` is the previous record
and the first with no `error` corner for `latch_regen`, so every corner
carries a regeneration number or an explicit `not_reached` verdict.
`records/20261110-222737-506b37e` is the previous
complete record (6 `error` corners; see "Regeneration at low supply" below).
`records/20261027-022309-00c2ed7` is the first complete record. The three
earliest directories are failed submissions, kept as found:

- `20261027-015751-ace29de`: client `klt 0.8.1.dev` against a `0.7.0` fleet runner (`batch_runner_version_mismatch`). Use the pinned client from `layout/toolchain.json` (repo-local `.venv`).
- `20261027-020212-ace29de`: `corners.units` silently ignored by the `0.7.0` runner; one default corner ran with no models (klayout-tools#4215).
- `20261027-020651-dc25cd0`: `measurements[].expr` jobs exit 2 with no diagnostic (klayout-tools#4217); the requests use plain `.meas` cards since.

## Regeneration at low supply: swing, not speed

**Sizing evidence from a simulation, never a measurement.** All figures below
are read from `records/20261114-050716-eb34d10/latch_regen.report.json`
(27-corner HBT grid, `klt sim` on the batch fleet, `errored: 0`,
`not_reached: 12`).

Regeneration is measured to **two fixed absolute levels** of |q|, both plain
`.meas` cards (neither is swing-relative -- see Constraints below):

- **0.25 V, the decision level** the DR-002 sampler fits need the latch to
  resolve to. Declared `on_unreached: "null"`, so a corner whose |q| asymptotes
  below it is graded `not_reached` -- an explicit "does not regenerate to the
  decision level" verdict -- instead of erroring the corner, which is what the
  previous record `20261110-222737-506b37e` did at 6 of 27 corners.
- **0.10 V, a floor level** every corner in the grid crosses (worst-case peak
  |q| is 0.148 V), so a regeneration *speed* is returned even where the
  decision level is not reached. This is what separates "too slow" from
  "too weak".

### Cause of each of the 6 `error` corners in the previous record

All six were the **threshold, not the latch's speed**: the measurement could
not fire because 0.25 V is an absolute level the output swing never reaches at
1.080 V. The six are exactly the six corners whose peak |q| is below 0.25 V,
with no overlap in either direction, and each of them regenerates to the 0.10 V
floor level well inside the 100 ps limit:

| corner | peak \|q\| (V) | vs 0.25 V | t_regen to 0.10 V, up / dn (ps) | cause |
|---|---|---|---|---|
| hbt_wcs/1.080V/-40C | 0.148 | below | 17.5 / 16.8 | swing |
| hbt_typ/1.080V/-40C | 0.176 | below | 10.6 / 10.2 | swing |
| hbt_wcs/1.080V/27C | 0.187 | below | 14.1 / 13.1 | swing |
| hbt_bcs/1.080V/-40C | 0.206 | below | 6.9 / 6.6 | swing |
| hbt_typ/1.080V/27C | 0.222 | below | 8.6 / 8.0 | swing |
| hbt_wcs/1.080V/125C | 0.240 | below | 14.1 / 12.6 | swing |

The latch *is* weak at the low supply corner, but that weakness shows up as
swing, not as a missed timing limit.

### Per corner that misses the 100 ps first-look limit: speed or swing

**No corner in the 27-point grid misses the 100 ps limit on speed, at either
level.** The slowest regeneration anywhere is 93.9 ps to the decision level
(hbt_wcs/1.200V/-40C) and 17.5 ps to the floor level
(hbt_wcs/1.080V/-40C); the report's own "slower than 100 ps" counts are `0` for
both levels. So:

- **Misses on speed: none.** No corner reached a level later than 100 ps.
- **Misses on swing: the 6 corners in the table above**, all at 1.080 V. They
  never reach the 0.25 V decision level at all, so no regeneration time to that
  level exists to compare against 100 ps. Their floor-level times (6.6-17.5 ps)
  show the regeneration itself is fast; the deficit is amplitude.

The nearest corner to the decision-level limit is hbt_bcs/1.080V/27C at
92.5 / 92.3 ps with a peak |q| of 0.261 V -- 7.5 ps of margin and 11 mV of
swing margin. Margin at 1.080 V is thin on both axes, which is a sizing
finding for #22, not a spec relaxation.

### The record still exits 3, and that is the honest result

`latch_regen exit=3` in `records/20261114-050716-eb34d10/exit-codes.txt`:
`errored` is 0, but the **nine 1.320 V corners exceed the DR-003 collector
limit** -- six collector nodes over 1.32 V: `latch_xl_qs1_vc_max` and
`latch_xl_qh1_vc_max` at all 9, `clk_xclk_qq2a_vc_max` at 8,
`clk_xclk_qq2b_vc_max` at 7, and `latch_xl_qs2_vc_max` / `latch_xl_qh2_vc_max`
at 1 each. That is a separate, already-recorded finding, reported under
"HBT node stress versus DR-003" in `record.md`. It is not relaxed to make the
bench exit 0, so `run_sizing.sh` exits 1. The report's aggregate status is
`fail` (never an unqualified `pass`), and `coverage` carries 12 `skipped`
entries with `reason: "not_reached"` for the unreached decision-level limits --
recorded as found, not engineered around. A corner that is only `not_reached`
and otherwise clean still grades `pass` at the corner level: each of the six
1.080 V corners does, carrying two info-severity `measurement_not_reached`
diagnostics. The unreached decision-level limits are therefore visible only in
those diagnostics and in the 12 `skipped` coverage entries, never as a
corner-level penalty -- read `coverage`, not the corner status, to see them.

## CTLE transient node stress

**Sizing evidence from a simulation, never a measurement.** The `ctle_op`
stress cards are quiescent (inputs at `dc 0`), so the R3 per-device table's
CTLE rows were operating-point values — a lower bound for a differential pair,
whose off-side collector rises under signal. The `ctle_tran` bench (issue
#256, record `records/20261123-102613-14d2158`) replaces them with
`.meas tran` maxima over a driven run that exercises **both polarities** of the
settled long run (the `ctle` input network is a symmetric pair with AC-coupled
feed-forward paths, so one polarity under-stresses half of it): 2 ns settled,
1 ns of 5 GHz alternation (200 ps period, 20 ps edges), 3 ns held at the
opposite polarity (> 8 tau of the 300 ps feed-forward), 1 ns of alternation
again; all 8 peaking codes, 27-corner grid, max Vc / Vce / reverse Vbe per HBT.

The spec declares **no maximum RX input swing** (R8 gives only the minimum
sensitivity), so the bench runs two named bounds rather than an invented one:

- **50 mVppd** — R8 nominal RX input sensitivity, the stress floor.
- **800 mVppd** — the R4 stretch (maximum) TX swing taken as the pad amplitude
  at zero channel loss: the committed channel model (`spec/channel/`) has
  S11 = S22 = 0 and IL(f) -> 0 dB as f -> 0, so the largest pad amplitude it
  admits is the TX swing itself.

Result over the whole grid, both levels, all codes: **no DR-003 violation**
(limits Vc 1.32 V, Vce 1.40 V/BVCEO, reverse Vbe 1.0 V/BVEBO). Worst Vc is
1.315 V (device `q1`, code 7, hbt_wcs/1.320V/-40C) — a 5 mV margin. The `hi`
(800 mVppd) swing fully switches off one side of the pair (Ic -> 0), pulling
that off-side collector up to the +10 % rail (1.320 V); the `lo` (50 mVppd)
swing does not, and its worst Vc is 1.067 V. Worst Vce
1.309 V; reverse Vbe never leaves forward bias anywhere (worst -0.334 V). An
earlier record (`records/20261123-050201-5214c04`) drove one polarity only and is superseded
by an Erratum in that record. The 5 mV collector margin is a sizing finding for #22, not a spec relaxation.

## Constraints that shaped the benches

- `.meas` cards only (see above). Operating-point values use a two-point dummy dc sweep (`Vdmy`), differences go through `B` sources (ngspice caps `par()` at 99 calls per deck, klayout-tools#4218).
- **No swing-relative threshold.** A `.meas` card cannot reference an earlier `.meas` result: `.meas tran vpk max v(q)` followed by `.meas tran t when v(q)='0.5*vpk'` fails with `Undefined parameter [vpk]` and aborts the whole deck (verified on ngspice 47), and `measurements[].expr` is refused by the fleet runner (klayout-tools#4217). Regeneration levels are therefore fixed absolute volts, with a floor level low enough that every corner crosses it.
- The PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models and the PSP103 MOS models need OSDI, so neither is in the five main benches (`sim/README.md`, klayout-tools#3818). The `rppd` termination-corner bench (issue #240, `run_rppd_corners.sh`) loads `r3_cmc` via `osdi_preload` on the batch fleet, as the TX MOS benches do; the CTLE-internal and latch resistors are still ideal.
