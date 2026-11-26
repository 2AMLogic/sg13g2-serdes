#!/usr/bin/env python3
"""Generate the RX core analog cells (ctle, latch_cml, clk_buf_quad, lvl_cml2cmos).

Netlist-driven: devices and nets are read from design/rx/netlists/rx_top.spice.
Each device becomes a `klt gen` block (npn13G2 -> bjt_array, sg13_lv_* ->
mos_array, plain R -> res_array, cap_cmim -> cap_array); each subckt is then
placed with `klt gen-compose` (explicit placement), its internal nets are
routed where gen-compose can route them, and each subckt port is labelled on a
device terminal carrying that net (`pins[]`).

Usage: gen_rx_cells.py OUTDIR      (needs `klt` + PDK on PATH/env: source scripts/env.sh)

Nothing here claims DRC, LVS, extraction or matching verification.
"""
import json, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from layout_common import (parse_subckts, run_klt as run, um,
                           write_tie_block, compose_routed_cell, route_plan_summary,
                           composed_pin, bbox_um)

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
NETLIST = os.path.join(REPO, "design/rx/netlists/rx_top.spice")
CELLS = ["ctle", "latch_cml", "clk_buf_quad", "lvl_cml2cmos"]
PDK = "ihp-sg13g2"
SPACING = 3.0      # um between placed device blocks
ROUTE = {"layer_role": "metal3", "width_um": 0.2}
# clk_buf_quad: row = one chain; Q chain is a pure translation of the I chain, and
# the b half of each differential pair is the mirror_x image of the a half.


def kv(tokens):
    return {k: v for k, _, v in (x.partition("=") for x in tokens if "=" in x)}


def device(t, gate_contact=False):
    """-> (name, gen, params, {terminal-net-map: [(port-suffix, net)]})"""
    n, rest = t[0], t[1:]
    if n.startswith(("XQ", "XS")):
        c, b, e = rest[0:3]
        nx = int(kv(rest).get("Nx", "1"))
        return n, "bjt_array", {"flavor": "npn13G2", "rows": 1, "cols": nx,
                                "topology": "array", "dummy": 0,
                                "add_collector_ring": False}, \
            [(f"Q{k}_{s}", net) for k in range(1, nx + 1)
             for s, net in (("C", c), ("B", b), ("E", e))]
    if n.startswith("XM"):
        d, g, s_, _b = rest[0:4]
        p = kv(rest)
        # The fourth (bulk) terminal has no mos_array port at klt 0.9.0: the
        # layout realises it through the body-tie straps (draw_tie_strap), so
        # LVS must show every nfet body on vss and every pfet body on vdd --
        # the routed build below asserts the ties, the record's klt lvs run
        # is the acceptance check.
        return n, "mos_array", {"rows": 1, "cols": 1, "dummy": 0,
                                "w_um": um(p["w"]), "l_um": um(p["l"]),
                                "gate_contact": gate_contact,
                                "flavor": "pfet" if "pmos" in rest[4] else "nfet"}, \
            [("U0_D", d), ("U0_G", g), ("U0_S", s_)]
    if n.startswith("XC"):
        a, b = rest[0:2]
        return n, "cap_array", {"num": 1, "plate_w_um": 10, "plate_h_um": 10}, \
            [("C0_TOP", a), ("C0_BOT", b)]
    if n.startswith("R"):
        a, b = rest[0:2]
        return n, "res_array", {"num": 1, "dummy": 0}, [("R0_A", a), ("R0_B", b)]
    raise SystemExit(f"unsupported device: {' '.join(t)}")


# ---------------------------------------------------------------------------
# lvl_cml2cmos: the explicit per-net route plan (issue #199, first split of
# #127). Every net names its routing plane and the exact legs it is drawn as,
# steered through waypoints in free corridors -- nothing is left to
# gen-compose's automatic spanning-tree search (which routes 2 of 7 nets
# here, the upstream gap 2AMLogic/klayout-tools#1962 tracks).
#
# Floorplan: five columns, nfets in row A (y=0), pfets in row B (above the
# channel); the well-tie strap sits in row B's column-3 slot (XMnt has no
# row-B twin), the substrate-tie strap below row A's west end. In-column
# vertical nets (x, z, op) are one lane in the gap beside their columns;
# row-spanning nets (tl, y) run a channel trunk; supplies straddle everything
# on their own planes (vdd metal3 above row B, vss metal2 below row A).
# Planes: metal2 = vss, x, y, z, op; metal3 = vdd, tl.
# ---------------------------------------------------------------------------
LVL_COLS = [("XMn1", "XMp1"), ("XMn2", "XMp2"), ("XMnt", "TIE_VDD"),
            ("XMni1", "XMpi1"), ("XMni2", "XMpi2")]
LVL_GAP, LVL_WEST, LVL_CHANNEL = 5.0, 8.0, 6.0


def build_lvl_routed(spec, out):
    cell = "lvl_cml2cmos"
    work = os.path.join(out, cell)
    os.makedirs(work, exist_ok=True)
    devs = [device(t, gate_contact=True) for t in spec["devs"]]
    reports, blocks, order = {}, [], []
    for name, gen, params, terms in devs:
        gds = os.path.join(work, f"{name}.gds")
        rep = run(["klt", "gen", gen, "--pdk", PDK, "--params", json.dumps(params),
                   "--cell-name", f"{cell}_{name}", "-o", gds, "--format", "json"])
        rep["gds_path"] = gds
        reports[name] = rep
        blocks.append({"id": name, "generator_report": rep})
        order.append(name)
    # tie straps: substrate tie under row A's west end (into vss), well tie in
    # row B column 3 (into vdd; its NWell merges with the pfet wells below)
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
    x = LVL_WEST
    for ca, cb in LVL_COLS:
        ids = [i for i in (ca, cb) if i in reports or i.startswith("TIE")]
        w = max(reports[i]["bbox_um"]["x1"] - reports[i]["bbox_um"]["x0"]
                if i in reports else 1.5 for i in ids)
        col_x0[ca] = x
        col_w[ca] = w
        col_cx[ca] = x + w / 2
        x += w + LVL_GAP
    row_a_top = max(reports[n]["bbox_um"]["y1"] for ca, _ in LVL_COLS
                    for n in (ca,) if n in reports)
    y_b = round(row_a_top + LVL_CHANNEL, 1)
    origins = {}
    for ca, cb in LVL_COLS:
        if ca in reports:
            b = reports[ca]["bbox_um"]
            origins[ca] = {"x": round(col_x0[ca] - b["x0"], 3), "y": round(-b["y0"], 3)}
        if cb == "TIE_VDD":
            origins[cb] = {"x": round(col_x0[ca], 3), "y": round(y_b, 3)}
        elif cb in reports:
            b = reports[cb]["bbox_um"]
            origins[cb] = {"x": round(col_x0[ca] - b["x0"], 3), "y": round(y_b - b["y0"], 3)}
    origins["TIE_VSS"] = {"x": 0.5, "y": -6.5}
    row_b_top = max(bbox_um(reports[cb], origins[cb])[3] for _, cb in LVL_COLS if cb in reports)

    # free-corridor coordinates (um): channel trunks, supply rails, G jogs
    ch_y = round(row_a_top + 1.6, 1)      # metal2: y trunk
    ch_t = round(row_a_top + 2.6, 1)      # metal3: tl trunk
    jog = round(row_b_top + 1.0, 1)       # metal2: gate jogs above row B
    vdd_y = round(row_b_top + 2.0, 1)     # metal3: vdd trunk
    tl_low = -1.2                         # metal3: tl trunk below row A
    vss_y = -2.5                          # metal2: vss trunk below row A
    g = lambda i, dx: round((col_x0[LVL_COLS[i][0]] + col_w[LVL_COLS[i][0]]) + dx, 1)
    tl_w, vdd_w = round(LVL_WEST - 1.5, 1), round(LVL_WEST - 2.5, 1)
    tl_1, x_1, vdd_1 = g(0, 1.0), g(0, 2.0), g(0, 3.0)
    y_2, vss_2 = g(1, 1.0), g(1, 4.0)
    tl_3, vss_3, y_3, feed_3, vdd_3 = g(2, 0.8), g(2, 1.7), g(2, 2.6), g(2, 3.5), g(2, 4.2)
    z_4, vdd_4, vss_4 = g(3, 1.0), g(3, 2.0), g(3, 4.0)
    op_5 = g(4, 1.0)
    cx4 = round(col_cx[LVL_COLS[3][0]], 1)
    cx5 = round(col_cx[LVL_COLS[4][0]], 1)
    tie_w_cx = round(origins["TIE_VDD"]["x"] + 0.75, 1)
    tie_s_cx = round(origins["TIE_VSS"]["x"] + 0.75, 1)
    P = lambda b, p: [b, p]
    nets = [
        {"net": "vdd", "layer_role": "metal3",
         "pins": [P("XMnt", "U0_G"), P("XMp1", "U0_S"), P("XMp2", "U0_S"),
                  P("XMpi1", "U0_S"), P("XMpi2", "U0_S"), P("TIE_VDD", "TAP")],
         "legs": [
             {"a": P("TIE_VDD", "TAP"), "b": P("XMp1", "U0_S"),
              "waypoints_um": [[tie_w_cx, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMp2", "U0_S"), "b": P("XMp1", "U0_S"),
              "waypoints_um": [[vdd_1, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMpi1", "U0_S"), "b": P("XMp1", "U0_S"),
              "waypoints_um": [[vdd_3, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMpi2", "U0_S"), "b": P("XMp1", "U0_S"),
              "waypoints_um": [[vdd_4, vdd_y], [vdd_w, vdd_y]]},
             {"a": P("XMnt", "U0_G"), "b": P("TIE_VDD", "TAP"),
              "waypoints_um": [[feed_3, round(row_a_top + 1.0, 1)], [feed_3, vdd_y],
                               [tie_w_cx, vdd_y]]}]},
        {"net": "vss", "layer_role": "metal2",
         "pins": [P("XMnt", "U0_S"), P("XMni1", "U0_S"), P("XMni2", "U0_S"),
                  P("TIE_VSS", "TAP")],
         "legs": [
             {"a": P("TIE_VSS", "TAP"), "b": P("XMnt", "U0_S"),
              "waypoints_um": [[tie_s_cx, vss_y], [vss_2, vss_y]]},
             {"a": P("XMni1", "U0_S"), "b": P("XMnt", "U0_S"),
              "waypoints_um": [[vss_3, vss_y], [vss_2, vss_y]]},
             {"a": P("XMni2", "U0_S"), "b": P("XMnt", "U0_S"),
              "waypoints_um": [[vss_4, vss_y], [vss_2, vss_y]]}]},
        {"net": "tl", "layer_role": "metal3",
         "pins": [P("XMn1", "U0_S"), P("XMn2", "U0_S"), P("XMnt", "U0_D")],
         "legs": [
             {"a": P("XMn1", "U0_S"), "b": P("XMnt", "U0_D"),
              "waypoints_um": [[tl_w, tl_low], [tl_3, tl_low]]},
             {"a": P("XMn2", "U0_S"), "b": P("XMn1", "U0_S"),
              "waypoints_um": [[tl_1, ch_t]]}]},
        {"net": "op", "layer_role": "metal2",
         "pins": [P("XMpi2", "U0_D"), P("XMni2", "U0_D")],
         "legs": [{"a": P("XMni2", "U0_D"), "b": P("XMpi2", "U0_D"),
                   "waypoints_um": [[op_5, ch_y]]}]},
        {"net": "x", "layer_role": "metal2",
         "pins": [P("XMn1", "U0_D"), P("XMp1", "U0_D"), P("XMp1", "U0_G"),
                  P("XMp2", "U0_G")],
         "legs": [
             {"a": P("XMn1", "U0_D"), "b": P("XMp1", "U0_D"),
              "waypoints_um": [[x_1, ch_y]]},
             {"a": P("XMp1", "U0_G"), "b": P("XMp1", "U0_D"),
              "waypoints_um": [[x_1, jog]]},
             {"a": P("XMp2", "U0_G"), "b": P("XMp1", "U0_D"),
              "waypoints_um": [[x_1, jog]]}]},
        {"net": "y", "layer_role": "metal2",
         "pins": [P("XMn2", "U0_D"), P("XMp2", "U0_D"), P("XMpi1", "U0_G"),
                  P("XMni1", "U0_G")],
         "legs": [
             {"a": P("XMn2", "U0_D"), "b": P("XMp2", "U0_D"),
              "waypoints_um": [[y_2, ch_y]]},
             {"a": P("XMni1", "U0_G"), "b": P("XMn2", "U0_D"),
              "waypoints_um": [[cx4, ch_y], [y_2, ch_y]]},
             {"a": P("XMpi1", "U0_G"), "b": P("XMn2", "U0_D"),
              "waypoints_um": [[y_3, jog], [y_3, ch_y], [y_2, ch_y]]}]},
        {"net": "z", "layer_role": "metal2",
         "pins": [P("XMpi1", "U0_D"), P("XMni1", "U0_D"), P("XMpi2", "U0_G"),
                  P("XMni2", "U0_G")],
         "legs": [
             {"a": P("XMni1", "U0_D"), "b": P("XMpi1", "U0_D"),
              "waypoints_um": [[z_4, ch_y]]},
             # the two col-5 gate pads sit on one free metal3 vertical east of
             # the column (vdd's XMpi2.S drop pad reaches x~34.3 at y~13, the
             # vdd trunk stops at the gap-4 lane west of it); the low metal3
             # corridor at y = row_a_top + 0.6 then reaches the z lane in
             # gap 4 clear of every metal2 net.
             {"a": P("XMpi2", "U0_G"), "b": P("XMni2", "U0_G"),
              "layer_role": "metal3",
              "waypoints_um": [[cx5 + 0.85, jog], [cx5 + 0.85, round(row_a_top + 0.6, 1)]]},
             {"a": P("XMni2", "U0_G"), "b": P("XMni1", "U0_D"),
              "layer_role": "metal3",
              "waypoints_um": [[cx5, round(row_a_top + 0.6, 1)],
                               [z_4, round(row_a_top + 0.6, 1)]]}]},
    ]
    pins = [{"net": n, "block": b, "port": p} for n, b, p in (
        ("ip", "XMn1", "U0_G"), ("in", "XMn2", "U0_G"),
        ("vdd", "TIE_VDD", "TAP"), ("vss", "TIE_VSS", "TAP"),
        ("op", "XMpi2", "U0_D"))]
    # one NWell bar through row B merges the tie strap's well with every pfet's
    nw_bar_y0 = round(y_b + 1.0, 1)
    nwell_boxes = [[round(LVL_WEST - 1.0, 1), nw_bar_y0,
                    round(origins["TIE_VSS"]["x"] + 45, 1), round(nw_bar_y0 + 1.0, 1)]]
    # x1 of the bar: east edge of the last pfet column's well (+ margin)
    last_x1 = max(bbox_um(reports[cb], origins[cb])[2] for _, cb in LVL_COLS if cb in reports)
    nwell_boxes[0][2] = round(last_x1 + 0.3, 1)
    req, res = compose_routed_cell(out, cell, PDK, blocks, order, origins, nets, pins,
                                   nwell_boxes)
    return {"cell": cell, "devices": len(devs), "explicit_route_plan": True,
            "planes": {n["net"]: n["layer_role"] for n in nets},
            "nets_routed": [n["net"] for n in res.get("nets", []) if n.get("routed")],
            "nets_unrouted": [{"net": n["net"], "status": n.get("status")}
                              for n in res.get("nets", []) if not n.get("routed")],
            "legs": route_plan_summary(res),
            "body_ties": res.get("body_ties"),
            "pins_labelled": [p["net"] for p in pins],
            "ports_without_pin": []}


def build(cell, spec, out):
    devs = [device(t) for t in spec["devs"]]
    work = os.path.join(out, cell)
    os.makedirs(work, exist_ok=True)
    reports, blocks, order, nets = {}, [], [], {}
    for name, gen, params, terms in devs:
        gds = os.path.join(work, f"{name}.gds")
        rep = run(["klt", "gen", gen, "--pdk", PDK, "--params", json.dumps(params),
                   "--cell-name", f"{cell}_{name}", "-o", gds, "--format", "json"])
        rep["gds_path"] = gds
        reports[name] = rep
        blocks.append({"id": name, "generator_report": rep})
        order.append(name)
        for port, net in terms:
            nets.setdefault(net, []).append((name, port))
    # placement: rows of devices; clk_buf_quad splits I / Q chains into two rows
    if cell == "clk_buf_quad":
        chain = lambda n: re.match(r"(?:XQ|RL|Rt)([iq])\d", n).group(1)
        rows = [[n for n in order if chain(n) == c] for c in "iq"]
    else:
        rows, per = [], 6
        rows = [order[i:i + per] for i in range(0, len(order), per)]
    origins, orient, y = {}, {}, 0.0
    for row in rows:
        x, h = 0.0, 0.0
        for n in row:
            bb = reports[n]["bbox_um"]
            if cell == "clk_buf_quad" and n.endswith("b"):
                # gen-compose "mirror_x" is the x -> -x flip (GDS m90), so the block
                # occupies [origin - x1, origin - x0]; put the origin at the right edge
                # of its slot, else the b device overlaps the a device (#26).
                orient[n] = "mirror_x"
                origins[n] = {"x": round(x + bb["x1"], 3), "y": round(y - bb["y0"], 3)}
            else:
                origins[n] = {"x": round(x - bb["x0"], 3), "y": round(y - bb["y0"], 3)}
            x += bb["x1"] - bb["x0"] + SPACING
            h = max(h, bb["y1"] - bb["y0"])
        y += h + SPACING
    for b in blocks:
        if b["id"] in orient:
            b["orientation"] = orient[b["id"]]
    port_nets = spec["ports"]
    conn, pins = [], []
    for net, pl in sorted(nets.items()):
        # gen-compose routes onto an HBT terminal by dropping a via stack inside the
        # PDK cell's own via1/metal1 array, 15 nm from existing vias (DRC: via1.space.1,
        # metal1/2.space.1). Nets with an HBT terminal are therefore left unrouted
        # (their pins stay labelled); intra-cell routing is partial by design (#26).
        if len(pl) >= 2 and not any(b.startswith(("XQ", "XS")) for b, _ in pl):
            conn.append({"net": net, "pins": [{"block": b, "port": p} for b, p in pl]})
    for net in port_nets:
        if net in nets:
            b, p = nets[net][0]
            pins.append({"net": net, "block": b, "port": p})
    req = {"schema": "klt.gen_compose.request/1", "pdk": {"variant": PDK},
           "blocks": blocks,
           "placement": {"strategy": "explicit", "order": order, "origins_um": origins},
           "connectivity": conn, "pins": pins, "routing": ROUTE,
           "options": {"cell_name": cell, "output": os.path.join(out, f"{cell}.gds")}}
    rp = os.path.join(work, "compose.request.json")
    json.dump(req, open(rp, "w"), indent=1)
    res = run(["klt", "gen-compose", rp, "--format", "json"])
    return {"cell": cell, "devices": len(devs), "orientation": orient,
            "nets_routed": [n["net"] for n in res.get("nets", []) if n.get("routed")],
            "nets_unrouted": [{"net": n["net"], "reason": n.get("reason")}
                              for n in res.get("nets", []) if not n.get("routed")],
            "pins_labelled": [p["net"] for p in pins],
            "ports_without_pin": [p for p in port_nets if p not in nets]}


def main():
    out = os.path.abspath(sys.argv[1])
    os.makedirs(out, exist_ok=True)
    spice = parse_subckts(NETLIST)
    summary = [build_lvl_routed(spice["lvl_cml2cmos"], out) if c == "lvl_cml2cmos"
               else build(c, spice[c], out) for c in CELLS]
    # one stream holding all four cells (shared PDK sub-cells are merged by name)
    import klayout.db as kdb
    ly = kdb.Layout()
    opt = kdb.LoadLayoutOptions()
    opt.cell_conflict_resolution = kdb.LoadLayoutOptions.CellConflictResolution.SkipNewCell
    for c in CELLS:
        ly.read(os.path.join(out, f"{c}.gds"), opt)
    ly.write(os.path.join(out, "rx_core.gds"))
    # records must not leak host paths: rewrite the absolute output dir to "."
    for root, _, files in os.walk(out):
        for f in files:
            if f.endswith(".json"):
                fp = os.path.join(root, f)
                txt = open(fp).read()
                txt = txt.replace(out, ".").replace(REPO, "<repo>")
                open(fp, "w").write(txt)
    json.dump(summary, open(os.path.join(out, "summary.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
