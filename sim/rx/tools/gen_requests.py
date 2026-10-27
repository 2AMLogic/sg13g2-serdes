#!/usr/bin/env python3
"""Generate the sim/rx bench bodies and `klt sim` request files.

    python3 -I sim/rx/tools/gen_requests.py            # write sim/rx/*.sp, *.request.json
    python3 -I sim/rx/tools/gen_requests.py --debug OUTDIR
        # one-unit (typ, 27 C, 1.2 V) variants of every request for a quick
        # local check; never the grid, never a recorded result

Node-stress measurements are derived from the exported netlists in
design/rx/netlists/, so they follow the schematics. Everything measured here is
sizing evidence, not a spec result.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, "..")
NET = os.path.join(SIM, "..", "..", "design", "rx", "netlists")

HBT_LIB = "libs.tech/ngspice/models/cornerHBT.lib"
CAP_LIB = "libs.tech/ngspice/models/cornerCAP.lib"
DIO_LIB = "libs.tech/ngspice/models/cornerDIO.lib"

# HBT-family PVT grid: 3 HBT corners (ganged with CAP and DIO sections, the
# spec's own ganging proposal) x 3 supplies x 3 temperatures = 27 points. It is
# a crossed grid, not `corners.units`: the fleet runner (klt 0.7.0) silently
# ignores `corners.units` and runs one default corner.
PROCESS = [
    {"name": "hbt_typ", "sections": [{"lib": HBT_LIB, "section": "hbt_typ"},
                                     {"lib": CAP_LIB, "section": "cap_typ"},
                                     {"lib": DIO_LIB, "section": "dio_tt"}]},
    {"name": "hbt_bcs", "sections": [{"lib": HBT_LIB, "section": "hbt_bcs"},
                                     {"lib": CAP_LIB, "section": "cap_bcs"},
                                     {"lib": DIO_LIB, "section": "dio_ff"}]},
    {"name": "hbt_wcs", "sections": [{"lib": HBT_LIB, "section": "hbt_wcs"},
                                     {"lib": CAP_LIB, "section": "cap_wcs"},
                                     {"lib": DIO_LIB, "section": "dio_ss"}]},
]

VC_MAX = 1.32   # DR-003: no HBT collector node above this
VBE_REV = 1.0   # DR-003: no reverse Vbe above this


def parse_subckt(cell):
    """(ports, [(name, c, b, e)]) of the exported cell netlist."""
    ports, qs, inside = None, [], False
    for line in open(os.path.join(NET, cell + ".spice")):
        t = line.split()
        if not t or line.startswith("*"):
            continue
        if t[0] == ".subckt" and t[1] == cell:
            ports, inside = t[2:], True
        elif t[0] == ".ends":
            inside = False
        elif inside and t[0].startswith("XQ") or inside and t[0].startswith("XS"):
            if "npn13G2" in t:
                qs.append((t[0][1:], t[1], t[2], t[3]))
    return ports, qs


def stress_meas(inst, cell, portmap, prefix, kind):
    """`.meas` cards for max collector V and max reverse Vbe of every HBT.

    kind "dc": operating-point value via a two-point dummy sweep (`at=0`);
    kind "tran": maximum over the run. Plain `spice` cards, because the fleet
    runner's `expr` support is not usable (see sim/rx/README.md).
    """
    ports, qs = parse_subckt(cell)

    def node(n):
        if n in ("0", "vss"):
            return "0"
        if n in portmap:
            return portmap[n]
        return "%s.%s" % (inst.lower(), n)

    # ngspice limits par() to 99 calls per deck, so differences go through a
    # B source and the .meas reads that node (also keeps tran and dc alike).
    lines, out = [], []
    for q, c, b, e in qs:
        base = "%s_%s_%s" % (prefix, inst.lower(), q.lower())
        vbe = base + "_vbe_node"
        lines.append("B%s %s 0 V=v(%s)-v(%s)" % (vbe, vbe, node(e), node(b)))
        for suffix, sig, lim in (("_vc_max", "v(%s)" % node(c), VC_MAX), ("_vbe_rev_max", "v(%s)" % vbe, VBE_REV)):
            name = base + suffix
            if kind == "dc":
                card = ".meas dc %s find %s at=0" % (name, sig)
            else:
                card = ".meas tran %s max %s" % (name, sig)
            out.append({"name": name, "unit": "V", "spice": card, "limits": {"max": lim}})
    return lines, out


def request(netlist, analysis, measurements, corners, extra_options=None):
    opts = {"stage_model_inputs": True, "timeout_s": 120, "keep_artifacts": False}
    opts.update(extra_options or {})
    return {
        "engine": "ngspice",
        "netlist": netlist,
        "models": {"pdk": "ihp-sg13g2", "lib": HBT_LIB},
        "corners": corners,
        "analysis": analysis,
        "measurements": measurements,
        "options": opts,
    }


def corner_axes(debug):
    if debug:
        return {"process": PROCESS[:1], "temperature_c": [27], "supply_v": {"vdd": [1.2]}}
    return {"process": PROCESS, "temperature_c": [-40, 27, 125],
            "supply_v": {"vdd": [1.08, 1.2, 1.32]}}


# ---------------------------------------------------------------- CTLE bench
def ctle_body():
    L = ["* CTLE sizing bench (issue #22): 8 copies of ctle, one per peaking code,",
         "* driven by the same ideal differential source. Sizing evidence, not a spec result.",
         "* vcm and the control levels track the supply (vcm = 0.7917 vdd; control",
         "* high = vdd, low = vdd - 0.25 V). Output load is a 80 fF placeholder per side",
         "* (stand-in for the four latch inputs; replaced by extraction in #24/#28).",
         ".include ../../design/rx/netlists/ctle.spice",
         "Vdd vdd 0 1.2",
         "Bvcm vcm 0 V=0.7917*v(vdd)",
         "Vip inp vcm dc 0 ac 0.5",
         "Vin inn vcm dc 0 ac -0.5"]
    for c in range(8):
        for k in range(3):
            bit = (c >> k) & 1
            hi, lo = "v(vdd)", "v(vdd)-0.25"
            L.append("Bk%d_%d c%dk%d 0 V=%s" % (c, k, c, k, hi if bit else lo))
            L.append("Bk%d_%db c%dk%db 0 V=%s" % (c, k, c, k, lo if bit else hi))
        L.append("Xd%d inp inn vcm vdd 0 c%dk0 c%dk0b c%dk1 c%dk1b c%dk2 c%dk2b op%d on%d ctle"
                 % (c, c, c, c, c, c, c, c, c))
        L.append("Clp%d op%d 0 80f" % (c, c))
        L.append("Cln%d on%d 0 80f" % (c, c))
        L.append("Bd%d dif%d 0 V=v(op%d)-v(on%d)" % (c, c, c, c))
    return "\n".join(L) + "\n"


def ctle_ac_meas():
    """Gains at 0.1, 2.5 and 5 GHz per code. Peaking (5 GHz minus 0.1 GHz) and
    the R10 comparison are formed in sim/rx/tools/make_record.py."""
    m = []
    for c in range(8):
        for tag, f in (("g0p1g", "1e8"), ("g2p5g", "2.5e9"), ("g5g", "5e9")):
            n = "ctle_c%d_%s_db" % (c, tag)
            m.append({"name": n, "unit": "dB",
                      "spice": ".meas ac %s find vdb(dif%d) at=%s" % (n, c, f)})
    return m


def ctle_op_body(extra=()):
    # same circuit; operating point read through a two-point dummy dc sweep
    return ctle_body().replace("Vip inp vcm dc 0 ac 0.5", "Vip inp vcm dc 0").replace(
        "Vin inn vcm dc 0 ac -0.5", "Vin inn vcm dc 0") + "Vdmy dmy 0 0\nRdmy dmy 0 1k\n" + "".join(l + "\n" for l in extra)


def ctle_op_meas():
    m, lines = [], []
    for c in range(8):
        pm = {"inp": "inp", "inn": "inn", "vcm": "vcm", "vdd": "vdd", "outp": "op%d" % c,
              "outn": "on%d" % c}
        for k in range(3):
            pm["c%d" % k] = "c%dk%d" % (c, k)
            pm["c%db" % k] = "c%dk%db" % (c, k)
        l_, m_ = stress_meas("Xd%d" % c, "ctle", pm, "ctle_c%d" % c, "dc")
        lines += l_
        m += m_
        m.append({"name": "ctle_c%d_outcm" % c, "unit": "V",
                  "spice": ".meas dc ctle_c%d_outcm find v(ocm%d) at=0" % (c, c)})
        lines.append("Bocm%d ocm%d 0 V=(v(op%d)+v(on%d))/2" % (c, c, c, c))
    return lines, m


# ----------------------------------------------------------- pad/term bench
def pad_body():
    L = ["* Termination + pad first-look bench (issue #22). PLACEHOLDER pad capacitance",
         "* (Cpad in rx_term_pad), ideal resistors, ESD from the PDK diode models, the CTLE",
         "* (code 0) hanging on the pad. NOT a return-loss result: R9 SDD11 is graded on",
         "* extracted layout in #24/#28. Only |Zdiff| at low frequency and at 5 GHz.",
         ".include ../../design/rx/netlists/rx_term_pad.spice",
         ".include ../../design/rx/netlists/ctle.spice",
         "Vdd vdd 0 1.2",
         "Bvcm vcm 0 V=0.7917*v(vdd)",
         "Vip padp vcm dc 0 ac 0.5",
         "Vin padn vcm dc 0 ac -0.5",
         "Xpad padp padn vcm vdd 0 inp inn rx_term_pad",
         "Xc inp inn vcm vdd 0 kl klb kl klb kl klb op on ctle",
         "Bkl kl 0 V=v(vdd)-0.25",
         "Bklb klb 0 V=v(vdd)",
         "Clp op 0 80f", "Cln on 0 80f",
         "Hip iz 0 Vip 1"]
    return "\n".join(L) + "\n"


def pad_meas():
    """Differential drive current for 1 V differential (Hip: 1 ohm
    transresistance, so vm(iz) is |I| in A); |Zdiff| = 1/|I| in the record."""
    return [
        {"name": "pad_idiff_0p1g_a", "unit": "A", "spice": ".meas ac pad_idiff_0p1g_a find vm(iz) at=1e8"},
        {"name": "pad_idiff_5g_a", "unit": "A", "spice": ".meas ac pad_idiff_5g_a find vm(iz) at=5e9"},
    ]


# --------------------------------------------------------------- latch bench
def latch_body(extra=()):
    L = ["* Latch + clock-buffer sizing bench (issue #22). Sizing evidence, not a spec result.",
         "* Ideal 5 GHz clock source (the SG13G2 clock candidates do not meet R20, see",
         "* spec/clock-requirement.md): common mode 0.8333 vdd, +-150 mV per phase, ideal",
         "* quadrature and 50 % duty. Data: +-10 mV differential toggling every 200 ps",
         "* inside the hold phase, common mode 0.8167 vdd (the CTLE output common mode).",
         ".include ../../design/rx/netlists/latch_cml.spice",
         ".include ../../design/rx/netlists/clk_buf_quad.spice",
         "Vdd vdd 0 1.2"]
    for n, ph in (("ck0", 0), ("ck180", 180), ("ck90", 90), ("ck270", 270)):
        L.append("B%s %s 0 V=0.8333*v(vdd)+0.15*sin(2*3.14159265*5e9*time+%g*3.14159265/180)"
                 % (n, n, ph))
    L += ["Xclk ck0 ck180 ck90 ck270 vdd 0 b0 b180 b90 b270 clk_buf_quad",
          "Cb0 b0 0 20f", "Cb1 b180 0 20f", "Cb2 b90 0 20f", "Cb3 b270 0 20f",
          "Bdcm dcm 0 V=0.8167*v(vdd)",
          "Vdp dp dcm pulse(-0.01 0.01 250p 20p 20p 180p 400p)",
          "Vdn dn dcm pulse(0.01 -0.01 250p 20p 20p 180p 400p)",
          "Xl dp dn b0 b180 vdd 0 qp qn latch_cml",
          "Bck ck 0 V=v(b0)-v(b180)",
          "Bq q 0 V=v(qp)-v(qn)"] + list(extra)
    return "\n".join(L) + "\n"


def latch_meas():
    # Regeneration time: from the clock edge that closes the sample phase (ck
    # falling through 0) to |q| reaching 0.25 V, about 85 % of the +-0.3 V
    # swing. The hold pair regenerates only during that phase. First-look
    # limit: the half period at 5 GHz (100 ps), after which the next sample
    # phase opens. Cycle selection is by td= (data toggles at 250 ps + 400 ps k).
    m = [
        {"name": "latch_t_regen_up", "unit": "s",
         "spice": ".meas tran latch_t_regen_up trig v(ck) val=0 fall=1 td=2.35n targ v(q) val=0.25 rise=1 td=2.35n",
         "limits": {"max": 100e-12}},
        {"name": "latch_t_regen_dn", "unit": "s",
         "spice": ".meas tran latch_t_regen_dn trig v(ck) val=0 fall=1 td=2.55n targ v(q) val=-0.25 fall=1 td=2.55n",
         "limits": {"max": 100e-12}},
        {"name": "latch_q_max_v", "unit": "V", "spice": ".meas tran latch_q_max_v max v(q) from=2n to=3n"},
        {"name": "latch_q_min_v", "unit": "V", "spice": ".meas tran latch_q_min_v min v(q) from=2n to=3n"},
    ]
    pm_clk = {"ck0": "ck0", "ck180": "ck180", "ck90": "ck90", "ck270": "ck270", "vdd": "vdd",
              "b0": "b0", "b180": "b180", "b90": "b90", "b270": "b270"}
    pm_lat = {"dp": "dp", "dn": "dn", "clkp": "b0", "clkn": "b180", "vdd": "vdd",
              "qp": "qp", "qn": "qn"}
    l1, m1 = stress_meas("Xclk", "clk_buf_quad", pm_clk, "clk", "tran")
    l2, m2 = stress_meas("Xl", "latch_cml", pm_lat, "latch", "tran")
    return l1 + l2, m + m1 + m2


def main(argv):
    debug = len(argv) > 1 and argv[1] == "--debug"
    out = argv[2] if debug else SIM
    os.makedirs(out, exist_ok=True)
    units = corner_axes(debug)
    op_lines, op_meas = ctle_op_meas()
    lat_lines, lat_meas = latch_meas()
    files = {
        "ctle_ac": (ctle_body(), {"kind": "ac", "args": "lin 300 1e8 3e10"}, ctle_ac_meas()),
        "ctle_op": (ctle_op_body(op_lines), {"kind": "dc", "args": "Vdmy 0 1m 1m"}, op_meas),
        "pad_ac": (pad_body(), {"kind": "ac", "args": "lin 300 1e8 3e10"}, pad_meas()),
        "latch_regen": (latch_body(lat_lines), {"kind": "tran", "args": "2p 3n"}, lat_meas),
    }
    for name, (body, ana, meas) in files.items():
        rel = os.path.relpath(NET, out)
        with open(os.path.join(out, name + ".sp"), "w") as f:
            f.write(body.replace("../../design/rx/netlists", rel))
        req = request(name + ".sp", ana, meas, units)
        with open(os.path.join(out, name + ".request.json"), "w") as f:
            json.dump(req, f, indent=2)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
