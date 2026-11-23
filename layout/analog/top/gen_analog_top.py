#!/usr/bin/env python3
"""Assemble the analog top cell `serdes_analog_top` (T1 item 2, Analog column).

Composition (partition_boundary.analog in manifests/sg13g2-serdes.signoff.json):
  tx_top = TX core cells (tx_core_lib.gds) + `pad_esd`   (pad_esd.gds)
  rx_top = RX core cells (rx_core.gds)     + `rx_term_pad` (rx_term_pad.gds)
Inputs are the newest committed records under layout/analog/{tx,rx,pads}/records/
(or pass --tx/--rx/--pads record dirs); they are read, never modified.

Cells are PLACED only (shelf placement, instance names = cell names). Nothing is
routed between cells and no DRC, LVS, extraction, capacitance or 5 GHz claim is
made: the core-to-pad seam is "placed" (pad model is #94; DRC #26, LVS #27).
The pad cells keep the net labels (cp/cn, padp/padn, inp/inn, vcm) they were
generated with.

Usage: gen_analog_top.py OUTDIR      (needs only klayout.db; no PDK)
"""
import glob, json, os, sys
import klayout.db as kdb

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
GAP_UM = 20.0
ROW_GAP_UM = 60.0

INPUTS = {   # group -> (record glob, stream) per tx_top / rx_top member
    "tx_top": [("tx", "tx_core_lib.gds"), ("pads", "pad_esd.gds")],
    "rx_top": [("rx", "rx_core.gds"), ("pads", "rx_term_pad.gds")],
}


def newest(group):
    recs = sorted(glob.glob(os.path.join(ROOT, group, "records", "*")))
    if not recs:
        sys.exit(f"no records under layout/analog/{group}/records")
    return recs[-1]


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(out, exist_ok=True)
    ly = kdb.Layout()
    ly.dbu = 0.001
    top = ly.create_cell("serdes_analog_top")
    opt = kdb.LoadLayoutOptions()
    # PDK sub-cells with colliding names get distinct names instead of being dropped
    opt.cell_conflict_resolution = kdb.LoadLayoutOptions.CellConflictResolution.RenameCell
    sources, y, partition = [], 0.0, {}
    for part, members in INPUTS.items():
        sub = ly.create_cell(part)
        top.insert(kdb.CellInstArray(sub.cell_index(), kdb.Trans(0, int(round(y / ly.dbu)))))
        x, h, placed = 0.0, 0.0, []
        for group, stream in members:
            path = os.path.join(newest(group), stream)
            src = kdb.Layout()
            src.read(path)
            before = {c.name for c in ly.each_cell()}
            ly.read(path, opt)
            tops = [c for c in src.top_cells()]
            sources.append({"stream": os.path.relpath(path, os.path.join(ROOT, "..", "..")),
                            "top_cells": [c.name for c in tops]})
            for t in tops:
                cell = ly.cell(t.name) if t.name not in before else None
                if cell is None:   # renamed on conflict: find the newest same-prefixed cell
                    cell = [c for c in ly.each_cell() if c.name.startswith(t.name)
                            and c.name not in before][-1]
                bb = cell.dbbox()
                dx = int(round((x - bb.left) / ly.dbu))
                dy = int(round((0.0 - bb.bottom) / ly.dbu))
                sub.insert(kdb.CellInstArray(cell.cell_index(), kdb.Trans(dx, dy)))
                placed.append({"cell": cell.name, "x_um": round(x, 3), "y_um": 0.0,
                               "w_um": round(bb.width(), 3), "h_um": round(bb.height(), 3)})
                x += bb.width() + GAP_UM
                h = max(h, bb.height())
        partition[part] = placed
        y += h + ROW_GAP_UM
    ly.write(os.path.join(out, "serdes_analog_top.gds"))
    summary = {"top": "serdes_analog_top", "partition": partition, "sources": sources,
               "claims": "placed only; no routing/DRC/LVS/extraction/capacitance/5 GHz claim"}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
