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
- `analog/rx/` — RX core analog cells (`ctle`, `latch_cml`, `clk_buf_quad`,
  `lvl_cml2cmos`), T1 item 2, Analog column (#112, part of #24).
  `gen_rx_cells.py` reads `design/rx/netlists/rx_top.spice`, builds each device
  with `klt gen` and composes each subckt with `klt gen-compose`;
  `regen.sh` re-runs it into a new dated, append-only `records/<date>-<sha>/`
  (`rx_core.gds` holds all four cells; per-cell GDS and compose requests/reports
  alongside). Devices are placed and labelled; intra-cell routing is partial
  (see each record's `summary.json`). No DRC/LVS/extraction claim yet (#26, #27).
  Evidence: `manifests/evidence/item2.rx.json`.
- Other analog/CML groups (TX, pads/ESD) are not here yet (issue #24).
- `toolchain.json` pins klt; `tools.json` pins the RTL-flow tool versions.
