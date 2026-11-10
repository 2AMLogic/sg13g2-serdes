# sim

Simulation toolchain, pins and evidence. See the repo README "Bring-up" for the
reproduce steps.

| Path | What |
|---|---|
| `pdk.json` | PDK pin (IHP-Open-PDK v0.3.0, tarball sha256) |
| `toolchain.json` | simulator floors |
| `tools/build-osdi.sh` | compiles the PDK's Verilog-A sources (PSP103, r3_cmc, mosvar) with a checksum-pinned OpenVAF-Reloaded; exit 5 = built, but the host ngspice cannot load OSDI v0.4 |
| `smoke/` | toolchain smoke grid: HBT Gummel at every HBT corner section, MOS inverter DC at `tt/ff/ss/fs/sf`, and a mixed MOS+HBT transient. Placeholder devices, not design values |
| `smoke/records/<id>/` | append-only run records (reports, `record.md`); never edited after the fact |
| `rx/` | RX sizing benches (CTLE AC per setting, latch regeneration at 5 GHz, HBT node stress, termination first look). `rx/tools/gen_requests.py` writes the bench bodies and `klt sim` requests; `rx/run_sizing.sh` submits the 27-point HBT PVT grid to the batch fleet and writes `rx/records/<id>/` (append-only). Sizing evidence, not spec results |
| `tx/` | TX sizing decks, requests and append-only records (issue #21); see `tx/README.md` |
| `bench/` | testbench registry for T1 item 9: `benches.json` (one entry per bench: spec rows, requests, corner set, declared measurements) and `gen_inventory.py`, which derives `verification/testbench-inventory.json` from it |
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
this item (recording is T1 item 5).

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
| `rtl-*` (8) | R22, R11 (digital), R2 | functional | `rtl/tests/test_*.py` |

Each bench's `limitations` field in `bench/benches.json` states what it does not cover. Pad model for
R6/R9: the placeholder in `rx/pad_ac` (ideal resistors, placeholder pad capacitance).

**Declared gaps** (inventory `unbenched_rows`, none silently omitted): R6, R20 (#92); R8 statistical eye,
R12, R13, R15 (#93); R18, R19 (#94, PDK `bondpad` is an empty placeholder). Not simulation rows: R1 (graded by R15),
R14 (committed model), R17, R21; R22 is graded by the `rtl-*` benches (the eye monitor lives in #23's RTL).

Regenerate the inventory after editing `bench/benches.json`: `python3 -I sim/bench/gen_inventory.py`, then
`scripts/check-ci.sh --regen` (re-attests items 9 and 10; the cold starts are `local_only`, so CI re-hashes
rather than re-running them).
