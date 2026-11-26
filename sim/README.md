# sim

Simulation toolchain, pins and evidence. See the repo README "Bring-up" for the
reproduce steps.

| Path | What |
|---|---|
| `pdk.json` | PDK pin (IHP-Open-PDK v0.3.0, tarball sha256) |
| `toolchain.json` | simulator floors |
| `tools/build-osdi.sh` | compiles the PDK's Verilog-A sources (PSP103, r3_cmc, mosvar) with a checksum-pinned OpenVAF-Reloaded; exit 5 = built, but the host ngspice cannot load OSDI v0.4 |
| `tools/record-dir.sh` | record-directory reservation shared by the rx/tx/smoke runners: builds the `<ts>-<sha>` record id and delegates the exclusive creation to the single `reserve_record_dir` primitive in `scripts/klt-lib.sh` (reads the `mkdir(2)` result via python `os.mkdir`, immune to the uutils `mkdir` false-success of #220), so a same-second relaunch, a retry, or a double reservation refuses instead of overwriting saved evidence (issues #202, #220, #244); `tools/test-record-dir.sh` proves it with a fixed clock and a mock klt |
| `tools/record-dir-race-investigation.md` | issue #220 findings (append-only record, dated errata at the end): the hosted-runner double reservations came from the uutils coreutils 0.10.0 `mkdir` EEXIST rescue, which the python `os.mkdir` primitive `tools/record-dir.sh` delegates to is immune to (#244); the one-shot probe behind its measurements is removed, retrievable at `42fd372`, the revision that produced the full evidence set (the first-reproduction rows were taken at `de832e9`) |
| `smoke/` | toolchain smoke grid: HBT Gummel at every HBT corner section, MOS inverter DC at `tt/ff/ss/fs/sf`, and a mixed MOS+HBT transient. Placeholder devices, not design values |
| `smoke/records/<id>/` | append-only run records (reports, `record.md`); never edited after the fact |
| `rx/` | RX sizing benches (CTLE AC per setting, latch regeneration at 5 GHz, HBT node stress, termination first look). `rx/tools/gen_requests.py` writes the bench bodies and `klt sim` requests; `rx/run_sizing.sh` submits the 27-point HBT PVT grid to the batch fleet and writes `rx/records/<id>/` (append-only). Sizing evidence, not spec results |
| `tx/` | TX sizing decks, requests and append-only records (issue #21); see `tx/README.md` |
| `bench/` | testbench registry for T1 item 9: `benches.json` (one entry per bench: spec rows, requests, corner set, declared measurements) and `gen_inventory.py`, which derives `verification/testbench-inventory.json` from it. Also the DR-002 behavioural benches (`link_bench.py`, `linkcore.py`, `cdrmodel.py`, smoke test `test_link_bench.py`, and `link_sensitivity.py`, the one-factor-at-a-time CDR dither attribution of DR-009) |
| `harness/` | fetched by `scripts/setup-env.sh` per `reuse.lock.json` (gitignored, never committed) |

## HBT models

The SG13G2 HBT (`npn13G2`, VBIC) is built into ngspice and needs no OSDI. The PDK
provides corner sections `hbt_typ`, `hbt_bcs`, `hbt_wcs` plus `_mismatch` /
`_stat` Monte Carlo variants in `cornerHBT.lib`. MOS devices (PSP103) need the
OSDI models and `cornerMOSlv.lib` sections `mos_tt/ff/ss/fs/sf`.

## Known gaps (tool issues filed on 2AMLogic/klayout-tools)

- [#3818](https://github.com/2AMLogic/klayout-tools/issues/3818): batch jobs that stage `.osdi` inputs exit 2 with no diagnostic. Fixed in klt 0.8.0 (the pin since issue #42). Re-run by PR #76 (smoke) and by the TX MOS-cell benches in `tx/` (issue #80: executed on the fleet under klt 0.9.0, record `tx/records/20261110-221849-506b37e-mos/`, see `tx/README.md`). It is why the MOS and mixed smoke runs in the first record (klt 0.7.0) are `error`, not `pass`.
- [#3819](https://github.com/2AMLogic/klayout-tools/issues/3819): the submit-time OSDI ABI check judges the client's ngspice, not the worker's.

- PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models. They now load with `osdi_preload` (PR #76) and the TX MOS-cell benches in `tx/` simulate them (issue #80). The six TX HBT-bench decks still use a behavioural `rsil`, and `design/rx` uses ideal resistors and records that.

## PDK pin

Every record under `smoke/records/` and `rx/records/` traces to `pdk.json`; a bump to that file
is a new decision, not an edit of an earlier record.

## Testbenches (T1 item 9)

Graded against the PROPOSED draft rows (#2, not ratified) and DR-001 to DR-004; re-grade at ratification.
Entry point: `scripts/run-bench.sh` (`--list`, `<id>`, `<id> --run`). Default mode is a **check**: the
request is validated, the corner set expanded and the declared measurements asserted (no PDK, no fleet),
so it runs from a fresh clone. `--run` submits the full grid with `klt sim --wait-for-capacity 600`
(batch fleet) after `scripts/setup-env.sh` and `source scripts/env.sh`. Digital benches run the cocotb
test for real. Every printed figure is simulated, never measured, and no bench result is recorded by
this item (recording is T1 item 5). Analog checks grade with the klt pinned in `layout/toolchain.json`:
`run-bench.sh` resolves `.venv/bin/klt` by path (installed by `scripts/setup-env.sh`), so the pin holds even
inside `klt signoff --attest 9`'s sanitized cold-start environment; with no `.venv` it falls back to PATH `klt` (#176).

| Bench id | Rows | Corner set | Deck |
|---|---|---|---|
| `tx-link` | R3 R4 R5 R7 R16 | 54-pt PVT-full (3 HBT corners x 3 V x 3 T, six requests) | `tx/tx_sizing_ffe{0,1}_*` |
| `tx-mos-ffe-en` | R5 | 5 MOS corners x 3 V x 3 T | `tx/tx_mos_ffe_en` |
| `tx-mos-mux2to1-cml` | R3 R7 R16 | same | `tx/tx_mos_mux2to1_cml` |
| `tx-mos-lvl-cml2cmos` | R16 | same | `tx/tx_mos_tx_lvl_cml2cmos` |
| `rx-ctle-ac` | R10 | 27-pt HBT PVT-full | `rx/ctle_ac` |
| `rx-ctle-op` | R3 | same | `rx/ctle_op` |
| `rx-latch-regen` | R3 R8 (latch record only) | same | `rx/latch_regen` |
| `rx-term-pad` | R9 (|Zdiff| only) | same | `rx/pad_ac` |
| `tx-return-loss` | R6 (SDD22 on the extracted pad load; driver on and off requests) | 27-pt HBT PVT-full per request | `bench/r6_tx_return_loss_{on,off}` |
| `rx-clk-quality` | R20 (duty, quadrature; RJ is a gap) | 27-pt HBT PVT-full | `bench/r20_clk_quality` |
| `link-r8-sensitivity` | R8 | 27-pt HBT PVT-full x sampler offset MC | `bench/link_bench.py r8` |
| `link-r11-cdr-lock` | R11 | PVT-edge (corner-independent, see below) | `bench/link_bench.py r11` |
| `link-r12-jtol` | R12 | 4 PVT-edge corners for the eye | `bench/link_bench.py r12` |
| `link-r13-offset` | R13 | PVT-edge (corner-independent) | `bench/link_bench.py r13` |
| `link-r15-method` | R15 | 27-pt HBT PVT-full | `bench/link_bench.py r15` |
| `rtl-*` (8) | R22, R11 (digital), R2 | functional | `rtl/tests/test_*.py` |

The five `link-*` rows run one script, `bench/link_bench.py <row>`. The attested inventory (item 9) lists the model
source files, one cold start each, because klt refuses a path listed twice: `link_bench.py` (`link-r15-method`),
`linkcore.py` (`link-r8-sensitivity`), `cdrmodel.py` (`link-r11-cdr-lock`). `link-r12-jtol` and `link-r13-offset`
therefore have no attested cold start of their own; `scripts/run-bench.sh` still runs all five.

Each bench's `limitations` field in `bench/benches.json` states what it does not cover.
**R6** (`tx-return-loss`) loads both TX legs with the same extracted pad-metal capacitance
(70.66 fF to ground per leg, quasi-static lumped) and the PDK ESD diodes. The
[extraction record](../layout/analog/pads/records/2026-11-12-fc8a7fa/record.md)
tabulates padp and takes padn as identical (PR #145, DR-012). The PDK `bondpad` SPICE model
supplies no capacitance. R6's extracted per-leg load includes 25.41 fF from the bondpad
top metal. The model excludes bondwire, package, pad-to-pad coupling and distributed 5 GHz effects.
**R9** (`rx-term-pad`) uses ideal resistors and a placeholder 50 fF per pad in
`design/rx/netlists/rx_term_pad.spice`, pending the extracted RX pad model (#143).
Both benches report simulations. The R6/R20 decks are generated by `python3 -I sim/bench/gen_r6_r20.py`.

**Declared gaps** (inventory `unbenched_rows`, none silently omitted): none (R18 and R19 are bench-backed by `pad-cap-extracted` and `pad-esd-iv-extracted`, #94). Not simulation rows: R1 (graded by R15),
R14 (committed model), R17, R21. The random-jitter part of R20 is a gap inside `rx-clk-quality` (see its `limitations`); R22 is graded by the `rtl-*` benches (the eye monitor lives in #23's RTL).

Regenerate the inventory after editing `bench/benches.json`: `python3 -I sim/bench/gen_inventory.py`, then
`scripts/check-ci.sh --regen` (re-attests items 9 and 10; the cold starts are `local_only`, so CI re-hashes
rather than re-running them).

### Behavioural link benches (R8, R11, R12, R13, R15; issue #93, DR-002)

Cold start, one command per row (numpy + a pinned scipy -- installed into `.venv` by `scripts/setup-env.sh`
at the `bench_install` pins in `layout/toolchain.json`, which `run-bench.sh` resolves by path so the pins hold
even inside `klt signoff --attest 9`'s sanitized cold-start environment; `linkcore.py` prefers scipy's compiled
`erfc` and falls back to `math.erfc` without it, but scipy is a pinned dependency and that fallback is a
per-element Python loop, ~5x slower -- a degraded fallback, not an equivalent option (issue #170); one local
process, no fleet, no `-j`/`-n`); add `--quick` for a short configuration. The cold start exits 0 whenever the bench ran (the verdict, e.g.
`NOT MET`, is in the output and is never relaxed); `--strict` makes a missed threshold exit 3:

    scripts/run-bench.sh link-r8-sensitivity     # python3 -I sim/bench/link_bench.py r8 (27 corners x 16 offset draws; 59 s wall with the pinned scipy, 363 s without it -- measured 2026-11-15 on a 16-vCPU Xeon 8488C shared worker at load 15-27, issue #170)
    scripts/run-bench.sh link-r11-cdr-lock       # r11
    scripts/run-bench.sh link-r12-jtol           # r12 (SJ sweep, 4 edge corners)
    scripts/run-bench.sh link-r13-offset         # r13 (+-300 ppm, 1e6 UI)
    scripts/run-bench.sh link-r15-method         # r15 (27 corners)
    python3 -I sim/bench/test_link_bench.py      # smoke + negative controls

Chain: `sim/rx/records/<newest>/ctle_ac.report.json` (per-corner CTLE gain at 0.1/2.5/5 GHz) -> piecewise CTLE
model -> `spec/channel/channel_model.py` (R14) pulse response -> statistical eye (PRBS-31 as independent symbols)
-> dual-Dirac Q-scale wall/amplitude fit to 1e-12. The time-domain CDR uses `rtl/tests/serdes_ref.CdrFilter`
(bit-exact against the RTL) with KP/KI/FMAX parsed from `rtl/serdes_cdr_filter.v` and the delay parsed from
DR-007; its recovered-clock error feeds the R15 eye. Every printed figure carries its DR-002 label and the record
it is fitted to. **The latch records carry the q swing and regeneration times, but no sampler offset/noise statistics.**
`sim/rx/records/20261114-050716-eb34d10` is the first latch record with no `error` corner: regeneration is measured
to two fixed \|q\| levels, and every corner returns a time to the 0.10 V floor level (1.5-17.5 ps) plus either a
time to the 0.25 V decision level or an explicit `not_reached` verdict. The six 1.080 V corners are `not_reached`
at the decision level -- a swing limit, not a speed limit; no corner in the grid misses the 100 ps first-look limit
(`sim/rx/README.md` § "Regeneration at low supply"). Sampler offset/noise, RJ/DJ, PD decision noise and the analog
loop delay are still printed as `UNFITTED ASSUMPTION`s; they are inputs, not results. Fit validation on held-out corners
(DR-002 step 3) is not done. PVT-edge for R11/R13 is corner-independent in this model (no per-corner PI/sampler
record); the latch/CTLE fits enter R12 through the per-corner eye.
