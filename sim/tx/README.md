# sim/tx

PVT-edge sizing evidence for the TX high-speed path (issue #21). **Sizing evidence, not
a spec result and not a measurement.**

| Path | What |
|---|---|
| `make_tb.py` | generates the decks and requests below from `design/tx/netlists/` |
| `tx_sizing_ffe{0,1}_{typ,bcs,wcs}.sp` / `.request.json` | six `klt sim` requests, each 3 supplies (1.08/1.2/1.32 V) x 3 temperatures (-40/27/125 C) = 54 corners; FFE off or all three post-cursor slices on; HBT, capacitor and resistor corners move together |
| `tx_mos_{mux2to1_cml,tx_lvl_cml2cmos,ffe_en}.sp` / `.request.json` | three MOS-cell `klt sim` requests (issue #80), each 5 process pairings x 3 supplies x 3 temperatures = 45 corners; PSP103 and the real `r3_cmc` resistors via `osdi_preload` |
| `run_sizing.sh [mos]` | runs the six HBT requests, or with `mos` the three MOS requests (batch fleet via `KLT_SIM_BACKEND=batch`; no local fallback) and writes `records/<id>/` (`<id>-mos/` for the MOS set) |
| `make_record.py` / `make_record_mos.py` | render `records/<id>/record.md` for the HBT / MOS set |
| `records/<id>/` | append-only run records; never edited after the fact |

Reproduce: `source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh`.
Every record traces to `sim/pdk.json`.

What runs, HBT set: `bias`, `predriver` (x2) and `driver_ffe`. The PDK `rsil` there is a
behavioural resistor from the PDK symbol's formula. The batch worker did not honour
`corners.params` (it returned 27 corner reports for 162 dispatched points,
`params_unsupported_worker`), so FFE and the resistor corner are baked into six decks
instead of being a parameter axis.

What runs, MOS set (the blocker #3 was cleared by PR #76; same `osdi_preload` as
`sim/smoke/mixed_tran.request.json`; `rsil`/`rppd` are the real `r3_cmc` models, no
behavioural resistor):

| Cell | Bench | Measured |
|---|---|---|
| `mux2to1_cml` | ideal 5 GHz complementary clock (0.4 V swing, an assumption), A held 1 / B held 0 so the output is a 1010 stream, loaded by the `predriver` main input + 20 fF | differential swing, rise/fall between fixed +-30 mV crossings (not a conforming 20-80 %), collector V and reverse Vbe per HBT, Vce |
| `tx_lvl_cml2cmos` | ideal 2.5 GHz CML input (300 mV), 20 fF load | CMOS high/low, duty, propagation delay |
| `ffe_en` | enable codes 000, 001, 011, 111 stepped, vbn from the real `bias` cell, vbp unloaded | `vbp0..2` against `vbn` per code |

Corner pairing (MOS / HBT / CAP / RES sections moved together): `mos_tt`/`hbt_typ`,
`mos_ff`/`hbt_bcs`, `mos_ss`/`hbt_wcs`, and `mos_fs`, `mos_sf` with the typical
HBT/CAP/RES (no HBT skew exists for them). Parameter axes are baked into the decks.

MOS-set run status: the first run, `records/20261106-054913-a506fea-mos/`, did not simulate
anything. The fleet runner is klt 0.9.0 and the pinned client is 0.8.0, so all 135 units
returned `batch_runner_version_mismatch`. The results are an open item until the pin and the
runner agree; there is no local fallback.
