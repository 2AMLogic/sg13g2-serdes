#!/usr/bin/env python3
"""Generate the TX core analog cells (issue #110, T1 item 2, analog column).

One GDS per subckt (cell name == subckt name, plus tx_core_lib.gds holding all six) from design/tx/netlists/tx_top.spice:
every device is a `klt gen` cell (mos_array / res_array / cap_array / bjt_array,
SG13G2), the devices are shelf-packed into the subckt cell, and each subckt port
becomes a Metal2 pin shape (10/0 + 10/2) with a 10/25 label on the cell boundary.

NOT drawn: routing between devices, wells/taps beyond what the generators emit,
pad/ESD. No DRC/LVS/extraction claim is made (#26, #27).

usage: gen_tx_core.py <netlist> <out-dir> [--klt PATH]   (needs PDK/PDK_ROOT env)
"""
import json, math, os, subprocess, sys, tempfile
import klayout.db as db

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from layout_common import parse_subckts, um

CELLS = ["bias", "ffe_en", "mux2to1_cml", "predriver", "driver_ffe", "tx_lvl_cml2cmos"]
GAP, ROW_W, PIN = 4.0, 120.0, 0.5
M2, M2_PIN, M2_LBL = (10, 0), (10, 2), (10, 25)


def parse(path):
    """Shared subckt parse, reduced to the X-prefixed devices this generator maps."""
    subs = parse_subckts(path)
    for sub in subs.values():
        devs = []
        for t in sub["devs"]:
            if t[0].startswith("X"):
                nodes = [x for x in t[1:] if "=" not in x]
                devs.append({"name": t[0], "model": nodes[-1],
                             "kv": dict(x.split("=") for x in t if "=" in x)})
        sub["devs"] = devs
    return subs


def gen_params(d):
    kv, m = d["kv"], d["model"]
    if m in ("sg13_lv_nmos", "sg13_lv_pmos"):
        ng = int(kv.get("ng", 1))
        return "mos_array", {"w_um": um(kv["w"]) / ng, "l_um": um(kv["l"]), "fingers": ng, "rows": 1, "cols": 1,
                             "dummy": 0, "topology": "array", "gate_contact": True,
                             "flavor": "nfet" if m.endswith("nmos") else "pfet"}
    if m in ("rsil", "rppd"):
        total, w = um(kv["l"]), um(kv["w"])
        n = max(1, math.ceil(total / 40.0))
        return "res_array", {"length_um": total / n, "width_um": w, "num": n, "dummy": 0, "rows": n,
                             "series": n > 1, "snap": True,
                             # res_array has no rsil flavour on sg13g2 (generic/rhigh/rppd): rsil
                             # bodies are drawn as the generic poly flavour (tool gap, see PR).
                             "flavor": "rppd" if m == "rppd" else "generic"}
    if m == "cap_cmim":
        return "cap_array", {"plate_w_um": um(kv["w"]), "plate_h_um": um(kv["l"]), "num": 1}
    if m == "npn13G2":
        return "bjt_array", {"flavor": "npn13G2", "rows": 1, "cols": int(kv.get("Nx", 1)), "dummy": 0,
                             "topology": "array", "add_collector_ring": False}
    raise SystemExit(f"unsupported device model {m} ({d['name']})")


def main():
    net, out = sys.argv[1], sys.argv[2]
    klt = sys.argv[sys.argv.index("--klt") + 1] if "--klt" in sys.argv else "klt"
    subs = parse(net); os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="txcore-")
    summary = {}
    for cell in CELLS:
        s, ly = subs[cell], db.Layout(); ly.dbu = 0.001
        top = ly.create_cell(cell)
        x = y = rowh = 0.0; placed = []
        for d in s["devs"]:
            gen, p = gen_params(d)
            g = os.path.join(tmp, f"{cell}_{d['name']}.gds")
            r = subprocess.run([klt, "gen", gen, "--params", json.dumps(p), "--cell-name", f"{cell}_{d['name']}",
                                "-o", g, "--format", "json"], capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(f"klt gen failed for {cell}/{d['name']}: {r.stderr or r.stdout}")
            bb = json.loads(r.stdout)["bbox_um"]
            w, h = bb["x1"] - bb["x0"], bb["y1"] - bb["y0"]
            if x and x + w > ROW_W:
                x, y, rowh = 0.0, y + rowh + GAP, 0.0
            sub = db.Layout(); sub.read(g)
            sc = ly.create_cell(f"{cell}_{d['name']}"); sc.copy_tree(sub.top_cell())
            top.insert(db.CellInstArray(sc.cell_index(), db.Trans(round((x - bb["x0"]) * 1000), round((y - bb["y0"]) * 1000))))
            placed.append({"device": d["name"], "model": d["model"], "generator": gen, "params": p,
                           "origin_um": [round(x, 3), round(y, 3)], "size_um": [round(w, 3), round(h, 3)]})
            x += w + GAP; rowh = max(rowh, h)
        bbox = top.bbox(); l2 = [ly.layer(*M2), ly.layer(*M2_PIN), ly.layer(*M2_LBL)]
        W, H = bbox.width(), bbox.height(); n = len(s["ports"]); pitch = max(1000, W // max(n, 1))
        pins = []
        for i, port in enumerate(s["ports"]):   # pins along the bottom boundary edge
            px = bbox.left + i * pitch; py = bbox.bottom - round(PIN * 1000)
            r = db.Box(px, py, px + round(PIN * 1000), py + round(PIN * 1000))
            top.shapes(l2[0]).insert(r); top.shapes(l2[1]).insert(r)
            top.shapes(l2[2]).insert(db.Text(port, r.center().x, r.center().y))
            pins.append({"port": port, "layer": "Metal2 10/0 pin 10/2 label 10/25", "x_um": r.center().x / 1000, "y_um": r.center().y / 1000})
        ly.write(os.path.join(out, f"{cell}.gds"))
        summary[cell] = {"devices": placed, "pins": pins, "bbox_um": [bbox.left / 1000, bbox.bottom / 1000, bbox.right / 1000, bbox.top / 1000]}
    # Library stream holding all six cells: the single input for `klt signoff --attest 2`
    # (klt 0.9.0 attests only the last of several --input streams).
    lib, opt = db.Layout(), db.LoadLayoutOptions()
    opt.cell_conflict_resolution = db.LoadLayoutOptions.CellConflictResolution.RenameCell
    for cell in CELLS:
        lib.read(os.path.join(out, f"{cell}.gds"), opt)
    lib.write(os.path.join(out, "tx_core_lib.gds"))
    json.dump(summary, open(os.path.join(out, "plan.json"), "w"), indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
