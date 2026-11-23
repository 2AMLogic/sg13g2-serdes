#!/usr/bin/env python3
"""Generate the pad/ESD cells `pad_esd` (TX) and `rx_term_pad` (RX).

Netlists: design/tx/netlists/pad_esd.spice, design/rx/netlists/rx_term_pad.spice.
Geometry sources:
  * bondpad, diodevdd_2kv, diodevss_2kv: the PDK's own fixed cells in
    libs.ref/sg13g2_pr/gds/sg13g2_pr.gds, placed as-drawn (`klt gen-compose`
    blocks[].cell). `klt gen --list-pdk-pcells` offers no SG13G2 pcells in this
    install (the PDK's pycell4klayout-api submodule is absent from the release
    tarball), so the fixed GDS cells are the PDK's own source available here.
  * rsil series/termination resistors: `klt gen res_array` (poly rsil flavour).
Cells are PLACED and net-labelled (`pins[]`). Diodes carry the Recog.diode marker
(99/31) so they extract; pad_esd also straps the pad net (resistor B, both diode PAD
pins, bondpad) through a Metal2..TopMetal1 stack (#131). No LVS and no 5 GHz claim is
made (LVS #27, pad model #94); extracted capacitance is interconnect only. The
Cpad_p/Cpad_n 50 fF elements of rx_term_pad are pad-capacitance model elements,
not drawn devices, so they have no layout.

Usage: gen_pad_cells.py OUTDIR   (source scripts/env.sh first)
"""
import json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from layout_common import parse_subckts, run_klt as run

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PDK = "ihp-sg13g2"
PR_GDS = os.path.join(os.environ.get("PDK_ROOT", ""), PDK, "libs.ref/sg13g2_pr/gds/sg13g2_pr.gds")
RSIL_OHM_SQ = 7.0     # nominal rsil sheet resistance used only to size bodies (not verified)
GAP = 5.0             # um between placed blocks


def netlist_devices(path, sub):
    return parse_subckts(path)[sub]["devs"]


def res_block(out, cell, name, w, l):
    gds = os.path.join(out, cell, f"{name}.gds")
    rep = run(["klt", "gen", "res_array", "--pdk", PDK, "--params",
               json.dumps({"num": 1, "dummy": 0, "width_um": w, "length_um": l}),
               "--cell-name", f"{cell}_{name}", "-o", gds, "--format", "json"])
    rep["gds_path"] = gds
    return {"id": name, "generator_report": rep}


def lib_block(name, cell_name, ports):
    return {"id": name, "cell": {"gds_path": PR_GDS, "cell_name": cell_name, "ports": ports}}


def diode_ports(kind):
    # label positions from the PDK cell (text layer 63/0); PAD is the left edge
    pad = (-0.32, 18.535) if kind == "vdd" else (-0.28, 18.525)
    return [{"name": "PAD", "x_um": pad[0], "y_um": pad[1]}]


RECOG_DIODE = (99, 31)   # Recog.diode: the sg13g2 extraction deck's diode device marker
ACTIV = (1, 0)


def add_diode_markers(gds, top):
    """Draw Recog.diode (99/31) over each placed diodevdd_2kv/diodevss_2kv.

    The PDK cells carry Recog.esd (99/30) but not Recog.diode, which the klt sg13g2
    deck requires for dantenna/dpantenna recognition (it is a user-drawn marker),
    so without it both clamps extract as no device. The marker covers the Activ
    bbox of each diode instance; it is a recognition layer, not a mask layer.
    Returns the number of markers drawn.
    """
    import klayout.db as db
    ly = db.Layout()
    ly.read(gds)
    tc = ly.cell(top)
    act = ly.layer(*ACTIV)
    mk = ly.layer(*RECOG_DIODE)
    n = 0
    for inst in list(tc.each_inst()):
        cn = inst.cell.name
        if cn.endswith("diodevdd_2kv") or cn.endswith("diodevss_2kv"):
            tc.shapes(mk).insert(inst.cell.bbox_per_layer(act).transformed(inst.trans))
            n += 1
    ly.write(gds)
    return n


# Metal/via stack under the bondpad (layer numbers from the klt sg13g2 extraction deck).
M1, M2, M3, M4, M5, TM1 = (8, 0), (10, 0), (30, 0), (50, 0), (67, 0), (126, 0)
V1, V2, V3, V4, TV1, TV2 = (19, 0), (29, 0), (49, 0), (66, 0), (125, 0), (133, 0)
# (via layer, via size um, via pitch um, lower metal, upper metal); sizes/spaces are the
# `klt deck rules --deck sg13g2` values (V2-V4 0.19/0.22, TV1 0.42/0.42, TV2 0.9/1.06).
STACK = [(V2, 0.19, 0.41, M2, M3), (V3, 0.19, 0.41, M3, M4), (V4, 0.19, 0.41, M4, M5),
         (TV1, 0.42, 0.84, M5, TM1), (TV2, 0.9, 1.96, TM1, None)]
PLATE = (14.0, 70.0, 26.0, 82.0)   # um, relative to the leg origin x0; inside the bondpad


def _box(cell, ly, lay, x0, y0, x1, y1):
    import klayout.db as db
    cell.shapes(ly.layer(*lay)).insert(db.DBox(x0, y0, x1, y1))


def _via_array(tc, ly, lay, size, pitch, x0, y0, x1, y1):
    """Centred array of size x size vias fully inside [x0,x1]x[y0,y1]."""
    nx = int((x1 - x0 - size) / pitch) + 1
    ny = int((y1 - y0 - size) / pitch) + 1
    ox = x0 + ((x1 - x0) - ((nx - 1) * pitch + size)) / 2
    oy = y0 + ((y1 - y0) - ((ny - 1) * pitch + size)) / 2
    for i in range(nx):
        for j in range(ny):
            _box(tc, ly, lay, ox + i * pitch, oy + j * pitch,
                 ox + i * pitch + size, oy + j * pitch + size)
    return nx * ny


def strap_pad_net(gds, top, legs):
    """Tie, per leg, the seam resistor pad-side terminal, both ESD-diode PAD terminals and
    the bondpad into one net (the pad net) with M1/M2 straps and a Metal2..TopMetal1 via
    stack landing under the bondpad's TopMetal2. legs: {leg: x0_um}. Returns via counts.

    Geometry is relative to each leg origin x0 (diodes at x0-2.12 / x0+14, y=15; see
    build_pad_esd): Dh PAD pin box x0-4.24..x0-0.64, Dl PAD pin box x0+11.92..x0+15.52,
    both topping out at y=44.3; seam resistor B terminal = right 0.42 um strip of Rs{leg}.
    """
    import klayout.db as db
    ly = db.Layout()
    ly.read(gds)
    tc = ly.cell(top)
    counts = {}
    for leg, x0 in legs.items():
        rs = next(i for i in tc.each_inst() if i.cell.name.startswith(f"Rs{leg}__"))
        bb = rs.dbbox()
        bx0, bx1, by1 = bb.right - 0.42, bb.right, bb.top
        # seam-resistor B strip -> M1 link to a left-side M1 riser -> Via1 -> M2 bus
        _box(tc, ly, M1, bx0, by1 - 0.5, bx1, by1 + 2.0)
        _box(tc, ly, M1, x0 - 7.0, by1 + 1.0, bx1, by1 + 2.0)
        _box(tc, ly, M1, x0 - 7.0, by1 + 1.0, x0 - 6.0, 52.5)
        _box(tc, ly, M2, x0 - 7.0, 49.5, x0 + 15.52, 52.5)
        n1 = _via_array(tc, ly, V1, 0.19, 0.41, x0 - 6.9, 49.6, x0 - 6.1, 52.4)
        # diode PAD pin boxes (M2) -> risers to the bus / the plate
        _box(tc, ly, M2, x0 - 4.24, 44.0, x0 - 0.64, 49.8)
        _box(tc, ly, M2, x0 + 11.92, 44.0, x0 + 15.52, PLATE[3] - 10.0)
        # via stack M2 -> TM1 -> (TV2) -> bondpad TM2
        px0, py0, px1, py1 = x0 + PLATE[0], PLATE[1], x0 + PLATE[2], PLATE[3]
        _box(tc, ly, M2, px0, py0, px1, py1)
        nstack = {"via1": n1}
        for lay, size, pitch, lo, hi in STACK:
            inset = 1.0 if lay == TV2 else 0.6
            nstack[str(lay)] = _via_array(tc, ly, lay, size, pitch,
                                          px0 + inset, py0 + inset, px1 - inset, py1 - inset)
            if hi:
                _box(tc, ly, hi, px0, py0, px1, py1)
        counts[leg] = nstack
    ly.write(gds)
    return counts


def compose(out, cell, blocks, origins, pins):
    req = {"schema": "klt.gen_compose.request/1", "pdk": {"variant": PDK},
           "blocks": blocks,
           "placement": {"strategy": "explicit", "order": [b["id"] for b in blocks],
                         "origins_um": origins},
           "pins": pins,
           "options": {"cell_name": cell, "output": os.path.join(out, f"{cell}.gds")}}
    rp = os.path.join(out, cell, "compose.request.json")
    json.dump(req, open(rp, "w"), indent=1)
    res = run(["klt", "gen-compose", rp, "--format", "json"])
    res["diode_markers"] = add_diode_markers(os.path.join(out, f"{cell}.gds"), cell)
    return res


def build_pad_esd(out):
    cell = "pad_esd"
    os.makedirs(os.path.join(out, cell), exist_ok=True)
    devs = netlist_devices(os.path.join(REPO, "design/tx/netlists/pad_esd.spice"), cell)
    assert sum(t[0].startswith("XXPAD") for t in devs) == 2
    blocks, origins, pins = [], {}, []
    # one column per differential leg: seam resistor (core side) -> ESD pair -> bondpad
    for leg, (core, pad) in {"p": ("cp", "padp"), "n": ("cn", "padn")}.items():
        x0 = 0.0 if leg == "p" else 100.0   # 100 um pad pitch
        rs = res_block(out, cell, f"Rs{leg}", 8.0, 4.571)
        blocks += [rs,
                   lib_block(f"Dh{leg}", "diodevdd_2kv", diode_ports("vdd")),
                   lib_block(f"Dl{leg}", "diodevss_2kv", diode_ports("vss")),
                   lib_block(f"PAD{leg}", "bondpad", [])]
        bb = rs["generator_report"]["bbox_um"]
        origins[f"Rs{leg}"] = {"x": x0 - bb["x0"], "y": 0.0 - bb["y0"]}
        origins[f"Dh{leg}"] = {"x": x0 - 2.12, "y": 15.0}
        origins[f"Dl{leg}"] = {"x": x0 + 14.0, "y": 15.0}
        origins[f"PAD{leg}"] = {"x": x0 + 20.0, "y": 15.0 + 37.05 + GAP + 40.0}
        pins += [{"net": core, "block": f"Rs{leg}", "port": "R0_A"},     # core-to-pad seam
                 {"net": pad, "block": f"Rs{leg}", "port": "R0_B"}]
    res = compose(out, cell, blocks, origins, pins)
    strapped = strap_pad_net(os.path.join(out, f"{cell}.gds"), cell, {"p": 0.0, "n": 100.0})
    return {"cell": cell, "blocks": len(blocks), "pins": [p["net"] for p in pins],
            "routed": "pad net only (resistor B, both diode PAD pins, bondpad)",
            "pad_stack_vias": strapped, "bbox_um": res.get("bbox_um")}


def build_rx_term_pad(out):
    cell = "rx_term_pad"
    os.makedirs(os.path.join(out, cell), exist_ok=True)
    devs = netlist_devices(os.path.join(REPO, "design/rx/netlists/rx_term_pad.spice"), cell)
    assert {t[0] for t in devs if t[0].startswith("C")} == {"Cpad_p", "Cpad_n"}
    blocks, origins, pins = [], {}, []
    for leg, (pad, inp) in {"p": ("padp", "inp"), "n": ("padn", "inn")}.items():
        x0 = 0.0 if leg == "p" else 60.0
        rt = res_block(out, cell, f"Rt{leg}", 1.0, round(50.0 / RSIL_OHM_SQ, 3))
        rs = res_block(out, cell, f"Rs{leg}", 8.0, 4.571)
        blocks += [rt, rs,
                   lib_block(f"Du{leg}", "diodevdd_2kv", diode_ports("vdd")),
                   lib_block(f"Dd{leg}", "diodevss_2kv", diode_ports("vss"))]
        origins[f"Rt{leg}"] = {"x": x0, "y": 0.0}
        origins[f"Rs{leg}"] = {"x": x0, "y": 15.0}
        origins[f"Du{leg}"] = {"x": x0 - 2.12, "y": 30.0}
        origins[f"Dd{leg}"] = {"x": x0 + 14.0, "y": 30.0}
        pins += [{"net": pad, "block": f"Rs{leg}", "port": "R0_A"},
                 {"net": inp, "block": f"Rs{leg}", "port": "R0_B"},
                 {"net": "vcm", "block": f"Rt{leg}", "port": "R0_B"}]
    res = compose(out, cell, blocks, origins, pins)
    return {"cell": cell, "blocks": len(blocks), "pins": [p["net"] for p in pins],
            "routed": False, "bbox_um": res.get("bbox_um")}


def main():
    out = os.path.abspath(sys.argv[1])
    summary = {"pdk": PDK, "pr_gds": "libs.ref/sg13g2_pr/gds/sg13g2_pr.gds",
               "claims": "placed, net-labelled, pad net strapped in pad_esd only; no LVS/5 GHz claim; extracted interconnect C only",
               "cells": [build_pad_esd(out), build_rx_term_pad(out)]}
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    scrub(out)
    print(json.dumps(summary, indent=1))


def scrub(out):
    """Keep host paths out of the committed record: record-relative / $PDK_ROOT."""
    for d, _, files in os.walk(out):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(d, f)
                s = open(p).read()
                s = s.replace(out, ".").replace(os.environ.get("PDK_ROOT", "\0"), "$PDK_ROOT")
                s = s.replace(REPO, "<repo>")
                open(p, "w").write(s)


if __name__ == "__main__":
    main()
