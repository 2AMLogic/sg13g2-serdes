"""Shared helpers for the analog layout generators under layout/analog/.

One `.subckt` netlist parser, one `klt` subprocess runner, one SPICE
length-to-micrometre converter and one host-path rewrite for the JSON records,
used by rx/gen_rx_cells.py, tx/gen_tx_core.py and pads/gen_pad_cells.py. The
device-to-`klt gen` mapping stays in each generator (it legitimately differs).
The generators run under `python3 -I`, so each puts this directory on sys.path
itself before importing.

The body-tie straps (issue #199) and the composed-route plan helpers below are
shared by the RX and TX per-cell routed generators.
"""
import json
import math
import os
import re
import subprocess
import sys

_UM = re.compile(r"([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)([unm]?)")
_UM_SCALE = {"u": 1.0, "n": 1e-3, "m": 1e3, "": 1e6}   # suffix -> um per unit; bare = metres


# ---------------------------------------------------------------------------
# sg13g2 body-tie straps (issue #199; the opamp canary's #57 precedent).
#
# `klt gen` at the pinned 0.9.0 draws no substrate/well-tie implant a
# `klt extract --deck sg13g2` recognises: mos_array's optional guard ring is
# bare Activ (no pSD/nSD marker, so every nfet body falls back to the deck's
# synthesized `vsubs` global and every pfet body to an anonymous well net),
# and `klt gen guard_ring` draws Cont off the 5 nm manufacturing grid
# (2AMLogic/klayout-tools#5231, fixed upstream after 0.9.0 by PR #5235).
# The curated deck derives a tie from the doping implant instead:
# tap_pplus pSD (14,0) on Activ outside every NWell is a substrate tie,
# tap_nplus nSD (7,0) on Activ inside an NWell is a well tie. These helpers
# draw that geometry directly, on-grid, sized from the same curated-deck rules
# `klt drc --deck sg13g2` checks.
# ---------------------------------------------------------------------------
DBU = 1000                                    # dbu per um (klt sg13g2 deck)
L_ACTIV, L_POLY, L_CONT = (1, 0), (5, 0), (6, 0)
L_PSD, L_NSD, L_NWELL = (14, 0), (7, 0), (31, 0)
L_M1, L_M1_PIN, L_M1_LBL = (8, 0), (8, 2), (8, 25)
# Curated-deck rule floors (klayout_tools.decks.sg13g2.DECK at klt 0.9.0),
# in um. The tie geometry is sized from these so `klt drc` sees legal shapes
# by construction rather than by luck.
R_ACTIV_W, R_ACTIV_S = 0.15, 0.21
R_PSD_W = 0.31
R_CONT = 0.16              # cont.width.1: fixed square
R_CONT_S = 0.18
R_ACTIV_ENC_CONT = 0.07
R_M1_W, R_M1_S = 0.16, 0.18
R_NWELL_W = 0.62
R_NWELL_ENC_NACT = 0.24    # nwell.enclosing.nactiv.1 (well tie)
R_NWELL_SPACE_PACT = 0.24  # nwell.space.pactiv.1 (to substrate-tie Activ)


def _g(v):
    """um float snapped to the 10 nm manufacturing grid."""
    return round(round(v * DBU / 10.0) * 10) / DBU


def _d(v):
    """um -> on-grid dbu int."""
    return int(round(_g(v) * DBU))


def draw_tie_strap(ly, cell, kind, x0, y0, w, h, net, port_name):
    """Draw one body-tie strap into `cell` (a klayout.db layout, um coords).

    kind "sub": Activ + pSD + Cont + Metal1 -- a substrate tie; the caller
    must keep it outside every NWell (asserted later on the composed layout).
    kind "well": Activ + nSD inside its own NWell + Cont + Metal1 -- a well
    tie; the caller merges this NWell with the pfet wells (overlay_nwell_merge).

    All shapes land on the 10 nm manufacturing grid. Returns the
    gen-compose `blocks[].cell.ports[]` entry for the Metal1 landing pad.
    """
    import klayout.db as kdb
    if kind not in ("sub", "well"):
        raise ValueError(kind)
    x0, y0, w, h = (_g(v) for v in (x0, y0, w, h))
    act = kdb.Box(_d(x0), _d(y0), _d(x0 + w), _d(y0 + h))
    lay = {n: ly.layer(*l) for n, l in (
        ("act", L_ACTIV), ("psd", L_PSD), ("nsd", L_NSD), ("nw", L_NWELL),
        ("cont", L_CONT), ("m1", L_M1), ("lbl", L_M1_LBL))}
    cell.shapes(lay["act"]).insert(act)
    cell.shapes(lay["psd" if kind == "sub" else "nsd"]).insert(act)
    if kind == "well":
        m = _g(R_NWELL_ENC_NACT + 0.01)
        cell.shapes(lay["nw"]).insert(act.enlarged(_d(m), _d(m)))
    # Contact centres, one grid step inside the 0.07 um Activ enclosure floor
    # on both ends, so the 10 nm snap can never shave the enclosure below it
    # (activ.enclosing.cont.1; the first scratch build stuck out 10 nm).
    m = R_ACTIV_ENC_CONT + 0.01
    n = max(1, min(int((h - 2 * m - R_CONT) / (R_CONT + R_CONT_S + 0.02)) + 1, 12))
    if n > 1:
        step = (h - 2 * m - R_CONT) / (n - 1)
        ys = [y0 + m + R_CONT / 2 + i * step for i in range(n)]
    else:
        ys = [y0 + (h - R_CONT) / 2]
    for cy0 in ys:
        cy = _g(cy0)
        cell.shapes(lay["cont"]).insert(kdb.Box(
            _d(x0 + (w - R_CONT) / 2), _d(cy - R_CONT / 2),
            _d(x0 + (w + R_CONT) / 2), _d(cy + R_CONT / 2)))
    pad = act.enlarged(_d(0.05), _d(0.05))
    cell.shapes(lay["m1"]).insert(pad)
    cell.shapes(lay["lbl"]).insert(kdb.Text(net, act.center().x, act.center().y))
    return {"name": port_name, "layer": {"layer": L_M1[0], "datatype": L_M1[1]},
            "x_um": round(x0 + w / 2, 3), "y_um": round(y0 + h / 2, 3),
            "width_um": round(min(w, h), 3), "direction_deg": 90}


def write_tie_block(path, cell_name, kind, w, h, net, port_name="TAP"):
    """Write one standalone tie-strap GDS (a gen-compose `blocks[].cell` block)."""
    import klayout.db as kdb
    ly = kdb.Layout()
    ly.dbu = 0.001
    cell = ly.create_cell(cell_name)
    port = draw_tie_strap(ly, cell, kind, 0.0, 0.0, w, h, net, port_name)
    ly.write(path)
    return port


def _region(ly, cell, layer):
    import klayout.db as kdb
    return kdb.Region(kdb.RecursiveShapeIterator(ly, cell, ly.layer(*layer))).merged()


def overlay_nwell_merge(ly, cell, extra_nwell):
    """Merge every pfet NWell (and any tie NWell) into one region, assert it.

    Draws `extra_nwell` ([x0, y0, x1, y1] um boxes) into the NWell layer, then
    asserts the merged NWell region touching the tie strap is a single
    polygon: a disjoint pfet well would leave that pfet's body on an
    anonymous net and fail LVS with a symptom far from its cause.
    Returns the merged-region polygon count (== 1) for the summary.
    """
    import klayout.db as kdb
    lnw = ly.layer(*L_NWELL)
    for x0, y0, x1, y1 in extra_nwell:
        cell.shapes(lnw).insert(kdb.Box(_d(x0), _d(y0), _d(x1), _d(y1)))
    return _region(ly, cell, L_NWELL).count()


def assert_ties(ly, cell):
    """Assert the two tie invariants the whole body-tie scheme rests on.

    1. The substrate tie (pSD-marked Activ) lies outside every NWell: pSD
       inside a well is a pfet S/D diffusion, not a substrate tie, and it
       would short the rail it names into the well.
    2. The well tie (nSD-marked Activ) lies inside an NWell: nSD outside a
       well is an nfet S/D diffusion, not a well tie.
    Returns (n_sub_ties, n_well_ties) found, so a tie silently missing from
    the composed layout fails loudly too (0, 0 is always wrong here).
    """
    act, nw = _region(ly, cell, L_ACTIV), _region(ly, cell, L_NWELL)
    psd, nsd = _region(ly, cell, L_PSD), _region(ly, cell, L_NSD)
    sub, well = (psd & act) - nw, (nsd & act) & nw
    stray_sub, stray_well = (psd & act) & nw, (nsd & act) - nw
    if not stray_sub.is_empty():
        raise AssertionError(f"substrate tie overlaps NWell ({stray_sub.area()} dbu^2)")
    if not stray_well.is_empty():
        raise AssertionError(f"well tie outside every NWell ({stray_well.area()} dbu^2)")
    return sub.count(), well.count()


def composed_pin(block, port, reports, origins):
    """Composed-frame (x, y, width, direction) of a placed block's port (um)."""
    rep, o = reports[block], origins[block]
    for p in rep["ports"]:
        if p["name"] == port:
            return {"x": round(o["x"] + p["x_um"], 3), "y": round(o["y"] + p["y_um"], 3),
                    "width": p.get("width_um", 0.2), "dir": p.get("direction_deg", 90)}
    raise KeyError(f"{block}.{port}")


def bbox_um(rep, o):
    """Placed bbox (x0, y0, x1, y1) of a block, um, composed frame."""
    b = rep["bbox_um"]
    return (round(o["x"] + b["x0"], 3), round(o["y"] + b["y0"], 3),
            round(o["x"] + b["x1"], 3), round(o["y"] + b["y1"], 3))


def um(v):
    """SPICE length -> micrometres. Suffix u (micro), n (nano), m (milli), or a
    bare number in metres (exponent form allowed). Anything else raises."""
    m = _UM.fullmatch(v)
    if not m:
        raise ValueError(f"unsupported SPICE length {v!r}")
    return float(m.group(1)) * _UM_SCALE[m.group(2)]


def parse_subckts(path):
    """-> {subckt: {"ports": [net, ...], "devs": [[token, ...], ...]}}.
    Comment (`*`) and continuation (`+`) lines are skipped; every other line
    inside a subckt is one device token list."""
    cells, cur = {}, None
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith(("*", "+")):
            continue
        d = t[0].lower()
        if d == ".subckt":
            cur = {"ports": t[2:], "devs": []}
            cells[t[1]] = cur
        elif d == ".ends":
            cur = None
        elif cur is not None:
            cur["devs"].append(t)
    return cells


def run_klt(args, **kw):
    """Run a klt command, parse its JSON stdout. Exit 0 or 3 is OK, else exit."""
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode not in (0, 3):
        sys.exit(f"{' '.join(args)} failed ({r.returncode}):\n{r.stderr}{r.stdout}")
    return json.loads(r.stdout)


REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# Consume keys with their colon so only string values are eligible for rewriting.
_JSON_STRING = re.compile(r'"(?:[^"\\]|\\.)*"(?P<key>\s*:)?')
# Each match spells one decoded character, including a UTF-16 surrogate pair.
_JSON_CHAR = re.compile(r'\\u[dD][89a-bA-B]..\\u[dD][c-fC-F]..|\\u....|\\.|.', re.DOTALL)


def scrub_host_paths(out, pdk_root=None):
    """Rewrite host paths in JSON values, preserving the bytes around each root.

    Prefer the output directory, then the configured PDK, then the checkout.
    A relative PDK_ROOT is relative to the generator's working directory.
    """
    out = os.path.abspath(out)
    if pdk_root is None:
        pdk_root = os.environ.get("PDK_ROOT")
    roots = {out: "."}
    if pdk_root:
        roots.setdefault(os.path.abspath(pdk_root), "$PDK_ROOT")
    roots.setdefault(REPO, "<repo>")

    # Paths also occur after whitespace in klt diagnostics ("read from /...").
    boundary = rf"(?={re.escape(os.sep)}|\Z)"
    prefixes = [re.escape(root) + ("" if root.endswith(os.sep) else boundary) for root in roots]
    path_root = re.compile(r"(?<!\S)(?:" + "|".join(prefixes) + ")")

    def rewrite_value(token):
        if token["key"]:
            return token[0]
        value = json.loads(token[0])
        matches = list(path_root.finditer(value))
        if not matches:
            return token[0]
        # Splice at decoded character offsets but retain the original spelling
        # of escapes everywhere outside the roots, even inside a changed value.
        chars = _JSON_CHAR.findall(token[0][1:-1])
        for match in reversed(matches):
            root = match[0]
            end = match.end()
            if root.endswith(os.sep) and end < len(value):
                end -= 1  # keep the filesystem root's separator before a descendant
            chars[match.start():end] = [roots[root]]
        return '"' + "".join(chars) + '"'

    for root, _, files in os.walk(out):
        for f in files:
            if f.endswith(".json"):
                p = os.path.join(root, f)
                with open(p, encoding="utf-8", newline="") as s:
                    txt = s.read()
                rewritten = _JSON_STRING.sub(rewrite_value, txt)
                if rewritten != txt:
                    with open(p, "w", encoding="utf-8", newline="") as s:
                        s.write(rewritten)


# ---------------------------------------------------------------------------
# Explicit per-net route-plan composition (issue #199, first split of #127).
#
# `klt gen-compose` at 0.9.0 supports everything a hand-specified plan needs
# (connectivity[].layer_role per net, legs[] with from_pin/to_pin and
# per-leg waypoints_um), but its automatic spanning-tree search cannot assign
# planes across mutually-crossing nets (2AMLogic/klayout-tools#1962). The
# helpers below express the whole plan in the request: every net names its
# plane and, for bundle nets, the exact legs it is drawn as, each steered
# through caller-chosen waypoints (trunk lines and lanes in the free corridors
# between device rows). Nothing is left to the automatic search except pins a
# plan deliberately does not cover.
# ---------------------------------------------------------------------------

def assert_plan_followed(cell, nets, res):
    """Raise unless every leg the plan names was drawn as planned.

    gen-compose reports a net `routed` when its pins end up connected, even if
    it rejected a planned leg and substituted a connection of its own. This
    checks the legs, not the net: (1) no leg in the response may be unrouted
    (`routed` false), and (2) for a net that supplies legs, every response leg
    must be one of those planned pin pairs -- an extra leg is the router's
    substitute. Both are an explicit-plan defect, never a pass.
    """
    planned = {n["net"]: {frozenset((tuple(lg["a"]), tuple(lg["b"]))) for lg in n["legs"]}
               for n in nets if n.get("legs")}
    bad = []
    for n in res.get("nets", []):
        for lg in n.get("legs", []):
            ps = [(p["block"], p["port"]) for p in lg.get("pins", [])]
            name = f"{n.get('net')}: {ps[0][0]}.{ps[0][1]}-{ps[1][0]}.{ps[1][1]}" if len(ps) == 2 else str(n.get("net"))
            if not lg.get("routed"):
                bad.append(f"{name} rejected ({str(lg.get('reason'))[:90]})")
            elif n.get("net") in planned and len(ps) == 2 and frozenset(ps) not in planned[n["net"]]:
                bad.append(f"{name} not in the plan (router substitute)")
    if bad:
        raise AssertionError(f"{cell}: explicit route plan not followed: " + "; ".join(bad))


def compose_routed_cell(out, cell, pdk, blocks, order, origins, nets, pins,
                        nwell_merge_boxes, default_route=None,
                        expect_ties=(1, 1), expect_wells=1):
    """Compose one cell from an explicit plan; return (request, response).

    blocks: [{id, generator_report | cell}] -- device blocks are `klt gen`
        reports; tie straps are `blocks[].cell` entries (write_tie_block).
    nets: [{net, layer_role, pins: [{block, port}], legs:
        [{a: [block, port], b: [block, port], waypoints_um: [[x, y], ...]}]}]
        -- every leg becomes one named gen-compose leg (from_pin/to_pin) with
        the given waypoints; legs are seeded before the automatic search.
    nwell_merge_boxes: [[x0, y0, x1, y1], ...] um boxes drawn into NWell after
        composition to merge the pfet wells and the well-tie strap into one
        region (a disjoint well would float its pfet bodies).
    expect_ties: (substrate ties, well ties) the cell must contain;
    expect_wells: merged NWell polygon count the cell must contain (one well).
    After gen-compose the NWell merge is applied and the tie / merged-well
    invariants are enforced -- a count other than the expected one raises
    BEFORE the composed GDS is rewritten, so a layout with a dropped tie or a
    split well is never published; the GDS is then rewritten in place.
    """
    import klayout.db as kdb
    import os
    work = os.path.join(out, cell)
    os.makedirs(work, exist_ok=True)
    conn = []
    for n in nets:
        e = {"net": n["net"],
             "pins": [{"block": b, "port": p} for b, p in n["pins"]],
             "layer_role": n["layer_role"]}
        if n.get("legs"):
            e["legs"] = [{"from_pin": {"block": lg["a"][0], "port": lg["a"][1]},
                          "to_pin": {"block": lg["b"][0], "port": lg["b"][1]},
                          **({"layer_role": lg["layer_role"]} if lg.get("layer_role") else {}),
                          **({"waypoints_um": [[round(x, 3) for x in w] for w in lg["waypoints_um"]]}
                             if lg.get("waypoints_um") else {})}
                         for lg in n["legs"]]
        conn.append(e)
    req = {"schema": "klt.gen_compose.request/1", "pdk": {"variant": pdk},
           "blocks": blocks,
           "placement": {"strategy": "explicit", "order": order, "origins_um": origins},
           "connectivity": conn, "pins": pins,
           "routing": default_route or {"layer_role": "metal3", "width_um": 0.2},
           "options": {"cell_name": cell, "output": os.path.join(out, f"{cell}.gds")}}
    rp = os.path.join(work, "compose.request.json")
    json.dump(req, open(rp, "w"), indent=1)
    res = run_klt(["klt", "gen-compose", rp, "--format", "json"])
    json.dump(res, open(os.path.join(work, "compose.response.json"), "w"), indent=1)
    assert_plan_followed(cell, nets, res)
    gds = os.path.join(out, f"{cell}.gds")
    ly = kdb.Layout()
    ly.dbu = 0.001
    ly.read(gds)
    top = ly.cell(cell)
    nwell_polys = overlay_nwell_merge(ly, top, nwell_merge_boxes)
    n_sub, n_well = assert_ties(ly, top)
    if (n_sub, n_well) != tuple(expect_ties):
        raise AssertionError(f"{cell}: body ties (substrate, well) = {(n_sub, n_well)}, "
                             f"expected {tuple(expect_ties)}")
    if nwell_polys != expect_wells:
        raise AssertionError(f"{cell}: merged NWell has {nwell_polys} polygon(s), "
                             f"expected {expect_wells} (a split well floats a pfet body)")
    ly.write(gds)
    res["body_ties"] = {"substrate_ties": n_sub, "well_ties": n_well,
                        "merged_nwell_polygons": nwell_polys}
    return req, res


def route_plan_summary(res):
    """Human-auditable digest of one compose_routed_cell response."""
    out = []
    for n in res.get("nets", []):
        legs = []
        for l in n.get("legs", []):
            ps = l.get("pins") or []
            a, b = (ps + [{}] * 2)[:2]
            legs.append(f"{a.get('block')}.{a.get('port')}-{b.get('block')}.{b.get('port')}"
                        f"{'=ok' if l.get('routed') else '=' + str(l.get('reason'))[:80]}")
        out.append({"net": n.get("net"), "status": n.get("status"),
                    "routed": n.get("routed"), "legs": legs})
    return out
