# layout

- `digital/` — place-and-route of the digital partition (`serdes_digital_top`),
  T1 item 2, Digital column. `place-and-route.request.json` is the committed
  `klt place-and-route` request (input: `rtl/synth/serdes_digital_top_synth.v`;
  PDN, floorplan, IO layers and clock in the request). `records/<date>-<sha>/`
  holds the routed GDS, DEF, post-route netlist and report, append-only.
  - `scripts/pnr-regen.sh` re-runs the flow into a new dated record.
  - `scripts/check-pnr-fresh.sh` checks the newest record against the netlist
    (exit 3 = stale). Needs the PDK (`scripts/setup-env.sh`) and `openroad`, so
    it is not part of `scripts/check-ci.sh`.
- `analog/tx/` — analog layout of the TX CML core cells (`bias`, `ffe_en`,
  `mux2to1_cml`, `predriver`, `driver_ffe`, `tx_lvl_cml2cmos`), T1 item 2,
  Analog column. `gen_tx_core.py` builds one GDS per subckt (cell name = subckt
  name) from `design/tx/netlists/tx_top.spice`: `klt gen` device cells, shelf
  placed, with port-named Metal2 boundary pins. **Placement and pins only: no
  routing, so no DRC/LVS/extraction claim** (#26, #27). `records/<date>-<sha>/`
  is append-only; `scripts/tx-core-regen.sh` re-runs into a new record.
  Attestation: `manifests/evidence/item2.analog-tx-core.json`. RX and pad/ESD
  analog layout are not here yet (issues #112, #113).
- `toolchain.json` pins klt; `tools.json` pins the RTL-flow tool versions.
