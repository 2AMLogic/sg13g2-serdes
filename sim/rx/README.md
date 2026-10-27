# sim/rx

Sizing benches for the RX path in `design/rx/` (issue #22). **Sizing evidence,
not spec results**: `spec/target-spec.md` is PROPOSED, resistors are ideal, the
pad capacitance and the CTLE load are placeholders, the clock source is ideal.

| File | What |
|---|---|
| `ctle_ac.sp` | 8 copies of `ctle`, one per peaking code; AC gain at 0.1, 2.5, 5 GHz |
| `ctle_op.sp` | same circuit at its operating point: output common mode, max collector V and reverse Vbe per HBT |
| `latch_regen.sp` | clock buffer + latch at 5 GHz: regeneration time, collector/Vbe stress |
| `pad_ac.sp` | termination + pad + CTLE: differential drive current, so \|Zdiff\| at 0.1 and 5 GHz |
| `*.request.json` | `klt sim` requests: HBT corners (ganged with CAP and DIO sections) x 1.08/1.2/1.32 V x -40/27/125 C |
| `run_sizing.sh` | submits the four requests (batch fleet) and writes `records/<id>/` |
| `tools/gen_requests.py` | generates the `.sp` bodies and requests; the node-stress `.meas` cards follow the exported netlists |
| `tools/make_record.py` | renders `record.md` from the reports |

Requests and bodies are generated: edit `tools/gen_requests.py`, rerun it,
commit the output.

## Records (append-only)

`records/20261027-022309-00c2ed7` is the first complete record. The three
earlier directories are failed submissions, kept as found:

- `20261027-015751-ace29de`: client `klt 0.8.1.dev` against a `0.7.0` fleet runner (`batch_runner_version_mismatch`). Use the pinned client from `layout/toolchain.json` (repo-local `.venv`).
- `20261027-020212-ace29de`: `corners.units` silently ignored by the `0.7.0` runner; one default corner ran with no models (klayout-tools#4215).
- `20261027-020651-dc25cd0`: `measurements[].expr` jobs exit 2 with no diagnostic (klayout-tools#4217); the requests use plain `.meas` cards since.

## Constraints that shaped the benches

- `.meas` cards only (see above). Operating-point values use a two-point dummy dc sweep (`Vdmy`), differences go through `B` sources (ngspice caps `par()` at 99 calls per deck, klayout-tools#4218).
- The PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models and the PSP103 MOS models need OSDI, so neither is simulated (`sim/README.md`, klayout-tools#3818).
