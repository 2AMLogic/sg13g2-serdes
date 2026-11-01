# sim/tx

PVT-edge sizing evidence for the TX high-speed path (issue #21). **Sizing evidence, not
a spec result and not a measurement.**

| Path | What |
|---|---|
| `make_tb.py` | generates the decks and requests below from `design/tx/netlists/` |
| `tx_sizing_ffe{0,1}_{typ,bcs,wcs}.sp` / `.request.json` | six `klt sim` requests, each 3 supplies (1.08/1.2/1.32 V) x 3 temperatures (-40/27/125 C) = 54 corners; FFE off or all three post-cursor slices on; HBT, capacitor and resistor corners move together |
| `run_sizing.sh` | runs the six requests (batch fleet via `KLT_SIM_BACKEND=batch`; no local fallback) and writes `records/<id>/` |
| `make_record.py` | renders `records/<id>/record.md` |
| `records/<id>/` | append-only run records; never edited after the fact |

Reproduce: `source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh`.
Every record traces to `sim/pdk.json`.

What runs: `bias`, `predriver` (x2) and `driver_ffe`. What does not (MOS needs OSDI; see
`sim/README.md` known gaps, #3): `mux2to1_cml`, `ffe_en`, `lvl_cml2cmos`. The PDK `rsil`
is an OSDI (`r3_cmc`) model, so the decks use a behavioural resistor from the PDK symbol's
formula. The batch worker did not honour `corners.params` (it returned 27 corner reports for
162 dispatched points, `params_unsupported_worker`), so FFE and the resistor corner are baked
into six decks instead of being a parameter axis.
