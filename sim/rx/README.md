# sim/rx

Sizing benches for the RX path in `design/rx/` (issue #22). **Sizing evidence,
not spec results**: `spec/target-spec.md` is PROPOSED, resistors are ideal, the
pad capacitance and the CTLE load are placeholders, the clock source is ideal.
The MOS level converter has its own set and record (issue #241, below); the four
HBT benches do not include it.

| File | What |
|---|---|
| `ctle_ac.sp` | 8 copies of `ctle`, one per peaking code; AC gain at 0.1, 2.5, 5 GHz |
| `ctle_op.sp` | same circuit at its operating point: output common mode, max collector V and reverse Vbe per HBT |
| `latch_regen.sp` | clock buffer + latch at 5 GHz: regeneration time to two fixed \|q\| levels (0.25 V decision, 0.10 V floor), collector/Vbe stress |
| `pad_ac.sp` | termination + pad + CTLE: differential drive current, so \|Zdiff\| at 0.1 and 5 GHz |
| `lvl_cml2cmos.sp` | the `latch_regen` deck with one `lvl_cml2cmos` on `qp`/`qn`: output levels, delays, edges, pulse widths and the converter's own supply current (PSP103 via `osdi_preload`) |
| `*.request.json` | `klt sim` requests: the four HBT benches on HBT corners (ganged with CAP and DIO sections) x 1.08/1.2/1.32 V x -40/27/125 C; `lvl_cml2cmos` on 5 MOS corners (ganged with HBT/CAP/RES as in `sim/tx/make_tb.py`) x the same supplies and temperatures |
| `run_sizing.sh` | `run_sizing.sh` submits the four HBT requests (batch fleet) and writes `records/<id>/`; `run_sizing.sh mos` submits `lvl_cml2cmos` and writes `records/<id>-mos/` |
| `tools/gen_requests.py` | generates the `.sp` bodies and requests; the node-stress `.meas` cards follow the exported netlists |
| `tools/make_record.py` / `tools/make_record_mos.py` | render `record.md` from the reports: HBT set / MOS set |

Requests and bodies are generated: edit `tools/gen_requests.py`, rerun it,
commit the output.

## Records (append-only)

`records/20261114-050716-eb34d10` is the newest HBT-set record and the one the
behavioural link benches should fit to: it is the first with no `error` corner
for `latch_regen`, so every corner carries a regeneration number or an explicit
`not_reached` verdict. `records/20261110-222737-506b37e` is the previous
complete record (6 `error` corners; see "Regeneration at low supply" below).
`records/20261027-022309-00c2ed7` is the first complete record. The three
earliest directories are failed submissions, kept as found:

- `20261027-015751-ace29de`: client `klt 0.8.1.dev` against a `0.7.0` fleet runner (`batch_runner_version_mismatch`). Use the pinned client from `layout/toolchain.json` (repo-local `.venv`).
- `20261027-020212-ace29de`: `corners.units` silently ignored by the `0.7.0` runner; one default corner ran with no models (klayout-tools#4215).
- `20261027-020651-dc25cd0`: `measurements[].expr` jobs exit 2 with no diagnostic (klayout-tools#4217); the requests use plain `.meas` cards since.

`records/20261123-025944-cd608e7-mos` is the MOS-set record (`run_sizing.sh mos`, issue #241), the first that simulates `lvl_cml2cmos`. The HBT records above say the converter is "not simulated"; that statement is superseded for that cell only.

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

## Level converter at 5 Gb/s (MOS set, issue #241)

**Sizing evidence from a simulation, never a measurement.** All figures are
read from `records/20261123-025944-cd608e7-mos/lvl_cml2cmos.report.json`
(45-corner MOS grid, `klt sim` on the batch fleet, `errored: 0`, request
`exit=3`). The converter is driven by the latch it loads in `rx_top`, so its
input is the latch's own swing (0.29 to 1.14 V differential) at 5 Gb/s per
wire (the 1010 stream, 200 ps per bit); the load is an assumed 20 fF.

The request declares two first-look bounds, neither a spec value (DR-008 item 3
leaves the converter unspecified): the output reaches 90 % of vdd rising and
10 % of vdd falling within 100 ps of the clock edge that closes the latch's
sample phase. Against them:

- 2 of 45 corners are inside both bounds with full levels
  (`ff_bcs/1.320V/-40C`, `ff_bcs/1.320V/27C`); 0 of 15 at 1.080 V and 0 of 15
  at 1.200 V.
- At 14 corners the output never rises above vdd/2. Eleven are at 1.080 V,
  three at 1.200 V; at `ss_wcs/1.200V/27C` the latch swings 0.62 V and the
  converter still stops at 0.274 V, so this is not only the latch's 1.080 V
  swing limit.
- At 4 more corners the rising edge stops under 90 % of vdd.
- Of the 27 corners that reach 90 %, the hold edge to 90 % is 86.4 to 210.2 ps
  and 24 are over 100 ps; of the 31 that reach 10 %, the hold edge to 10 % is
  66.7 to 185.8 ps and 18 are over 100 ps.
- Typical, `tt_typ/1.200V/27C`: 158.4 ps to 90 % rising, 114.1 ps to 10 %
  falling; the output is high for 158.7 ps and low for 241.2 ps where the input
  is 200/200.

This is a sizing finding for the cell (`design/rx/lvl_cml2cmos`, issue #22),
not a spec relaxation: no limit was changed to produce it. The stage it sits
in, and what keeps evidence gate G3 open, are in `spec/clock-domains.md`.

## Constraints that shaped the benches

- `.meas` cards only (see above). Operating-point values use a two-point dummy dc sweep (`Vdmy`), differences go through `B` sources (ngspice caps `par()` at 99 calls per deck, klayout-tools#4218).
- **No swing-relative threshold.** A `.meas` card cannot reference an earlier `.meas` result: `.meas tran vpk max v(q)` followed by `.meas tran t when v(q)='0.5*vpk'` fails with `Undefined parameter [vpk]` and aborts the whole deck (verified on ngspice 47), and `measurements[].expr` is refused by the fleet runner (klayout-tools#4217). Regeneration levels are therefore fixed absolute volts, with a floor level low enough that every corner crosses it.
- The PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models and the PSP103 MOS models need OSDI. klt 0.8.0 cleared the batch `.osdi` blocker (klayout-tools#3818), so the MOS converter runs in the MOS set with `osdi_preload` like the TX MOS-cell benches; every resistor in `design/rx` is still an ideal `res`, so the HBT benches exercise no resistor corner.
