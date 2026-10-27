#!/usr/bin/env python3
"""Generate the TX xschem schematics (.sch) and symbols (.sym) in design/tx/.

The cells are described once, as data, below. The generated .sch/.sym files are
the committed schematic sources; this script is the generator that produced
them (T1 item 1: "committed schematic sources (or generator)"). Re-run it after
editing a cell, then re-export the netlists with design/tx/export-netlists.sh.

Every value is a first-cut SIZING value for the draft spec rows (R3, R4, R5,
R7, R18, R19), not a spec result and not a measurement.

Usage:  python3 -I design/tx/gen_schematics.py        (from the repo root)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- device kinds
# pin -> (dx, dy, stub_dx, stub_dy): pin offset from the symbol origin and the
# direction the label stub leaves the pin.
KINDS = {
    "npn": dict(sym="sg13g2_pr/npn13G2.sym", prefix="X", model="npn13G2",
                pins={"C": (20, -30, 0, -20), "B": (-20, 0, -30, 0),
                      "E": (20, 30, 0, 20), "S": (20, 0, 30, 0)}),
    "nmos": dict(sym="sg13g2_pr/sg13_lv_nmos.sym", prefix="X", model="sg13_lv_nmos",
                 pins={"D": (20, -30, 0, -20), "G": (-20, 0, -30, 0),
                       "S": (20, 30, 0, 20), "B": (20, 0, 30, 0)}),
    "pmos": dict(sym="sg13g2_pr/sg13_lv_pmos.sym", prefix="X", model="sg13_lv_pmos",
                 pins={"D": (20, 30, 0, 20), "G": (-20, 0, -30, 0),
                       "S": (20, -30, 0, -20), "B": (20, 0, 30, 0)}),
    "rsil": dict(sym="sg13g2_pr/rsil.sym", prefix="X", model="rsil",
                 pins={"P": (0, -30, 0, -20), "M": (0, 30, 0, 20)}),
    "rppd": dict(sym="sg13g2_pr/rppd.sym", prefix="X", model="rppd",
                 pins={"P": (0, -30, 0, -20), "M": (0, 30, 0, 20)}),
    "cmim": dict(sym="sg13g2_pr/cap_cmim.sym", prefix="X", model="cap_cmim",
                 pins={"c0": (0, -30, 0, -20), "c1": (0, 30, 0, 20)}),
    "dvdd": dict(sym="sg13g2_pr/diodevdd_2kv.sym", prefix="X", model="diodevdd_2kv",
                 pins={"vdd": (0, -30, 0, -20), "pad": (0, 30, 0, 20),
                       "vss": (-30, 0, -30, 0)}),
    "dvss": dict(sym="sg13g2_pr/diodevss_2kv.sym", prefix="X", model="diodevss_2kv",
                 pins={"vdd": (-30, 0, -30, 0), "pad": (0, -30, 0, -20),
                       "vss": (0, 30, 0, 20)}),
    "bondpad": dict(sym="sg13g2_pr/bondpad.sym", prefix="X", model="bondpad",
                    pins={"pad": (0, 40, 0, 20)}),
}


def fmt_si(x):
    """Engineering value string for a length/resistance-like float."""
    return ("%.4g" % x)


def npn(name, c, b, e, nx, s="vss"):
    return dict(kind="npn", name=name, nets=dict(C=c, B=b, E=e, S=s),
                attrs="Nx=%d" % nx)


def nmos(name, d, g, s, w, ng=1, b="vss", l="0.13u"):
    return dict(kind="nmos", name=name, nets=dict(D=d, G=g, S=s, B=b),
                attrs="w=%s l=%s ng=%d m=1" % (w, l, ng))


def pmos(name, d, g, s, w, ng=1, b="vdd", l="0.13u"):
    return dict(kind="pmos", name=name, nets=dict(D=d, G=g, S=s, B=b),
                attrs="w=%s l=%s ng=%d m=1" % (w, l, ng))


# Sheet resistance used to turn an ohm target into a drawn length (rsil 7 ohm/sq,
# rppd ~260 ohm/sq as in the PDK symbol/model); the PDK model computes the real
# value, these only choose w and l.
RSH = {"rsil": 7.0, "rppd": 260.0}


def res(name, p, m, ohm, w_um, kind="rsil"):
    l_um = ohm * w_um / RSH[kind]
    return dict(kind=kind, name=name, nets=dict(P=p, M=m),
                attrs="w=%su l=%su b=0 m=1 body=vss" % (fmt_si(w_um), fmt_si(l_um)))


def cmim(name, p, m, w_um=7.0, l_um=7.0):
    return dict(kind="cmim", name=name, nets=dict(c0=p, c1=m),
                attrs="w=%su l=%su m=1" % (fmt_si(w_um), fmt_si(l_um)))


# --------------------------------------------------------------------- cells
# ports: (name, dir) with dir in {power, in, out, inout}. Order = pin order.
CELLS = {}


def cell(name, doc, ports, devices):
    CELLS[name] = dict(doc=doc, ports=ports, devices=devices)


P_POWER = [("vdd", "power"), ("vss", "power")]

# --- bias: HBT-only reference that sets every HBT tail (density-matched mirror)
cell("bias",
     "HBT-only tail-bias reference. Qref (Nx=1) at 1.25 mA with 64 ohm degeneration; "
     "every tail is a density-matched Nx*Qref with Re = 64/Nx ohm. Rref is a "
     "PLACEHOLDER: the reference current follows the supply (see sizing record); "
     "a bandgap-derived reference belongs to a sibling block and is not designed here.",
     P_POWER + [("vbn", "out")],
     [res("Rref", "vdd", "vbn", 200, 4),
      npn("Qref", "vbn", "vbn", "er", 1),
      res("Rer", "er", "vss", 64, 4),
      cmim("Cvbn", "vbn", "vss")])

# --- ffe_en: MOS gating of the three post-cursor tail biases
_en = []
for i in range(3):
    _en += [
        pmos("MPi%d" % i, "enb%d" % i, "en%d" % i, "vdd", "1u"),
        nmos("MNi%d" % i, "enb%d" % i, "en%d" % i, "vss", "0.5u"),
        res("Rb%d" % i, "vbn", "vbp%d" % i, 1000, 2),
        nmos("MNd%d" % i, "vbp%d" % i, "enb%d" % i, "vss", "2u"),
    ]
cell("ffe_en",
     "Thin-oxide MOS enable for the three post-cursor FFE slices. enN=1 passes vbn "
     "to vbpN (slice on); enN=0 pulls vbpN to vss through MNd (slice off). 4 steps "
     "(0..3 slices). MOS only: not simulated while OSDI is unavailable (#3).",
     P_POWER + [("vbn", "in"), ("en0", "in"), ("en1", "in"), ("en2", "in"),
                ("vbp0", "out"), ("vbp1", "out"), ("vbp2", "out")],
     _en)

# --- mux2to1_cml: final 2:1 mux, half-rate 5 GHz clock
_mux = []
for ph, (ckin, sq) in {"a": ("ckp", "sqa"), "b": ("ckn", "sqb")}.items():
    _mux += [
        cmim("Cc" + ph, ckin, "nc" + ph),
        res("Rf" + ph, "mid" + ph, "nc" + ph, 20000, 0.5, kind="rppd"),
        pmos("MP1" + ph, "mid" + ph, "nc" + ph, "vdd", "8u", ng=2),
        nmos("MN1" + ph, "mid" + ph, "nc" + ph, "vss", "4u", ng=2),
        pmos("MP2" + ph, sq, "mid" + ph, "vdd", "16u", ng=4),
        nmos("MN2" + ph, sq, "mid" + ph, "vss", "8u", ng=2),
    ]
for ph, (dp, dn, sq) in {"a": ("dap", "dan", "sqa"), "b": ("dbp", "dbn", "sqb")}.items():
    _mux += [
        npn("Q%s1" % ph, "outn", dp, "e" + ph, 2),
        npn("Q%s2" % ph, "outp", dn, "e" + ph, 2),
        nmos("MT" + ph, "e" + ph, sq, "s" + ph, "20u", ng=4),
        res("Rs" + ph, "s" + ph, "vss", 60, 8),
    ]
_mux += [res("RLp", "vdd", "outp", 100, 8), res("RLn", "vdd", "outn", 100, 8)]
cell("mux2to1_cml",
     "Final 2:1 mux (DR-001 decision 2). Two HBT data pairs share resistive loads; each "
     "pair's tail is a thin-oxide NMOS gated by a rail-swing copy of one 5 GHz phase "
     "(AC-coupled, self-biased inverter pair squarer). Series-gated HBT does not fit the "
     "1.2 V rail (two Vbe + two Vce > 1.2 V), hence the MOS tail switch. The "
     "clock squarer at 5 GHz is an unproven seam, flagged in the sizing record.",
     P_POWER + [("ckp", "in"), ("ckn", "in"), ("dap", "in"), ("dan", "in"),
                ("dbp", "in"), ("dbn", "in"), ("outp", "out"), ("outn", "out")],
     _mux)

# --- predriver
cell("predriver",
     "HBT CML pre-driver: Nx=4 pair, 60 ohm loads, 5 mA tail (Nx=4, Re=16 ohm) from vbn. "
     "Outputs are vdd-referenced so the driver pair sees the same input levels as this "
     "stage does (no level shift fits the rail). HBT and resistors only.",
     P_POWER + [("inp", "in"), ("inn", "in"), ("vbn", "in"),
                ("outp", "out"), ("outn", "out")],
     [npn("Q1", "outn", "inp", "e", 4), npn("Q2", "outp", "inn", "e", 4),
      npn("Qt", "e", "vbn", "et", 4), res("Re", "et", "vss", 16, 8),
      res("RL1", "vdd", "outp", 60, 8), res("RL2", "vdd", "outn", 60, 8)])

# --- driver_ffe: main pair + 3 post-cursor slices, 50 ohm back-termination
_drv = [npn("QM1", "outn", "inp", "em", 8), npn("QM2", "outp", "inn", "em", 8),
        npn("QTM", "em", "vbn", "etm", 8), res("REM", "etm", "vss", 8, 16),
        res("RT1", "vdd", "outp", 50, 16), res("RT2", "vdd", "outn", 50, 16)]
for i in range(3):
    _drv += [npn("QP%da" % i, "outp", "pip", "ep%d" % i, 1),
             npn("QP%db" % i, "outn", "pin", "ep%d" % i, 1),
             npn("QTP%d" % i, "ep%d" % i, "vbp%d" % i, "etp%d" % i, 1),
             res("REP%d" % i, "etp%d" % i, "vss", 72, 4)]
cell("driver_ffe",
     "HBT CML line driver with 2-tap FFE (R5). Main pair Nx=8 / 10 mA tail; three Nx=1 "
     "post-cursor pairs of 1.11 mA each (0..3 slices => 0..6 dB de-emphasis in 4 steps) "
     "steer with crossed collectors from the one-UI-delayed stream (pip/pin). 50 ohm "
     "on-die back-termination to vdd. HBT and resistors only.",
     P_POWER + [("inp", "in"), ("inn", "in"), ("pip", "in"), ("pin", "in"),
                ("vbn", "in"), ("vbp0", "in"), ("vbp1", "in"), ("vbp2", "in"),
                ("outp", "out"), ("outn", "out")],
     _drv)

# --- lvl_cml2cmos
cell("lvl_cml2cmos",
     "CML-to-CMOS level conversion at the first divided clock (DR-001 decision 3). "
     "NMOS pair with PMOS mirror load, then an inverter to a rail-swing output. "
     "MOS only: not simulated while OSDI is unavailable (#3).",
     P_POWER + [("inp", "in"), ("inn", "in"), ("out", "out")],
     [nmos("MN1", "d1", "inp", "s", "8u", ng=2), nmos("MN2", "o1", "inn", "s", "8u", ng=2),
      pmos("MP1", "d1", "d1", "vdd", "8u", ng=2), pmos("MP2", "o1", "d1", "vdd", "8u", ng=2),
      nmos("MNt", "s", "vbm", "vss", "8u", ng=2),
      nmos("MNb", "vbm", "vbm", "vss", "2u"),
      res("Rbm", "vdd", "vbm", 10000, 0.5, kind="rppd"),
      pmos("MP3", "out", "o1", "vdd", "4u", ng=1), nmos("MN3", "out", "o1", "vss", "2u")])

# --- pad_esd: separate cell so #24 can lay it out and replace the placeholders
_pad = []
for k, (core, pad) in enumerate((("cp", "padp"), ("cn", "padn"))):
    _pad += [res("Rs%d" % k, core, pad, 4, 8),
             dict(kind="dvdd", name="Dh%d" % k, nets=dict(vdd="vdd", pad=pad, vss="vss"),
                  attrs="m=1"),
             dict(kind="dvss", name="Dl%d" % k, nets=dict(vdd="vdd", pad=pad, vss="vss"),
                  attrs="m=1"),
             dict(kind="bondpad", name="XPAD%d" % k, nets=dict(pad=pad),
                  attrs="size=80u shape=0 padtype=0")]
cell("pad_esd",
     "TX pad and ESD network (R18, R19), one per leg: 4 ohm series isolation, the PDK "
     "2 kV rail diodes to vdd/vss, and the bondpad placeholder. All values are "
     "PLACEHOLDERS: the PDK bondpad model is empty (no capacitance) and the 3.3 V-class "
     "diodes are not characterised for a 5 GHz pad. #24 replaces them with an extraction.",
     P_POWER + [("cp", "inout"), ("cn", "inout"), ("padp", "inout"), ("padn", "inout")],
     _pad)

# --- tx_top: instances of the cells above (handled specially)
TOP_INSTANCES = [
    ("Xbias", "bias", dict(vdd="vdd", vss="vss", vbn="vbn")),
    ("Xffe_en", "ffe_en", dict(vdd="vdd", vss="vss", vbn="vbn", en0="en0", en1="en1",
                               en2="en2", vbp0="vbp0", vbp1="vbp1", vbp2="vbp2")),
    ("Xmux_main", "mux2to1_cml", dict(vdd="vdd", vss="vss", ckp="ckp", ckn="ckn", dap="dap",
                                       dan="dan", dbp="dbp", dbn="dbn", outp="mp", outn="mn")),
    ("Xmux_post", "mux2to1_cml", dict(vdd="vdd", vss="vss", ckp="ckp", ckn="ckn", dap="dpap",
                                       dan="dpan", dbp="dpbp", dbn="dpbn", outp="qp", outn="qn")),
    ("Xpre_main", "predriver", dict(vdd="vdd", vss="vss", inp="mp", inn="mn", vbn="vbn",
                                     outp="pp", outn="pn")),
    ("Xpre_post", "predriver", dict(vdd="vdd", vss="vss", inp="qp", inn="qn", vbn="vbn",
                                     outp="rp", outn="rn")),
    ("Xdrv", "driver_ffe", dict(vdd="vdd", vss="vss", inp="pp", inn="pn", pip="rp", pin="rn",
                                 vbn="vbn", vbp0="vbp0", vbp1="vbp1", vbp2="vbp2",
                                 outp="cp", outn="cn")),
    ("Xpad", "pad_esd", dict(vdd="vdd", vss="vss", cp="cp", cn="cn", padp="padp",
                              padn="padn")),
    ("Xlvl", "lvl_cml2cmos", dict(vdd="vdd", vss="vss", inp="ckdp", inn="ckdn",
                                   out="ckd_cmos")),
]
TOP_PORTS = (P_POWER + [("ckp", "in"), ("ckn", "in"), ("dap", "in"), ("dan", "in"),
                         ("dbp", "in"), ("dbn", "in"), ("dpap", "in"), ("dpan", "in"),
                         ("dpbp", "in"), ("dpbn", "in"), ("en0", "in"), ("en1", "in"),
                         ("en2", "in"), ("ckdp", "in"), ("ckdn", "in"),
                         ("ckd_cmos", "out"), ("padp", "inout"), ("padn", "inout")])
TOP_DOC = ("TX high-speed path: final 2:1 mux (main and one-UI-delayed post-cursor "
           "copies), pre-drivers, FFE line driver, bias, FFE enable, CML-to-CMOS "
           "level converter and pad/ESD. The post-cursor streams dpa*/dpb* are the "
           "main streams delayed by one UI; the digital serializer must supply them "
           "(interface requirement on the digital partition).")


# ----------------------------------------------------------- symbol geometry
def sym_pins(ports):
    """Return {name: (x, y)} pin positions and the body half-height."""
    left = [p for p, d in ports if d == "in"]
    right = [p for p, d in ports if d in ("out", "inout")]
    n = max(len(left), len(right), 1)
    h = 20 * n + 10
    pos = {}
    for i, p in enumerate(left):
        pos[p] = (-120, -h + 20 + 40 * i)
    for i, p in enumerate(right):
        pos[p] = (120, -h + 20 + 40 * i)
    pos["vdd"] = (0, -h - 20)
    pos["vss"] = (0, h + 20)
    return pos, h


def write_sym(name, doc, ports):
    pos, h = sym_pins(ports)
    out = ["v {xschem version=3.4.6 file_version=1.2", "}", "G {}",
           'K {type=subcircuit', 'format="@name @pinlist @symname"',
           'template="name=x1"', "}", "V {}", "S {}", "E {}"]
    out.append("B 4 -100 %d 100 %d {}" % (-h, h))
    out.append("T {%s} 0 %d 0 0 0.3 0.3 {hcenter=true}" % (name, -h - 45))
    for pname, d in ports:
        x, y = pos[pname]
        if pname == "vdd":
            out.append("L 4 0 %d 0 %d {}" % (-h - 20, -h))
            out.append("T {vdd} 8 %d 0 0 0.2 0.2 {}" % (-h + 4))
        elif pname == "vss":
            out.append("L 4 0 %d 0 %d {}" % (h, h + 20))
            out.append("T {vss} 8 %d 0 0 0.2 0.2 {}" % (h - 24))
        elif x < 0:
            out.append("L 4 -120 %d -100 %d {}" % (y, y))
            out.append("T {%s} -95 %d 0 0 0.2 0.2 {}" % (pname, y - 6))
        else:
            out.append("L 4 100 %d 120 %d {}" % (y, y))
            out.append("T {%s} 95 %d 0 1 0.2 0.2 {}" % (pname, y - 6))
    # pins last, in pinlist order
    for pname, d in ports:
        x, y = pos[pname]
        dd = {"in": "in", "out": "out", "inout": "inout", "power": "inout"}[d]
        out.append("B 5 %g %g %g %g {name=%s dir=%s}" % (x - 2.5, y - 2.5, x + 2.5, y + 2.5,
                                                         pname, dd))
    with open(os.path.join(HERE, name + ".sym"), "w") as f:
        f.write("\n".join(out) + "\n")


# ---------------------------------------------------------- schematic writer
class Sch:
    def __init__(self):
        self.lines = []
        self.n = 0

    def wire(self, x1, y1, x2, y2):
        self.lines.append("N %g %g %g %g {}" % (x1, y1, x2, y2))

    def label(self, x, y, net):
        self.n += 1
        self.lines.append("C {lab_pin.sym} %g %g 0 0 {name=l%d lab=%s}" % (x, y, self.n, net))

    def inst(self, sym, x, y, props):
        self.lines.append("C {%s} %g %g 0 0 {%s}" % (sym, x, y, props))


def header_comment(title, doc):
    words = doc.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 74:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    body = ["* " + title + " (issue #21; generated by design/tx/gen_schematics.py)",
            "*"] + ["* " + l for l in lines] + [
        "*", "* First-cut sizing for the PROPOSED draft spec rows; not a spec result and",
        "* not a measurement. Traces to sim/pdk.json."]
    return "v {xschem version=3.4.6 file_version=1.2\n" + "\n".join(body) + "\n}"


def write_sch(name, doc, ports, devices=None, instances=None):
    s = Sch()
    # ports as iopins in a left column, in pinlist order
    for i, (pname, d) in enumerate(ports):
        y = 40 * i
        s.inst("iopin.sym", -200, y, "name=p%d lab=%s" % (i, pname))
    pos_ref = {c: sym_pins(CELLS[c]["ports"] if c in CELLS else TOP_PORTS)
               for c in {i[1] for i in (instances or [])}}
    cols = 5
    x0, y0, dx, dy = 100, 0, 360, 360
    items = []
    if devices:
        for d in devices:
            k = KINDS[d["kind"]]
            items.append((d["name"], k["sym"],
                          "name=%s model=%s spiceprefix=%s %s" % (d["name"], k["model"],
                                                                  k["prefix"], d["attrs"]),
                          {p: (v[0], v[1], v[2], v[3]) for p, v in k["pins"].items()},
                          d["nets"]))
    for iname, cname, nets in (instances or []):
        pos, _ = pos_ref[cname]
        pins = {}
        for p, (px, py) in pos.items():
            sx = -20 if px < 0 else (20 if px > 0 else 0)
            sy = -20 if (px == 0 and py < 0) else (20 if px == 0 else 0)
            pins[p] = (px, py, sx, sy)
        items.append((iname, cname + ".sym", "name=%s" % iname, pins, nets))
    cols = 4 if instances else 6
    dx, dy = (560, 520) if instances else (260, 300)
    for idx, (iname, sym, props, pins, nets) in enumerate(items):
        x = x0 + dx * (idx % cols)
        y = y0 + dy * (idx // cols) + (200 if instances else 60)
        s.inst(sym, x, y, props)
        for p, net in nets.items():
            px, py, sx, sy = pins[p]
            # stub direction: horizontal pins already extended by sx/sy sign
            s.wire(x + px, y + py, x + px + sx, y + py + sy)
            s.label(x + px + sx, y + py + sy, net)
    text = header_comment(name, doc) + "\nG {}\nK {}\nV {}\nS {}\nE {}\n" + \
        "\n".join(s.lines) + "\n"
    with open(os.path.join(HERE, name + ".sch"), "w") as f:
        f.write(text)


def main():
    for name, c in CELLS.items():
        write_sym(name, c["doc"], c["ports"])
        write_sch(name, c["doc"], c["ports"], devices=c["devices"])
    write_sym("tx_top", TOP_DOC, TOP_PORTS)
    CELLS["tx_top"] = dict(doc=TOP_DOC, ports=TOP_PORTS, devices=None)
    write_sch("tx_top", TOP_DOC, TOP_PORTS, instances=[(a, b, c) for a, b, c in TOP_INSTANCES])
    # sanity: every instance net map names exactly the cell's ports
    for iname, cname, nets in TOP_INSTANCES:
        want = {p for p, _ in CELLS[cname]["ports"]}
        if set(nets) != want:
            sys.exit("tx_top %s: pin map %s != ports %s" % (iname, sorted(nets), sorted(want)))
    for name, c in CELLS.items():
        if c["devices"]:
            for d in c["devices"]:
                if set(d["nets"]) != set(KINDS[d["kind"]]["pins"]):
                    sys.exit("%s/%s: pins %s mismatch" % (name, d["name"], sorted(d["nets"])))


if __name__ == "__main__":
    main()
