# sim/rx

Sizing benches for the RX path in `design/rx/` (issue #22). **Sizing evidence,
not spec results**: `spec/target-spec.md` is PROPOSED, resistors are ideal, the
pad capacitance and the CTLE load are placeholders, the clock source is ideal.

| File | What |
|---|---|
| `ctle_ac.sp` | 8 copies of `ctle`, one per peaking code; AC gain at 0.1, 2.5, 5 GHz |
| `ctle_op.sp` | same circuit at its operating point: output common mode, max collector V and reverse Vbe per HBT |
| `latch_regen.sp` | clock buffer + latch at 5 GHz: regeneration time to two fixed \|q\| levels (0.25 V decision, 0.10 V floor), collector/Vbe stress |
| `pad_ac.sp` | termination + pad + CTLE: differential drive current, so \|Zdiff\| at 0.1 and 5 GHz |
| `*.request.json` | `klt sim` requests: HBT corners (ganged with CAP and DIO sections) x 1.08/1.2/1.32 V x -40/27/125 C |
| `run_sizing.sh` | submits the four requests (batch fleet) and writes `records/<id>/` |
| `tools/gen_requests.py` | generates the `.sp` bodies and requests; the node-stress `.meas` cards follow the exported netlists |
| `tools/make_record.py` | renders `record.md` from the reports |

Requests and bodies are generated: edit `tools/gen_requests.py`, rerun it,
commit the output.

## Records (append-only)

`records/20261114-050716-eb34d10` is the newest record and the one the
behavioural link benches should fit to: it is the first with no `error` corner
for `latch_regen`, so every corner carries a regeneration number or an explicit
`not_reached` verdict. `records/20261110-222737-506b37e` is the previous
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
and otherwise clean grades `pass_partial`, as the six 1.080 V corners do
individually.

## Constraints that shaped the benches

- `.meas` cards only (see above). Operating-point values use a two-point dummy dc sweep (`Vdmy`), differences go through `B` sources (ngspice caps `par()` at 99 calls per deck, klayout-tools#4218).
- **No swing-relative threshold.** A `.meas` card cannot reference an earlier `.meas` result: `.meas tran vpk max v(q)` followed by `.meas tran t when v(q)='0.5*vpk'` fails with `Undefined parameter [vpk]` and aborts the whole deck (verified on ngspice 47), and `measurements[].expr` is refused by the fleet runner (klayout-tools#4217). Regeneration levels are therefore fixed absolute volts, with a floor level low enough that every corner crosses it.
- The PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models and the PSP103 MOS models need OSDI, so neither is simulated (`sim/README.md`, klayout-tools#3818).
