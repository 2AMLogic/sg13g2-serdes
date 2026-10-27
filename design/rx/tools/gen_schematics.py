#!/usr/bin/env python3
"""Emit the RX xschem sheets and symbols under design/rx/.

The committed .sch/.sym files are the source of truth for the netlists; this
script is how they were drawn (lab_pin-per-pin style, no routed wires), and
rerunning it must reproduce them byte for byte. Edit a value here, rerun, then
export with design/check-netlists.sh --write and commit all three together.

    python3 -I design/rx/tools/gen_schematics.py
"""
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# pin offsets (rot 0) of the symbols used
PINS = {
    "sg13g2_pr/npn13G2.sym": {"C": (20, -30), "B": (-20, 0), "E": (20, 30), "S": (20, 0)},
    "devices/res.sym": {"P": (0, -30), "M": (0, 30)},
    "sg13g2_pr/cap_cmim.sym": {"c0": (0, -30), "c1": (0, 30)},
    "devices/capa.sym": {"p": (0, -30), "m": (0, 30)},
    "sg13g2_pr/diodevdd_2kv.sym": {"vdd": (0, -30), "pad": (0, 30), "vss": (-30, 0)},
    "sg13g2_pr/diodevss_2kv.sym": {"vdd": (-30, 0), "pad": (0, -30), "vss": (0, 30)},
    "sg13g2_pr/sg13_lv_nmos.sym": {"D": (20, -30), "G": (-20, 0), "S": (20, 30), "B": (20, 0)},
    "sg13g2_pr/sg13_lv_pmos.sym": {"D": (20, 30), "G": (-20, 0), "S": (20, -30), "B": (20, 0)},
}

# block interfaces: name -> (inputs/left, outputs/right)
BLOCKS = {
    "rx_term_pad": (["padp", "padn", "vcm", "vdd", "vss"], ["inp", "inn"]),
    "ctle": (["inp", "inn", "vcm", "vdd", "vss", "c0", "c0b", "c1", "c1b", "c2", "c2b"],
             ["outp", "outn"]),
    "latch_cml": (["dp", "dn", "clkp", "clkn", "vdd", "vss"], ["qp", "qn"]),
    "clk_buf_quad": (["ck0", "ck180", "ck90", "ck270", "vdd", "vss"],
                     ["b0", "b180", "b90", "b270"]),
    "lvl_cml2cmos": (["ip", "in", "vdd", "vss"], ["op"]),
    "rx_top": (["padp", "padn", "vcm", "ck0", "ck180", "ck90", "ck270",
                "c0", "c0b", "c1", "c1b", "c2", "c2b", "vdd", "vss"],
               ["d0", "d180", "e90", "e270"]),
}


class Sheet:
    def __init__(self, name, title):
        self.name = name
        self.title = title
        self.items = []
        self.n = 0
        self.pitch = (300, 400) if name == "rx_top" else (160, 130)

    def _at(self, col, row):
        return col * self.pitch[0] + 100, row * self.pitch[1] + 60

    def _lab(self, net, x, y, left):
        self.n += 1
        self.items.append(
            "C {devices/lab_pin.sym} %g %g %d 0 {name=l%d sig_type=std_logic lab=%s}"
            % (x, y, 0 if left else 2, self.n, net))

    def dev(self, sym, props, nets, col, row):
        x, y = self._at(col, row)
        self.items.append("C {%s} %g %g 0 0 {%s}" % (sym, x, y, props))
        for pin, net in nets.items():
            px, py = PINS[sym][pin]
            self._lab(net, x + px, y + py, px <= 0)

    def npn(self, name, c, b, e, nx, col, row, s="vss"):
        self.dev("sg13g2_pr/npn13G2.sym",
                 "name=%s model=npn13G2 spiceprefix=X Nx=%s" % (name, nx),
                 {"C": c, "B": b, "E": e, "S": s}, col, row)

    def res(self, name, a, b, r, col, row, body=None):
        # Ideal generic resistor: the PDK rsil/rppd models are r3_cmc OSDI
        # models, which the host ngspice and the batch fleet cannot load today
        # (sim/README.md). Layout (#24) swaps in rsil/rppd and re-simulates.
        self.dev("devices/res.sym", "name=%s value=%.4g m=1" % (name, r),
                 {"P": a, "M": b}, col, row)

    def mim(self, name, a, b, side_um, col, row):
        self.dev("sg13g2_pr/cap_cmim.sym",
                 "name=%s model=cap_cmim w=%gu l=%gu m=1 spiceprefix=X" % (name, side_um, side_um),
                 {"c0": a, "c1": b}, col, row)

    def cap(self, name, a, b, val, col, row):
        self.dev("devices/capa.sym", "name=%s m=1 value=%s" % (name, val),
                 {"p": a, "m": b}, col, row)

    def mos(self, kind, name, d, g, s, b, w, l, col, row):
        sym = "sg13g2_pr/sg13_lv_%smos.sym" % kind
        self.dev(sym, "name=%s l=%su w=%su ng=1 m=1 model=sg13_lv_%smos spiceprefix=X"
                 % (name, l, w, kind), {"D": d, "G": g, "S": s, "B": b}, col, row)

    def inst(self, block, name, conns, col, row):
        x, y = self._at(col, row)
        self.items.append("C {%s.sym} %g %g 0 0 {name=%s}" % (block, x, y, name))
        for pin, (px, py) in sym_pins(block).items():
            self._lab(conns[pin], x + px, y + py, px <= 0)

    def text(self, s, col, row):
        x, y = self._at(col, row)
        self.items.append("T {%s} %g %g 0 0 0.3 0.3 {}" % (s, x - 60, y - 50))

    def render(self):
        ins, outs = BLOCKS[self.name]
        head = ["v {xschem version=3.4.6 file_version=1.2"]
        head += ["* " + ln for ln in self.title.strip().splitlines()]
        head += ["}", "G {}", "K {}", "V {}", "S {}", "E {}"]
        ports = []
        for i, p in enumerate(ins + outs):
            ports.append("C {devices/iopin.sym} -120 %d 0 0 {name=p%d lab=%s}" % (-200 + 20 * i, i + 1, p))
        return "\n".join(head + ports + self.items) + "\n"


def sym_pins(block):
    ins, outs = BLOCKS[block]
    pins = {}
    for i, p in enumerate(ins):
        pins[p] = (-30, -((max(len(ins), len(outs)) - 1) * 10) + 20 * i)
    for i, p in enumerate(outs):
        pins[p] = (30, -((max(len(ins), len(outs)) - 1) * 10) + 20 * i)
    return pins


def render_sym(block):
    ins, outs = BLOCKS[block]
    n = max(len(ins), len(outs))
    half = n * 10 + 10
    pins = sym_pins(block)
    lines = ["v {xschem version=3.4.6 file_version=1.2", "* %s block symbol; see %s.sch" % (block, block), "}",
             "G {}",
             'K {type=subcircuit\nformat="@name @pinlist @symname"\ntemplate="name=X1"}',
             "V {}", "S {}", "E {}",
             "L 4 -30 %d 30 %d {}" % (-half, -half), "L 4 -30 %d 30 %d {}" % (half, half),
             "L 4 -30 %d -30 %d {}" % (-half, half), "L 4 30 %d 30 %d {}" % (-half, half)]
    for p in ins:
        x, y = pins[p]
        lines.append("B 5 %g %g %g %g {name=%s dir=in}" % (x - 2.5, y - 2.5, x + 2.5, y + 2.5, p))
        lines.append("T {%s} %g %g 0 0 0.2 0.2 {}" % (p, x + 5, y - 4))
    for p in outs:
        x, y = pins[p]
        lines.append("B 5 %g %g %g %g {name=%s dir=out}" % (x - 2.5, y - 2.5, x + 2.5, y + 2.5, p))
        lines.append("T {%s} %g %g 0 1 0.2 0.2 {}" % (p, x - 5, y - 4))
    lines.append("T {@name} -30 %d 0 0 0.25 0.25 {}" % (half + 8))
    lines.append("T {%s} -25 %d 0 0 0.2 0.2 {}" % (block, -half - 15))
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Sizing constants. Every value is a first-pass sizing choice, not a result;
# the record under sim/rx/records/ says what each was checked against.
# --------------------------------------------------------------------------
RL_CTLE = 60
RT1 = 220
RU = 440
RL_LATCH = 100
RE_LATCH = 40
NX_LATCH = 2


def build_term_pad():
    s = Sheet("rx_term_pad", """
rx_term_pad: 100 ohm differential termination, pad capacitance placeholder and
the smallest PDK ESD clamp pair on each pad (DR-001, spec R9/R18/R19).
Resistors are ideal (PDK rsil/rppd are OSDI models, not simulable today).
Termination is 2 x 50 ohm to the vcm pin (bias supplied from outside this cell).
Cpad_* are PLACEHOLDER capacitances (the PDK bondpad model is empty): layout
and extraction (#24) replace them. Nothing here is a measured value.
""")
    s.res("Rtp", "padp", "vcm", 50, 0, 0)
    s.res("Rtn", "padn", "vcm", 50, 1, 0)
    s.cap("Cpad_p", "padp", "vss", "50f", 2, 0)
    s.cap("Cpad_n", "padn", "vss", "50f", 3, 0)
    s.dev("sg13g2_pr/diodevdd_2kv.sym", "name=Desd_pu model=diodevdd_2kv m=1 spiceprefix=X",
          {"vdd": "vdd", "pad": "padp", "vss": "vss"}, 0, 1)
    s.dev("sg13g2_pr/diodevss_2kv.sym", "name=Desd_pd model=diodevss_2kv m=1 spiceprefix=X",
          {"vdd": "vdd", "pad": "padp", "vss": "vss"}, 1, 1)
    s.dev("sg13g2_pr/diodevdd_2kv.sym", "name=Desd_nu model=diodevdd_2kv m=1 spiceprefix=X",
          {"vdd": "vdd", "pad": "padn", "vss": "vss"}, 2, 1)
    s.dev("sg13g2_pr/diodevss_2kv.sym", "name=Desd_nd model=diodevss_2kv m=1 spiceprefix=X",
          {"vdd": "vdd", "pad": "padn", "vss": "vss"}, 3, 1)
    s.res("Rsp", "padp", "inp", 4, 0, 2)
    s.res("Rsn", "padn", "inn", 4, 1, 2)
    return s


def build_ctle():
    s = Sheet("ctle", """
ctle: two parallel paths summed into RL. Path 1 is a flat HBT pair (always
on). Path 2 is AC-coupled (MIM + bias resistor) and built from a fixed
weight-7 cell plus binary cells of weight 1/2/4, each steered +/- onto the
outputs by a switch pair driven from (cK, cKb). Peaking at HF relative to DC
is 1 + 2*code*gu/g1 with code = c2c1c0 in 0..7, so 8 steps from 0 dB; total
current, and so the output common mode, is the same for every code. HBT only
(spec R3). Control inputs are differential levels (cK high = positive).
Sizing choice, not a result.
""")
    s.npn("Q1", "outn", "inp", "e1", 2, 0, 0)
    s.npn("Q2", "outp", "inn", "e2", 2, 1, 0)
    s.res("Rt1a", "e1", "vss", RT1, 2, 0)
    s.res("Rt1b", "e2", "vss", RT1, 3, 0)
    s.res("RLa", "vdd", "outn", RL_CTLE, 4, 0)
    s.res("RLb", "vdd", "outp", RL_CTLE, 5, 0)
    s.mim("Cca", "inp", "hpp", 10, 0, 1)
    s.mim("Ccb", "inn", "hpn", 10, 1, 1)
    s.res("Rca", "hpp", "vcm", 2000, 2, 1)
    s.res("Rcb", "hpn", "vcm", 2000, 3, 1)
    # fixed cell, weight 7, positive polarity
    s.npn("Qfa", "outn", "hpp", "efa", 7, 0, 2)
    s.npn("Qfb", "outp", "hpn", "efb", 7, 1, 2)
    s.res("Rfa", "efa", "vss", RU / 7.0, 2, 2)
    s.res("Rfb", "efb", "vss", RU / 7.0, 3, 2)
    for k, w in enumerate((1, 2, 4)):
        r = 3 + k
        s.npn("Qa%d" % k, "ca%d" % k, "hpp", "ea%d" % k, w, 0, r)
        s.npn("Qb%d" % k, "cb%d" % k, "hpn", "eb%d" % k, w, 1, r)
        s.res("Ra%d" % k, "ea%d" % k, "vss", RU / w, 2, r)
        s.res("Rb%d" % k, "eb%d" % k, "vss", RU / w, 3, r)
        s.npn("Spa%d" % k, "outn", "c%d" % k, "ca%d" % k, w, 4, r)
        s.npn("Sna%d" % k, "outp", "c%db" % k, "ca%d" % k, w, 5, r)
        s.npn("Spb%d" % k, "outp", "c%d" % k, "cb%d" % k, w, 6, r)
        s.npn("Snb%d" % k, "outn", "c%db" % k, "cb%d" % k, w, 7, r)
    return s


def build_latch():
    s = Sheet("latch_cml", """
latch_cml: HBT CML sampling latch. Sample pair (dp/dn) and cross-coupled hold
pair share nothing but the loads; each pair has its own clocked tail HBT
(clkp gates sample, clkn gates hold) with emitter resistor, so the stack is
two levels (pair + tail) rather than three, because 1.2 V does not fit the
conventional three-level latch with ~0.85 V Vbe. Transparent while clkp is
high. Sizing choice, not a result.
""")
    nx = NX_LATCH
    s.npn("Qs1", "qn", "dp", "es", nx, 0, 0)
    s.npn("Qs2", "qp", "dn", "es", nx, 1, 0)
    s.npn("Qh1", "qn", "qp", "eh", nx, 2, 0)
    s.npn("Qh2", "qp", "qn", "eh", nx, 3, 0)
    s.npn("Qts", "es", "clkp", "ets", nx, 0, 1)
    s.npn("Qth", "eh", "clkn", "eth", nx, 2, 1)
    s.res("Rts", "ets", "vss", RE_LATCH, 1, 1)
    s.res("Rth", "eth", "vss", RE_LATCH, 3, 1)
    s.res("RLp", "vdd", "qp", RL_LATCH, 4, 0)
    s.res("RLn", "vdd", "qn", RL_LATCH, 5, 0)
    return s


def build_clk():
    s = Sheet("clk_buf_quad", """
clk_buf_quad: receiving CML buffers for the four clock phases (interface:
spec/clock-requirement.md, R20: 5 GHz, 0/90/180/270 deg, duty +-1 %,
quadrature +-2 deg). Two chains, each two stages: ck0/ck180 -> b0/b180 and
ck90/ck270 -> b90/b270. The clock SOURCE is not designed here; no quadrature
correction is attempted, the cell passes the source's phase error through.
Output common mode is set low (about 0.75 V) to drive the latch tail bases.
Sizing choice, not a result.
""")
    chains = (("ck0", "ck180", "b0", "b180", "i"), ("ck90", "ck270", "b90", "b270", "q"))
    for c, (ip, in_, op, on, tag) in enumerate(chains):
        r = 2 * c
        # stage 1: small load so common mode stays near 1.0 V
        s.npn("Q%s1a" % tag, "m%sn" % tag, ip, "t%s1" % tag, 2, 0, r)
        s.npn("Q%s1b" % tag, "m%sp" % tag, in_, "t%s1" % tag, 2, 1, r)
        s.res("Rt%s1" % tag, "t%s1" % tag, "vss", 85, 2, r)
        s.res("RL%s1a" % tag, "vdd", "m%sn" % tag, 100, 3, r)
        s.res("RL%s1b" % tag, "vdd", "m%sp" % tag, 100, 4, r)
        # stage 2: larger load, low common mode output
        s.npn("Q%s2a" % tag, on, "m%sn" % tag, "t%s2" % tag, 2, 0, r + 1)
        s.npn("Q%s2b" % tag, op, "m%sp" % tag, "t%s2" % tag, 2, 1, r + 1)
        s.res("Rt%s2" % tag, "t%s2" % tag, "vss", 85, 2, r + 1)
        s.res("RL%s2a" % tag, "vdd", on, 225, 3, r + 1)
        s.res("RL%s2b" % tag, "vdd", op, 225, 4, r + 1)
    return s


def build_lvl():
    s = Sheet("lvl_cml2cmos", """
lvl_cml2cmos: latch-to-CMOS conversion. NMOS differential pair with PMOS
mirror load, then two inverters. Thin-oxide MOS only (spec R3). The PDK MOS
models need OSDI, which the batch fleet cannot stage today (see sim/README.md),
so this cell is NOT simulated in this change.
""")
    s.mos("n", "Mn1", "x", "ip", "tl", "vss", 4, 0.13, 0, 0)
    s.mos("n", "Mn2", "y", "in", "tl", "vss", 4, 0.13, 1, 0)
    s.mos("n", "Mnt", "tl", "vdd", "vss", "vss", 2, 0.5, 2, 0)
    s.mos("p", "Mp1", "x", "x", "vdd", "vdd", 4, 0.13, 0, 1)
    s.mos("p", "Mp2", "y", "x", "vdd", "vdd", 4, 0.13, 1, 1)
    s.mos("p", "Mpi1", "z", "y", "vdd", "vdd", 2, 0.13, 0, 2)
    s.mos("n", "Mni1", "z", "y", "vss", "vss", 1, 0.13, 1, 2)
    s.mos("p", "Mpi2", "op", "z", "vdd", "vdd", 4, 0.13, 2, 2)
    s.mos("n", "Mni2", "op", "z", "vss", "vss", 2, 0.13, 3, 2)
    return s


def build_top():
    s = Sheet("rx_top", """
rx_top: RX high-speed path (DR-001): termination/pad -> CTLE -> four CML
sampling latches (data 0/180 deg, edge 90/270 deg, Alexander bang-bang) with
the 5 GHz clock buffers, then latch-to-CMOS conversion. Bias generation (vcm,
control levels) and the clock source are NOT in this cell. Sizing choice, not
a result.
""")
    s.inst("rx_term_pad", "Xpad", {"padp": "padp", "padn": "padn", "vcm": "vcm", "vdd": "vdd",
                                   "vss": "vss", "inp": "inp", "inn": "inn"}, 0, 0)
    c = {"inp": "inp", "inn": "inn", "vcm": "vcm", "vdd": "vdd", "vss": "vss",
         "outp": "dp", "outn": "dn"}
    for k in ("c0", "c0b", "c1", "c1b", "c2", "c2b"):
        c[k] = k
    s.inst("ctle", "Xctle", c, 1, 0)
    s.inst("clk_buf_quad", "Xclk", {"ck0": "ck0", "ck180": "ck180", "ck90": "ck90",
                                    "ck270": "ck270", "vdd": "vdd", "vss": "vss",
                                    "b0": "b0", "b180": "b180", "b90": "b90",
                                    "b270": "b270"}, 2, 0)
    lat = (("Xlat_d0", "b0", "b180", "d0"), ("Xlat_d180", "b180", "b0", "d180"),
           ("Xlat_e90", "b90", "b270", "e90"), ("Xlat_e270", "b270", "b90", "e270"))
    for i, (n, cp, cn, o) in enumerate(lat):
        s.inst("latch_cml", n, {"dp": "dp", "dn": "dn", "clkp": cp, "clkn": cn,
                                "vdd": "vdd", "vss": "vss", "qp": "qp_" + o, "qn": "qn_" + o}, i, 1)
        s.inst("lvl_cml2cmos", "Xlvl_" + o, {"ip": "qp_" + o, "in": "qn_" + o, "op": o,
                                             "vdd": "vdd", "vss": "vss"}, i, 2)
    return s


def main():
    sheets = [build_term_pad(), build_ctle(), build_latch(), build_clk(), build_lvl(), build_top()]
    for sh in sheets:
        with open(os.path.join(OUT, sh.name + ".sch"), "w") as f:
            f.write(sh.render())
        with open(os.path.join(OUT, sh.name + ".sym"), "w") as f:
            f.write(render_sym(sh.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
