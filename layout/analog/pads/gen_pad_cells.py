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
Cells are PLACED and net-labelled (`pins[]`); no routing, DRC, LVS, extraction
or capacitance/5 GHz claim is made (DRC #26, LVS #27, pad model #94). The
Cpad_p/Cpad_n 50 fF elements of rx_term_pad are pad-capacitance model elements,
not drawn devices, so they have no layout.

Usage: gen_pad_cells.py OUTDIR   (source scripts/env.sh first)
"""
import json, os, subprocess, sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PDK = "ihp-sg13g2"
PR_GDS = os.path.join(os.environ.get("PDK_ROOT", ""), PDK, "libs.ref/sg13g2_pr/gds/sg13g2_pr.gds")
RSIL_OHM_SQ = 7.0     # nominal rsil sheet resistance used only to size bodies (not verified)
GAP = 5.0             # um between placed blocks


def run(args):
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode not in (0, 3):
        sys.exit(f"{' '.join(args)} failed ({r.returncode}):\n{r.stderr}{r.stdout}")
    return json.loads(r.stdout)


def netlist_devices(path, sub):
    cur, devs = None, []
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith(("*", "+")):
            continue
        if t[0] == ".subckt":
            cur = t[1]
        elif t[0] == ".ends":
            cur = None
        elif cur == sub:
            devs.append(t)
    return devs


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


def compose(out, cell, blocks, origins, pins):
    req = {"schema": "klt.gen_compose.request/1", "pdk": {"variant": PDK},
           "blocks": blocks,
           "placement": {"strategy": "explicit", "order": [b["id"] for b in blocks],
                         "origins_um": origins},
           "pins": pins,
           "options": {"cell_name": cell, "output": os.path.join(out, f"{cell}.gds")}}
    rp = os.path.join(out, cell, "compose.request.json")
    json.dump(req, open(rp, "w"), indent=1)
    return run(["klt", "gen-compose", rp, "--format", "json"])


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
    return {"cell": cell, "blocks": len(blocks), "pins": [p["net"] for p in pins],
            "routed": False, "bbox_um": res.get("bbox_um")}


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
               "claims": "placed and net-labelled only; no routing/DRC/LVS/capacitance/5 GHz claim",
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
