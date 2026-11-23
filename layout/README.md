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
  - Record convention for a standalone `klt sta` report (#239): a record that
    cites one discloses, beside the clock / `geometry_source` /
    SPEF-or-wire-load model, `constraint_completeness.status`,
    `unconstrained_endpoints.count` and `unclocked_registers.count` per corner,
    and states that a violating-endpoint count is taken over the constrained
    endpoint set only. Read the fields as: `unclocked_registers.count == 0`
    means no register escapes the setup check; a non-zero
    `unconstrained_endpoints.count` means that many endpoints carry no setup
    check in that model. Re-measure with
    `jq -r '.corners[] | [.corner, .constraint_completeness.status, .constraint_completeness.unconstrained_endpoints.count, .constraint_completeness.unclocked_registers.count] | @tsv' <report>`.
  - `lvs.request.json` is the template for the gate-level LVS request (T1 item 4,
    Digital column, `4.digital`). `scripts/lvs-regen.sh` extracts the newest routed
    GDS with every standard cell abstracted (about 15 minutes, single process) and
    compares it to the post-route Verilog into a new dated, append-only
    `lvs-records/<date>-<sha>/`. `scripts/check-lvs-fresh.sh` is the `klt lvs --check`
    freshness gate (exit 3 = a newer place-and-route record or drifted inputs). Analog
    LVS is #128.
  - `erc/digital.erc.json` is the `klt erc` supply spec for the routed digital
    GDS (T1 item 11, Digital column, `11.digital`). `scripts/erc-regen.sh`
    runs `klt erc --findings-only --omit-antenna-tables --deck sg13g2` against
    the newest place-and-route record into a new dated, append-only
    `erc-records/<date>-<sha>/`, with the spec copy it graded committed beside
    the report (the document `klt signoff` re-reads). `scripts/check-erc-fresh.sh`
    is the `klt erc --check` freshness gate (exit 3 = a newer place-and-route
    record or drifted inputs). Neither needs the PDK or `openroad`; the
    PDK-free hash axes are mirrored in `scripts/check-ci.sh`'s `fresh` mode.
    Analog supply ERC stays on #29.
- `analog/rx/` — RX core analog cells (`ctle`, `latch_cml`, `clk_buf_quad`,
  `lvl_cml2cmos`), T1 item 2, Analog column (#112, part of #24).
  `gen_rx_cells.py` reads `design/rx/netlists/rx_top.spice`, builds each device
  with `klt gen` and composes each subckt with `klt gen-compose`;
  `regen.sh` re-runs it into a new dated, append-only `records/<date>-<sha>/`
  (`rx_core.gds` holds all four cells; per-cell GDS and compose requests/reports
  alongside). `lvl_cml2cmos` composes from an explicit per-net route plan
  (issue #199, see "Per-cell analog route plans" below) and is DRC clean +
  LVS match per record; the HBT cells are placed and labelled, intra-cell
  routing partial, nets with an HBT terminal left unrouted (#26). Evidence:
  `manifests/evidence/item2.rx.json`.
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
  name) from `design/tx/netlists/tx_top.spice`: `klt gen` device cells.
  `tx_lvl_cml2cmos` composes from an explicit per-net route plan (issue #199,
  see "Per-cell analog route plans" below) and is DRC clean + LVS match per
  record; the other five cells are shelf-packed with port-named Metal2
  boundary pins — **placement and pins only, no routing** (#26, #27).
  `records/<date>-<sha>/` is append-only; `scripts/tx-core-regen.sh` re-runs
  into a new record. Attestation: `manifests/evidence/item2.analog-tx-core.json`.
- `analog/hbt-recognition/` — routing-independent `npn13G2` recognition
  probe (#196): `klt lvs` (curated deck and the pinned `klayout-runset`)
  and `klt extract` (curated) on the bare PDK cell and the smallest placed
  HBT cell. Outcome (2026-11-20): curated engines extract no HBT (documented
  deck gap); the runset recognises it with C/B/E/S terminals and
  `we/le/Nx/m` parameters — the runset is item 4 analog's engine path
  (#128). `records/<date>-<sha>/` is append-only.
- `toolchain.json` pins klt; `tools.json` pins the RTL-flow tool versions.

## Per-cell analog route plans and per-cell LVS (issue #199, first split of #127)

Two cells are routed end-to-end from a **hand-specified multi-layer plan**:
RX `lvl_cml2cmos` and TX `tx_lvl_cml2cmos` (records `2026-11-21-4ff16d8`,
source commit `4ff16d8`). Per cell: every multi-terminal net drawn connected,
`klt drc --deck sg13g2` `clean`, `klt lvs` against the cell's standalone
subckt (`reference.form: subckt-call`, `options.anchor_top_level_pins: true`)
`match` with the subckt's port set — both supplies included — anchored, and a
scratch negative control (one removed device; one routing plane erased)
yielding `mismatch`. `scripts/analog-lvs-regen.sh` writes the DRC+LVS evidence
into the newest records; `scripts/check-analog-lvs-fresh.sh` is the
`klt lvs --check` freshness gate (exit 3 = a newer generator record without
LVS evidence). This is per-cell evidence under
`manifests/design-evidence-tiers.md` item 4, **not** a partition-level LVS
claim: T1 item 4 (analog) stays with #128 and the unrouted cells stay with
#127.

The recipe for the next cell (what worked, in order):

1. **Floorplan**: two rows of `klt gen` device blocks in columns — nfets in
   row A, pfets (and the well-tie strap) in row B above a channel; a supply
   trunk on each side of the rows; long passives above/below the trunks.
   Body ties: `layout_common.draw_tie_strap` draws the pSD/nSD-marked Activ
   the curated deck derives substrate/well ties from (mos_array has no bulk
   port at klt 0.9.0), and `overlay_nwell_merge` merges the pfet wells with
   the well-tie strap; `assert_ties` fails the build if a tie sits on the
   wrong side of a well.
2. **Plan**: every net gets `layer_role` + `legs[]` (`from_pin`/`to_pin`,
   `waypoints_um` through free corridors). Two planes suffice for these
   cells: put the nets whose trunks must *cross* row-spanning verticals on
   the other plane from them. Supply rails: one leg anchors the trunk (tie
   strap → first device), every other device joins pin-to-trunk.
3. **Pad geometry (what did not work)**: `mos_array`/`res_array` port pads
   are Metal2. (a) A trunk lane offset from the pad centre it feeds draws a
   sliver facing the pad edge — 0.02–0.06 um `metal2/metal3.space.1` markers;
   put trunk lanes **exactly on pad centres** (TX co-aligns each column's
   pfet so its pads share the nfet's x). (b) A supply leg that runs
   horizontally *at pad level* to its drop lane collides with the
   neighbouring S/D pad at the same y; drop vertically off the pad first,
   then run at rail level. (c) A seeded leg whose staircase crosses or
   approaches an already-drawn net (< spacing) is rejected and the router
   silently re-plans that net — the net still reports `routed`, the rejected
   leg carries `reason` in `compose.response.json`; check `legs[]` for
   `reason` to know the plan as written was not what got drawn. All three
   posted as generic data points on `2AMLogic/klayout-tools#1962`
   ([comment](https://github.com/2AMLogic/klayout-tools/issues/1962#issuecomment-7054026274),
   2026-11-21).
4. **Evidence**: run the partition's regen script (new dated record), then
   `scripts/analog-lvs-regen.sh` (DRC + LVS into the record), then the
   negative controls on scratch copies (never committed as evidence), then
   `scripts/check-analog-lvs-fresh.sh`. Fold `options.combine_devices: true`
   into the LVS request when the netlist uses `ng>1` fingers or drawn
   resistors (they extract per-primitive).


## DRC, T1 item 3 (#26)

`klt drc --deck sg13g2` (klayout-tools 0.9.0 via `uvx`, KLayout 0.30.13; the report records `klayout_version_mismatch: true`), curated engine, deck content hash `sha256:1c95db40596afc5412e216009bcf0b775d1d74895b32738447eccbc76336dd15`, run on each partition's committed GDS. Reports sit beside the GDS they checked (`drc.json`); `provenance.input.content_hash` equals the GDS sha256. A GDS-changing fix must go into a new dated record with a regenerated report, never an edit of an old record. Spec is PROPOSED (#2): nothing here is a measurement.

| Partition | Report | status | violations |
|---|---|---|---|
| digital | `layout/digital/records/2026-11-14-d19ba10/drc.json` | `clean` | 0 |
| analog | `layout/analog/top/records/2026-11-12-0193777/drc.json` | `clean` | 0 |

**Digital** is routed by `klt place-and-route`; `clean` means no violations under this deck's scope and coverage below, graded `met` by `klt signoff`.

**Analog** is `clean` on the same terms, but the top is placed only (devices placed and labelled, routing partial or absent), so it says only "no violations in the geometry that exists, under this deck". It does not claim routed, LVS-clean (#27) or extractable. Nets with an HBT terminal are left unrouted in the RX cells (see below), so there is less routing than before, not more.

The previous analog record (`2026-11-11-6b21302`, 830 violations, report kept) was not a deck false positive. Two layout defects caused it, fixed in `analog/rx/gen_rx_cells.py` and a new RX record plus a new top record (old records untouched):
1. `clk_buf_quad`'s mirrored `b` devices overlapped their `a` partners: `gen-compose` `mirror_x` flips x (GDS `m90`), so a block placed at origin `x` occupied `[x - w, x]` (4 `gatpoly.space.1` and 4 `metal1.space.1` markers).
2. `gen-compose` routing dropped via1/metal1 stubs inside the `npn13G2` cell's own via array, 15 nm from existing vias (826 `metal1/metal2/via1.space.1` markers, attributed to the foundry cell as `source_cell`). The same cells unrouted, and a single HBT device alone, are clean. Gap filed at `2AMLogic/klayout-tools#5398`, which closed as completed 2026-11-12 via upstream PR #5399 — first released in `v0.9.2`, above this repo's pinned `0.9.0`, so the fix is not in effect at the pin; the underlying routing gap remains open (`klayout-tools#1962`, as of 2026-11-15). This corrects the earlier "possible deck false positive" reading (`klayout-tools#5386`, closed with the cause unverified, measured 0 markers on bare foundry cells).

**Negative control**: `drc-negative-control.json` beside the analog report re-runs the same deck with the previous analog top as the control layout; the deck finds its 830 violations (`gatpoly.space.1`, `metal1.space.1`, `metal2.space.1`, `via1.space.1`), so `clean` is not vacuous. The deck did not fail on the layers listed under `layers_in_stream_without_rules` below, which it has no rules for; those are uncovered, not clean.

**KLayout version**: the reports record `klayout_version_mismatch: true` (KLayout 0.30.13 against the engine's tested version). Per `klayout-tools` docs (PR 5395) it changes no verdict; engine-dependent report details (deck hash, `rules_skipped`, category counts) may differ from the tested engine. We did not run the official engine, so no cross-engine comparison is claimed.

### Coverage, quoted verbatim from each report

**digital**
- `coverage.layers_in_stream_without_rules`: `["8/2", "8/25", "30/2", "30/25", "63/0", "99/31", "134/2", "134/25", "189/4"]`
- `coverage.rules_skipped`: `["metal5.enclosing.mim.1", "mim.enclosing.topvia1.1", "nwell.enclosing.nactiv.1", "nwell.enclosing.nactiv.dig.1", "nwell.enclosing.nactiv.hv.1", "nwell.space.nactiv.1", "nwell.space.nactiv.dig.1", "nwell.space.nactiv.hv.1"]`
- `coverage.deck_scope`: `["Act", "Cnt", "Gat", "M1", "M2", "M3", "M4", "M5", "MIM", "NW", "TM1", "TM2", "TV1", "TV2", "V1", "V2", "V3", "V4", "pSD"]`

**analog**
- `coverage.layers_in_stream_without_rules`: `["5/1", "7/21", "8/2", "8/25", "9/0", "10/2", "10/25", "24/0", "26/0", "28/0", "30/25", "33/0", "41/0", "51/0", "63/0", "99/30", "99/31", "111/0", "128/0", "129/0"]`
- `coverage.rules_skipped`: `["nwell.enclosing.nactiv.1", "nwell.enclosing.nactiv.dig.1", "nwell.enclosing.nactiv.hv.1", "nwell.space.nactiv.1", "nwell.space.nactiv.dig.1", "nwell.space.nactiv.hv.1"]`
- `coverage.deck_scope`: `["Act", "Cnt", "Gat", "M1", "M2", "M3", "M4", "M5", "MIM", "NW", "TM1", "TM2", "TV1", "TV2", "V1", "V2", "V3", "V4", "pSD"]`
