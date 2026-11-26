#!/usr/bin/env python3
"""Generate the TX core analog cells (issue #110, T1 item 2, analog column).

One GDS per subckt (cell name == subckt name, plus tx_core_lib.gds holding all six) from design/tx/netlists/tx_top.spice:
every device is a `klt gen` cell (mos_array / res_array / cap_array / bjt_array,
SG13G2). tx_lvl_cml2cmos composes from an explicit per-net route plan
(issue #199, build_tx_lvl_routed); the other five cells are shelf-packed into
the subckt cell, each subckt port becoming a Metal2 pin shape (10/0 + 10/2)
with a 10/25 label on the cell boundary.

NOT drawn for the five shelf-packed cells: routing between devices, wells/taps
beyond what the generators emit, pad/ESD. No DRC/LVS/extraction claim is made
for them (#26, #27); the routed cell's DRC/LVS evidence lives in its record.

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
    """Shared subckt parse. The X-prefixed devices keep their ordered node
    list (issue #199: the TX route plan maps named nets to generator ports,
    so the terminal order the netlist states cannot be dropped)."""
    subs = parse_subckts(path)
    for sub in subs.values():
        devs = []
        for t in sub["devs"]:
            if t[0].startswith("X"):
                nodes = [x for x in t[1:] if "=" not in x]
                devs.append({"name": t[0], "model": nodes[-1], "nodes": nodes[:-1],
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


# ---------------------------------------------------------------------------
# tx_lvl_cml2cmos: the explicit per-net route plan (issue #199, first split of
# #127), the same shape as RX's lvl_cml2cmos plan in rx/gen_rx_cells.py: every
# net names its routing plane and the exact legs it is drawn as, steered
# through waypoints in free corridors, so nothing depends on gen-compose's
# automatic spanning-tree assignment (upstream gap
# 2AMLogic/klayout-tools#1962).
#
# Floorplan: five columns -- row A (y=0) nfets XMNt, XMN1, XMN2, XMNb, XMN3;
# row B (above the channel) pfets XMP1, XMP2, XMP3 with the well-tie strap in
# c1's row-B slot; the substrate-tie strap below row A's west end; the rppd
# bias resistor spans the width above the vdd trunk (west end into vdd, east
# end dropping to the vbm plane). Planes: metal2 = vss, s, d1, o1, out;
# metal3 = vdd, vbm. Crossing structure: vbm's channel horizontal must cross
# the d1 and o1 row-spanning verticals (metal2), so it rides metal3; the
# resistor's east drop stays east of the vdd trunk's east end so the metal3
# vertical never crosses it.
# ---------------------------------------------------------------------------
TXL_COLS = [("XMNt", "TIE_VDD"), ("XMN1", "XMP1"), ("XMN2", "XMP2"),
            ("XMNb", None), ("XMN3", "XMP3")]
TXL_GAP, TXL_WEST, TXL_CHANNEL = 5.0, 8.0, 6.0


def txl_ports(d):
    """Ordered-node -> generator-port map for one device of this cell."""
    if d["model"] in ("sg13_lv_nmos", "sg13_lv_pmos"):
        dr, g, s_ = d["nodes"][0:3]     # bulk (4th) via the body-tie straps
        return [("U0_D", dr), ("U0_G", g), ("U0_S", s_)]
    if d["model"] == "rppd":
        return [("R0_A", d["nodes"][0]), ("R0_B", d["nodes"][1])]
        # body (3rd node, vss) has no res_array port: the curated deck ties a
        # drawn rppd body to the substrate, which the vss strap names.
    raise SystemExit(f"tx_lvl_cml2cmos: unsupported device {d['name']} ({d['model']})")


def build_tx_lvl_routed(subs, out, klt):
    """Compose tx_lvl_cml2cmos from the explicit plan (issue #199)."""
    import layout_common as LC
    # run_klt resolves "klt" from PATH; the regen script passes the repo venv
    # binary explicitly, so put its directory first for this process.
    os.environ["PATH"] = os.path.dirname(os.path.abspath(klt)) + os.pathsep + os.environ["PATH"]
    from layout_common import write_tie_block, compose_routed_cell, route_plan_summary, bbox_um
    cell = "tx_lvl_cml2cmos"
    spec = subs[cell]
    work = os.path.join(out, cell)
    os.makedirs(work, exist_ok=True)
    reports, blocks, order = {}, [], []
    for d in spec["devs"]:
        gen, params = gen_params(d)
        gds = os.path.join(work, f"{d['name']}.gds")
        rep = LC.run_klt(["klt", "gen", gen, "--pdk", "ihp-sg13g2",
                          "--params", json.dumps(params),
                          "--cell-name", f"{cell}_{d['name']}", "-o", gds,
                          "--format", "json"])
        rep["gds_path"] = gds
        reports[d["name"]] = rep
        blocks.append({"id": d["name"], "generator_report": rep})
        order.append(d["name"])
    tie_vdd_port = write_tie_block(os.path.join(work, "tie_vdd.gds"),
                                   f"{cell}_tie_vdd", "well", 1.5, 3.0, "vdd")
    tie_vss_port = write_tie_block(os.path.join(work, "tie_vss.gds"),
                                   f"{cell}_tie_vss", "sub", 1.5, 2.5, "vss")
    blocks += [{"id": "TIE_VDD", "cell": {"gds_path": os.path.join(work, "tie_vdd.gds"),
                                          "cell_name": f"{cell}_tie_vdd", "ports": [tie_vdd_port]}},
               {"id": "TIE_VSS", "cell": {"gds_path": os.path.join(work, "tie_vss.gds"),
                                          "cell_name": f"{cell}_tie_vss", "ports": [tie_vss_port]}}]
    order += ["TIE_VDD", "TIE_VSS"]

    # placement: columns of (row A nfet, row B pfet/tie), row-aligned bottoms
    col_x0, col_w, col_cx = {}, {}, {}
    x = TXL_WEST
    for ca, cb in TXL_COLS:
        ids = [i for i in (ca, cb) if i in reports or (i or "").startswith("TIE")]
        w = max(reports[i]["bbox_um"]["x1"] - reports[i]["bbox_um"]["x0"]
                if i in reports else 1.5 for i in ids)
        col_x0[ca], col_w[ca], col_cx[ca] = x, w, x + w / 2
        x += w + TXL_GAP
    row_a_top = max(reports[ca]["bbox_um"]["y1"] for ca, _ in TXL_COLS)
    y_b = round(row_a_top + TXL_CHANNEL, 1)
    origins = {}
    for ca, cb in TXL_COLS:
        b = reports[ca]["bbox_um"]
        origins[ca] = {"x": round(col_x0[ca] - b["x0"], 3), "y": round(-b["y0"], 3)}
        if cb == "TIE_VDD":
            origins[cb] = {"x": round(col_x0[ca], 3), "y": round(y_b, 3)}
        elif cb in reports:
            b = reports[cb]["bbox_um"]
            # align the pfet's D/S pad x with the nfet's below: mos pads are
            # Metal2, and a 0.15 um offset (the pfet bbox's -0.15 origin)
            # makes the router's trunk face the device pad edge 0.04 um away
            # (metal2.space.1 on the first scratch build)
            nd = next(p["x_um"] for p in reports[ca]["ports"] if p["name"] == "U0_D")
            pd = next(p["x_um"] for p in reports[cb]["ports"] if p["name"] == "U0_D")
            origins[cb] = {"x": round(origins[ca]["x"] + (nd - pd), 3),
                           "y": round(y_b - b["y0"], 3)}
    origins["TIE_VSS"] = {"x": 0.5, "y": -6.5}
    row_b_top = max(bbox_um(reports[cb], origins[cb])[3] for _, cb in TXL_COLS if cb in reports)
    # the rppd body: above the vdd trunk, starting over column 3, so its east
    # pad clears the vdd trunk's east end (the vbm drop must not cross it)
    origins["XRbm"] = {"x": round(col_x0["XMN2"], 3), "y": round(row_b_top + 5.3, 1)}
    rb = bbox_um(reports["XRbm"], origins["XRbm"])
    res_x0, res_y0 = rb[0], rb[1]
    res_cy = round(res_y0 + 0.25, 2)

    # free-corridor coordinates (um)
    jog1 = round(row_b_top + 0.8, 1)     # metal2: d1 gate jog above row B
    jog2 = round(row_b_top + 1.6, 1)     # metal2: o1 gate jog above row B
    vdd_y = round(row_b_top + 2.8, 1)    # metal3: vdd trunk
    vss_y = -2.5                         # metal2: vss trunk below row A
    s_y = -1.4                           # metal2: s trunk below row A
    ch_o = 3.5                           # metal2: o1 low corridor over row A east
    vbm_y = round(row_a_top + 2.2, 1)    # metal3: vbm channel trunk
    out_mid = round(vbm_y - 2.0, 1)      # metal2: out vertical mid-height
    d1_mid = out_mid                     # metal2: d1 vertical mid-height
    g = lambda k, dx: round((col_x0[k] + col_w[k]) + dx, 1)
    vdd_w = 6.0
    pin_x = lambda b, p: round(composed_pin_x(reports, origins, b, p), 2)
    pin_y = lambda b, p: round(composed_pin_y(reports, origins, b, p), 2)
    tie_w_cx = round(origins["TIE_VDD"]["x"] + 0.75, 1)
    tie_s_cx = round(origins["TIE_VSS"]["x"] + 0.75, 1)
    vdd_3, vdd_5 = pin_x("XMP2", "U0_S"), pin_x("XMP3", "U0_S")
    vss_t = pin_x("XMNt", "U0_S")        # vss drops go straight down off each
    vss_b = pin_x("XMNb", "U0_S")        # S pad, then along the trunk: a drop
    vss_o = pin_x("XMN3", "U0_S")        # that first runs at pad level would
    s_1 = pin_x("XMNt", "U0_D")          # cross the neighbouring D pad
    s_2, s_3 = pin_x("XMN1", "U0_S"), pin_x("XMN2", "U0_S")
    # trunk lanes sit exactly on the pad centre they feed: an offset lane makes
    # the router tile a 0.02-0.06 um sliver next to its via landing (DRC
    # metal2/metal3.space.1 on the first scratch build)
    d1_2 = pin_x("XMP1", "U0_D")
    o_3 = pin_x("XMN2", "U0_D")
    o_5w, o_5g = g("XMN3", -0.9), pin_x("XMN3", "U0_G")
    v4 = g("XMNb", 0.55)
    b_drop = round(rb[2] + 0.3, 1)       # east of the vdd trunk's east end
    a_drop = round(col_x0["XMN2"] - 0.9, 1)
    g1_x = pin_x("XMNt", "U0_G")
    # the out lane cannot ride the D pad centre: there it runs 0.02 um from
    # XMN3.G's metal2 landing (net o1), and the router rejected the planned
    # leg. It leaves the XMN3.D pad horizontally to a lane 0.75 um east of the
    # pad centre, rises clear of both landings, and re-enters XMP3.D's pad.
    out_5 = round(pin_x("XMP3", "U0_D") + 0.75, 2)
    out_lo, out_hi = (pin_y("XMN3", "U0_D"), pin_y("XMP3", "U0_D"))
    P = lambda b, p: [b, p]
    nets = [
        {"net": "vdd", "layer_role": "metal3",
         "pins": [P("XMP1", "U0_S"), P("XMP2", "U0_S"), P("XMP3", "U0_S"),
                  P("XRbm", "R0_A"), P("TIE_VDD", "TAP")],
         "legs": [
             {"a": P("TIE_VDD", "TAP"), "b": P("XMP1", "U0_S"),
              "waypoints_um": [[tie_w_cx, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMP2", "U0_S"), "b": P("XMP1", "U0_S"),
              "waypoints_um": [[vdd_3, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMP3", "U0_S"), "b": P("XMP1", "U0_S"),
              "waypoints_um": [[vdd_5, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XRbm", "R0_A"), "b": P("XMP1", "U0_S"),
              "waypoints_um": [[a_drop, res_cy], [a_drop, vdd_y], [vdd_w, vdd_y]]}]},
        {"net": "vss", "layer_role": "metal2",
         "pins": [P("XMNt", "U0_S"), P("XMNb", "U0_S"), P("XMN3", "U0_S"),
                  P("TIE_VSS", "TAP")],
         "legs": [
             {"a": P("TIE_VSS", "TAP"), "b": P("XMNt", "U0_S"),
              "waypoints_um": [[tie_s_cx, vss_y], [vss_t, vss_y]]},
             {"a": P("XMNb", "U0_S"), "b": P("XMNt", "U0_S"),
              "waypoints_um": [[vss_b, vss_y], [vss_t, vss_y]]},
             {"a": P("XMN3", "U0_S"), "b": P("XMNt", "U0_S"),
              "waypoints_um": [[vss_o, vss_y], [vss_t, vss_y]]}]},
        {"net": "s", "layer_role": "metal2",
         "pins": [P("XMNt", "U0_D"), P("XMN1", "U0_S"), P("XMN2", "U0_S")],
         "legs": [
             {"a": P("XMN1", "U0_S"), "b": P("XMNt", "U0_D"),
              "waypoints_um": [[s_2, s_y], [s_1, s_y]]},
             {"a": P("XMN2", "U0_S"), "b": P("XMN1", "U0_S"),
              "waypoints_um": [[s_3, s_y], [s_2, s_y]]}]},
        {"net": "d1", "layer_role": "metal2",
         "pins": [P("XMN1", "U0_D"), P("XMP1", "U0_D"), P("XMP1", "U0_G"),
                  P("XMP2", "U0_G")],
         "legs": [
             {"a": P("XMN1", "U0_D"), "b": P("XMP1", "U0_D"),
              "waypoints_um": [[d1_2, d1_mid]]},
             {"a": P("XMP1", "U0_G"), "b": P("XMP1", "U0_D"),
              "waypoints_um": [[d1_2, jog1]]},
             {"a": P("XMP2", "U0_G"), "b": P("XMP1", "U0_D"),
              "waypoints_um": [[d1_2, jog1]]}]},
        {"net": "o1", "layer_role": "metal2",
         "pins": [P("XMN2", "U0_D"), P("XMP2", "U0_D"), P("XMN3", "U0_G"),
                  P("XMP3", "U0_G")],
         "legs": [
             {"a": P("XMN2", "U0_D"), "b": P("XMP2", "U0_D"),
              "waypoints_um": [[o_3, d1_mid]]},
             {"a": P("XMN3", "U0_G"), "b": P("XMP2", "U0_D"),
              "waypoints_um": [[o_5w, ch_o], [o_3, ch_o]]},
             {"a": P("XMP3", "U0_G"), "b": P("XMP2", "U0_D"),
              "waypoints_um": [[o_5g, jog2], [o_3, jog2]]}]},
        {"net": "vbm", "layer_role": "metal3",
         "pins": [P("XMNt", "U0_G"), P("XMNb", "U0_G"), P("XMNb", "U0_D"),
                  P("XRbm", "R0_B")],
         "legs": [
             {"a": P("XRbm", "R0_B"), "b": P("XMNt", "U0_G"),
              "waypoints_um": [[b_drop, res_cy], [b_drop, vbm_y], [g1_x, vbm_y]]},
             {"a": P("XMNb", "U0_G"), "b": P("XMNt", "U0_G"),
              "waypoints_um": [[v4, vbm_y], [g1_x, vbm_y]]},
             {"a": P("XMNb", "U0_D"), "b": P("XMNt", "U0_G"),
              "waypoints_um": [[v4, 0.9], [g1_x, vbm_y]]}]},
        {"net": "out", "layer_role": "metal2",
         "pins": [P("XMP3", "U0_D"), P("XMN3", "U0_D")],
         "legs": [{"a": P("XMN3", "U0_D"), "b": P("XMP3", "U0_D"),
                   "waypoints_um": [[out_5, out_lo], [out_5, out_hi]]}]},
    ]
    pins = [{"net": n, "block": b, "port": p} for n, b, p in (
        ("vdd", "TIE_VDD", "TAP"), ("vss", "TIE_VSS", "TAP"),
        ("inp", "XMN1", "U0_G"), ("inn", "XMN2", "U0_G"),
        ("out", "XMP3", "U0_D"))]
    nw_y0 = round(y_b + 1.0, 1)
    last_x1 = max(bbox_um(reports[cb], origins[cb])[2] for _, cb in TXL_COLS if cb in reports)
    nwell_boxes = [[round(TXL_WEST - 0.5, 1), nw_y0, round(last_x1 + 0.3, 1),
                    round(nw_y0 + 1.0, 1)]]
    req, res_ = compose_routed_cell(out, cell, "ihp-sg13g2", blocks, order, origins,
                                    nets, pins, nwell_boxes)
    return {"cell": cell, "devices": len(spec["devs"]), "explicit_route_plan": True,
            "planes": {n["net"]: n["layer_role"] for n in nets},
            "nets_routed": [n["net"] for n in res_.get("nets", []) if n.get("routed")],
            "nets_unrouted": [{"net": n["net"], "status": n.get("status")}
                              for n in res_.get("nets", []) if not n.get("routed")],
            "legs": route_plan_summary(res_),
            "body_ties": res_.get("body_ties"),
            "pins_labelled": [p["net"] for p in pins],
            "ports_without_pin": []}


def composed_pin_x(reports, origins, block, port):
    for p in reports[block]["ports"]:
        if p["name"] == port:
            return origins[block]["x"] + p["x_um"]
    raise KeyError(f"{block}.{port}")


def composed_pin_y(reports, origins, block, port):
    for p in reports[block]["ports"]:
        if p["name"] == port:
            return origins[block]["y"] + p["y_um"]
    raise KeyError(f"{block}.{port}")


def main():
    net, out = sys.argv[1], sys.argv[2]
    klt = sys.argv[sys.argv.index("--klt") + 1] if "--klt" in sys.argv else "klt"
    subs = parse(net); os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="txcore-")
    summary = {}
    for cell in CELLS:
        if cell == "tx_lvl_cml2cmos":
            # issue #199: this cell composes from the explicit per-net route
            # plan; the other five keep the shelf-pack + boundary-pin path.
            summary[cell] = build_tx_lvl_routed(subs, out, klt)
            continue
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
    # records must not leak host paths: rewrite the absolute output dir and
    # repo root the compose request/response embed (same rule as gen_rx_cells)
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    for root, _, files in os.walk(out):
        for f in files:
            if f.endswith(".json"):
                fp = os.path.join(root, f)
                txt = open(fp).read()
                txt = txt.replace(os.path.abspath(out), ".").replace(repo, "<repo>")
                open(fp, "w").write(txt)
    json.dump(summary, open(os.path.join(out, "plan.json"), "w"), indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
