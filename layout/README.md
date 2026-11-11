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
- `analog/pads/` — pad/ESD cells `pad_esd` and `rx_term_pad` (issue #113):
  PDK bondpad/ESD-diode cells and `klt gen res_array` resistors, placed and
  net-labelled only (no routing, DRC, LVS or capacitance claim).
  `regen.sh` writes a new dated, append-only record. The analog top assembly
  waits on the TX/RX core records (#110, #112).
- `toolchain.json` pins klt; `tools.json` pins the RTL-flow tool versions.
