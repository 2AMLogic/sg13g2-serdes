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
from layout_common import parse_subckts, run_klt as run, um

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


def device(t):
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
        return n, "mos_array", {"rows": 1, "cols": 1, "dummy": 0,
                                "w_um": um(p["w"]), "l_um": um(p["l"]),
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
            origins[n] = {"x": round(x - bb["x0"], 3), "y": round(y - bb["y0"], 3)}
            if cell == "clk_buf_quad" and n.endswith("b"):
                orient[n] = "mirror_x"
            x += bb["x1"] - bb["x0"] + SPACING
            h = max(h, bb["y1"] - bb["y0"])
        y += h + SPACING
    for b in blocks:
        if b["id"] in orient:
            b["orientation"] = orient[b["id"]]
    port_nets = spec["ports"]
    conn, pins = [], []
    for net, pl in sorted(nets.items()):
        if len(pl) >= 2:
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
    summary = [build(c, spice[c], out) for c in CELLS]
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
