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
  - `lvs.request.json` is the template for the gate-level LVS request (T1 item 4,
    Digital column, `4.digital`). `scripts/lvs-regen.sh` extracts the newest routed
    GDS with every standard cell abstracted (about 15 minutes, single process) and
    compares it to the post-route Verilog into a new dated, append-only
    `lvs-records/<date>-<sha>/`. `scripts/check-lvs-fresh.sh` is the `klt lvs --check`
    freshness gate (exit 3 = a newer place-and-route record or drifted inputs). Analog
    LVS is #128.
- `analog/rx/` — RX core analog cells (`ctle`, `latch_cml`, `clk_buf_quad`,
  `lvl_cml2cmos`), T1 item 2, Analog column (#112, part of #24).
  `gen_rx_cells.py` reads `design/rx/netlists/rx_top.spice`, builds each device
  with `klt gen` and composes each subckt with `klt gen-compose`;
  `regen.sh` re-runs it into a new dated, append-only `records/<date>-<sha>/`
  (`rx_core.gds` holds all four cells; per-cell GDS and compose requests/reports
  alongside). Devices are placed and labelled; intra-cell routing is partial
  (see each record's `summary.json`). No DRC/LVS/extraction claim yet (#26, #27).
  Evidence: `manifests/evidence/item2.rx.json`.
- `analog/pads/` — pad/ESD cells `pad_esd` and `rx_term_pad` (issue #113):
  PDK bondpad/ESD-diode cells and `klt gen res_array` resistors, placed and
  net-labelled only (no routing, DRC, LVS or capacitance claim).
  `regen.sh` writes a new dated, append-only record.
- `analog/top/` — analog top `serdes_analog_top` (`tx_top` + `rx_top`: TX/RX
  core cells plus the pad cells), placed only, T1 item 2, Analog column (#113,
  part of #24). `gen_analog_top.py` reads the newest `tx`/`rx`/`pads` records;
  `regen.sh` writes a new dated, append-only record. Evidence:
  `manifests/evidence/item2.analog-top.json`, cited as `2.analog`.
- `analog/tx/` — analog layout of the TX CML core cells (`bias`, `ffe_en`,
  `mux2to1_cml`, `predriver`, `driver_ffe`, `tx_lvl_cml2cmos`), T1 item 2,
  Analog column. `gen_tx_core.py` builds one GDS per subckt (cell name = subckt
  name) from `design/tx/netlists/tx_top.spice`: `klt gen` device cells, shelf
  placed, with port-named Metal2 boundary pins. **Placement and pins only: no
  routing, so no DRC/LVS/extraction claim** (#26, #27). `records/<date>-<sha>/`
  is append-only; `scripts/tx-core-regen.sh` re-runs into a new record.
  Attestation: `manifests/evidence/item2.analog-tx-core.json`.
- `toolchain.json` pins klt; `tools.json` pins the RTL-flow tool versions.

## DRC, T1 item 3 (#26)

`klt drc --deck sg13g2` (klayout-tools 0.9.0 via `uvx`, KLayout 0.30.13; the report records `klayout_version_mismatch: true`), curated engine, deck content hash `sha256:1c95db40596afc5412e216009bcf0b775d1d74895b32738447eccbc76336dd15`, run on each partition's committed GDS. Reports sit beside the GDS they checked (`drc.json`); `provenance.input.content_hash` equals the GDS sha256. A GDS-changing fix must go into a new dated record with a regenerated report, never an edit of an old record. Spec is PROPOSED (#2): nothing here is a measurement.

| Partition | Report | status | violations |
|---|---|---|---|
| digital | `layout/digital/records/2026-11-10-f6fe587/drc.json` | `clean` | 0 |
| analog | `layout/analog/top/records/2026-11-11-6b21302/drc.json` | `violations` | 830 |

**Digital** is routed by `klt place-and-route`; `clean` means no violations under this deck's scope and coverage below, graded `met` by `klt signoff`.

**Analog is `violations`, so item 3 is graded `unmet` (not waived).** The top is placed only (devices placed and labelled, routing partial or absent), so even a clean run would say only "no violations in the geometry that exists, under this deck"; it would not claim routed, LVS-clean (#27) or extractable. Violations by rule: `gatpoly.space.1` 4, `metal1.space.1` 139, `metal2.space.1` 135, `via1.space.1` 552. Of 830, 826 are inside the PDK-supplied `npn13G2_base` cell hierarchy and 4+4 are in `clk_buf_quad` (`gatpoly.space.1`, `metal1.space.1`). Whether the curated deck should flag the foundry HBT cell internals is **unverified**; the tool gap is filed at `2AMLogic/klayout-tools#5386` and no waiver is applied.

### Coverage, quoted verbatim from each report

**digital**
- `coverage.layers_in_stream_without_rules`: `["8/2", "8/25", "30/2", "30/25", "63/0", "99/31", "134/2", "134/25", "189/4"]`
- `coverage.rules_skipped`: `["metal5.enclosing.mim.1", "mim.enclosing.topvia1.1", "nwell.enclosing.nactiv.1", "nwell.enclosing.nactiv.dig.1", "nwell.enclosing.nactiv.hv.1", "nwell.space.nactiv.1", "nwell.space.nactiv.dig.1", "nwell.space.nactiv.hv.1"]`
- `coverage.deck_scope`: `["Act", "Cnt", "Gat", "M1", "M2", "M3", "M4", "M5", "MIM", "NW", "TM1", "TM2", "TV1", "TV2", "V1", "V2", "V3", "V4", "pSD"]`

**analog**
- `coverage.layers_in_stream_without_rules`: `["5/1", "7/21", "8/2", "8/25", "9/0", "10/2", "10/25", "24/0", "26/0", "28/0", "30/25", "33/0", "41/0", "51/0", "63/0", "99/30", "111/0", "128/0", "129/0"]`
- `coverage.rules_skipped`: `["metal5.enclosing.topvia1.1", "mim.enclosing.topvia1.1", "nwell.enclosing.nactiv.1", "nwell.enclosing.nactiv.dig.1", "nwell.enclosing.nactiv.hv.1", "nwell.space.nactiv.1", "nwell.space.nactiv.dig.1", "nwell.space.nactiv.hv.1", "topmetal1.enclosing.topvia1.1", "topmetal1.enclosing.topvia2.1", "topmetal2.enclosing.topvia2.1", "topvia1.space.1", "topvia1.width.1", "topvia2.space.1", "topvia2.width.1"]`
- `coverage.deck_scope`: `["Act", "Cnt", "Gat", "M1", "M2", "M3", "M4", "M5", "MIM", "NW", "TM1", "TM2", "TV1", "TV2", "V1", "V2", "V3", "V4", "pSD"]`
