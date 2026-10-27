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
| `harness/` | fetched by `scripts/setup-env.sh` per `reuse.lock.json` (gitignored, never committed) |

## HBT models

The SG13G2 HBT (`npn13G2`, VBIC) is built into ngspice and needs no OSDI. The PDK
provides corner sections `hbt_typ`, `hbt_bcs`, `hbt_wcs` plus `_mismatch` /
`_stat` Monte Carlo variants in `cornerHBT.lib`. MOS devices (PSP103) need the
OSDI models and `cornerMOSlv.lib` sections `mos_tt/ff/ss/fs/sf`.

## Known gaps (tool issues filed on 2AMLogic/klayout-tools)

- [#3818](https://github.com/2AMLogic/klayout-tools/issues/3818): batch jobs that stage `.osdi` inputs exit 2 with no diagnostic. This is why the MOS and mixed smoke runs in the first record are `error`, not `pass`.
- [#3819](https://github.com/2AMLogic/klayout-tools/issues/3819): the submit-time OSDI ABI check judges the client's ngspice, not the worker's.

- PDK resistors (`rsil`, `rppd`) are `r3_cmc` OSDI models, so they cannot be simulated either; `design/rx` uses ideal resistors and records that.

## PDK pin

Every record under `smoke/records/` and `rx/records/` traces to `pdk.json`; a bump to that file
is a new decision, not an edit of an earlier record.
