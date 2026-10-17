# sim

Simulation toolchain, pins and evidence. See the repo README "Bring-up" for the
reproduce steps.

| Path | What |
|---|---|
| `pdk.json` | PDK pin (IHP-Open-PDK v0.3.0, tarball sha256) and OSDI toolchain fact sheet |
| `toolchain.json` | simulator floors |
| `tools/build-osdi.sh` | compiles the PDK's Verilog-A sources (PSP103, r3_cmc, mosvar) with a checksum-pinned OpenVAF-Reloaded; exit 5 = built, but the host ngspice cannot load OSDI v0.4 |
| `smoke/` | toolchain smoke grid: HBT Gummel at every HBT corner section, MOS inverter DC at `tt/ff/ss/fs/sf`, and a mixed MOS+HBT transient. Placeholder devices, not design values |
| `smoke/records/<id>/` | append-only run records (reports, `record.md`); never edited after the fact |
| `harness/` | fetched by `scripts/setup-env.sh` per `reuse.lock.json` (gitignored, never committed) |

## HBT models

The SG13G2 HBT (`npn13G2`, VBIC) is built into ngspice and needs no OSDI. The PDK
provides corner sections `hbt_typ`, `hbt_bcs`, `hbt_wcs` plus `_mismatch` /
`_stat` Monte Carlo variants in `cornerHBT.lib`. MOS devices (PSP103) need the
OSDI models and `cornerMOSlv.lib` sections `mos_tt/ff/ss/fs/sf`.

## Known gaps (tool issues filed on 2AMLogic/klayout-tools)

- [#3818](https://github.com/2AMLogic/klayout-tools/issues/3818): batch jobs that stage `.osdi` inputs exit 2 with no diagnostic. This is why the MOS and mixed smoke runs in the first record are `error`, not `pass`.
- [#3819](https://github.com/2AMLogic/klayout-tools/issues/3819): the submit-time OSDI ABI check judges the client's ngspice, not the worker's.

## PDK pin

Every record under `smoke/records/` traces to `pdk.json`; a bump to that file
is a new decision, not an edit of an earlier record.
