# Analog top assembly record, 2026-11-12 (source commit 0193777)

Append-only. Re-run with `layout/analog/top/regen.sh` into a new dated directory.

| Item | Value |
|---|---|
| Generator | `layout/analog/top/gen_analog_top.py` (klayout.db only, no PDK) |
| Top cell | `serdes_analog_top` = `tx_top` + `rx_top` |
| `tx_top` | TX core cells (`tx_core_lib.gds`, 2026-11-11-835e58e) + `pad_esd` (pads, 2026-11-12-fc8a7fa) |
| `rx_top` | RX core cells (`rx_core.gds`, 2026-11-12-0193777) + `rx_term_pad` (pads, 2026-11-12-fc8a7fa) |
| Attestation | `manifests/evidence/item2.analog-top.json` (`klt signoff --attest 2`, klt 0.9.0) |
| DRC | `drc.json` (`status: clean`, 0 violations); negative control `drc-negative-control.json` (#26) |

## Partition label

Item 2 is graded per partition. This record is the **analog** partition as
declared in `partition_boundary.analog` of `manifests/sg13g2-serdes.signoff.json`
(HBT CML from the serial pad down to the 625 MHz word boundary, including both
level converters, plus pads and ESD). The **digital** partition is
`layout/digital/records/2026-11-10-f6fe587/serdes_digital_top.gds`
(`partition_boundary.digital`: the `rtl/serdes_digital_top.v` hierarchy), cited
by `manifests/evidence/item2.json` under evidence key `2.digital`. This record
is cited under `2.analog`. The seam between them is DR-008's word boundary;
no analog-to-digital interconnect is drawn here.

## What this is

Input records are read, never modified. Cells are **placed** (shelf placement,
20 um gaps; `tx_top` row at y=0, `rx_top` row above it), instance names are the
cell names, and the pad cells keep their net labels (`cp`/`cn`, `padp`/`padn`,
`inp`/`inn`, `vcm`). Nothing is routed between cells. The core-to-pad seam is
**placed** only: no capacitance or 5 GHz claim (pad model #94), and no LVS (#27) or
extraction claim. DRC is item 3 (#26): see `drc.json` and `layout/README.md`.

Re-running into a scratch directory gives a stream `klt diff` reports
`equivalent` (bytes differ only by GDS write timestamps), and an identical
`summary.json`. The attestation therefore records no `regeneration` hash.

## Why this record supersedes 2026-11-11-6b21302 (#26)

That record's DRC report had 830 violations. Two layout defects, both fixed in
`layout/analog/rx/gen_rx_cells.py` (new RX record `2026-11-12-0193777`); the old
records are untouched:

1. **Overlapping HBT pairs in `clk_buf_quad`.** `gen-compose` `mirror_x` is the
   x -> -x flip (GDS `m90`), so each mirrored `b` device occupied
   `[origin - w, origin]`, 12.4 um on top of its `a` partner, with 0.16 um
   notches between the resistor pairs (the 4 `gatpoly.space.1` + 4 `metal1.space.1`
   markers). Mirrored devices now sit at the right edge of their slot.
2. **Routed via stacks inside the HBT.** `gen-compose` landed via1/metal1 stubs on
   `npn13G2` terminals inside the PDK cell's own via array (15 nm from existing
   vias). The markers named the foundry cell as `source_cell` but were caused by
   that routing: the same cells with no routing are clean, and a single HBT
   device alone is clean. Nets with an HBT terminal are now left unrouted (pins
   stay labelled), so intra-cell routing is thinner than before. This is
   not a deck false positive; the tool gap is filed at `2AMLogic/klayout-tools`.

The newest pad record (`2026-11-12-fc8a7fa`) is also picked up by the generator,
so this GDS differs from the old one for that reason too.
