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

sys.path.insert(0, os.path.join(SIM, "..", "tools"))
from hbt_corners import HBT_LIB, CAP_LIB, DIO_LIB, corner_axes  # noqa: E402

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


def request(netlist, analysis, measurements, corners, extra_options=None, lib=HBT_LIB):
    opts = {"stage_model_inputs": True, "timeout_s": 120, "keep_artifacts": False}
    opts.update(extra_options or {})
    return {
        "engine": "ngspice",
        "netlist": netlist,
        "models": {"pdk": "ihp-sg13g2", "lib": lib},
        "corners": corners,
        "analysis": analysis,
        "measurements": measurements,
        "options": opts,
    }


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


# ---------------------------------------------- rppd termination bench (#240)
# RX termination bench with the PDK's own rppd model (r3_cmc OSDI) in place of
# the ideal 50 ohm legs of design/rx/netlists/rx_term_pad.spice, run over the
# resistor corners (R9 gate G1 of #238). The tolerance figures and the p.11
# window members trace to spec/sources/rppd-tolerance-window.md. design/rx
# itself is unchanged (the termination re-point is #143): the series 4 ohm
# legs are metal stand-ins and stay ideal, as do the CTLE-internal resistors.
RES_LIB = "libs.tech/ngspice/models/cornerRES.lib"
OSDI = ["$PDK_ROOT/ihp-sg13g2/libs.tech/ngspice/osdi/" + f
        for f in ("psp103.osdi", "psp103_nqs.osdi", "r3_cmc.osdi", "mosvar.osdi")]
# Geometry: p.11 recommends w >= 2 um for precision resistors, and the layout
# minimums (SG13G2_os_layout_rules.pdf 6.3: 0.50 um GatPoly width and SalBlock
# length) forbid a single 50 ohm strip at w = 2 um (it would need
# l = 50*2.006/260 = 0.386 um). Two 100 ohm strips in parallel instead:
# l = 100*(2+0.006)/260 = 0.7715 um -> 49.998 ohm per side at rsh = 260.
RPPD_W, RPPD_L, RPPD_M = "2u", "0.7715u", 2
# Window edges from the source note: the p.11 min/max rsh and DWRPPD columns
# folded into one effective sheet resistance at w = 2 um (the r3_cmc model has
# no width-delta parameter; xw is fixed at the 6 nm target):
#   235 * 2.006/2.036 = 231.537,  285 * 2.006/1.976 = 289.327.
RSH_RPPD_P11_LO = 231.537
RSH_RPPD_P11_HI = 289.327


def pad_rppd_body(win=False):
    L = ["* RX termination rppd corner bench (issue #240, R9 gate G1): the two ideal",
         "* 50 ohm legs of design/rx/rx_term_pad are replaced by PDK rppd instances",
         "* (w=%s, l=%s, m=%d -> 49.998 ohm per side at rsh = 260); everything else" % (RPPD_W, RPPD_L, RPPD_M),
         "* is pad_ac as-is: PLACEHOLDER pad capacitance, ideal 4 ohm metal series",
         "* stand-ins, ideal CTLE-internal resistors, code-0 CTLE hanging on the pad.",
         "* NOT a return-loss result: R9 SDD11 is graded on extracted layout (#24/#28).",
         "* Tolerance figures trace to spec/sources/rppd-tolerance-window.md (PDK",
         "* process spec Rev. 1.2 p.11 vs cornerRES.lib; discrepancy reported, not",
         "* reconciled). Sizing evidence from a simulation, never a measurement."]
    if win:
        L += ["* p.11 window member: the corners.params axis overrides rsh_rppd with",
              "* the width-delta-folded window edges derived in the source note (the",
              "* deck-level .param below is the default the override addresses)."]
    L.append(".include ../../design/rx/netlists/ctle.spice")
    if win:
        L.append(".param rsh_rppd = 260.0")
    # rx_term_pad inlined: its ideal termination legs become rppd instances
    # (r3_cmc needs the body node bn, tied to ground), the cell's vss port maps
    # to ground exactly as the Xpad call in pad_ac does, and the subckt wrapper
    # is dropped. A changed netlist fails generation instead of substituting
    # silently.
    nsub = 0
    for line in open(os.path.join(NET, "rx_term_pad.spice")):
        if line.startswith("**") or line.startswith(".subckt") or line.startswith(".ends"):
            continue
        t = line.split()
        if not t or line.startswith("*"):
            continue
        if t[0] in ("Rtp", "Rtn") and len(t) >= 4 and t[3] == "50":
            L.append("X%s %s %s 0 rppd w=%s l=%s m=%d b=0" % (t[0], t[1], t[2], RPPD_W, RPPD_L, RPPD_M))
            nsub += 1
            continue
        L.append(" ".join("0" if x == "vss" else x for x in t))
    if nsub != 2:
        raise SystemExit("gen_requests.py: expected exactly 2 ideal termination legs in "
                         "rx_term_pad.spice, found %d -- the netlist changed, revisit the "
                         "rppd substitution" % nsub)
    L += ["Vdd vdd 0 1.2",
          "Bvcm vcm 0 V=0.7917*v(vdd)",
          "Vip padp vcm dc 0 ac 0.5",
          "Vin padn vcm dc 0 ac -0.5",
          "Xc inp inn vcm vdd 0 kl klb kl klb kl klb op on ctle",
          "Bkl kl 0 V=v(vdd)-0.25",
          "Bklb klb 0 V=v(vdd)",
          "Clp op 0 80f", "Cln on 0 80f",
          "Hip iz 0 Vip 1"]
    return "\n".join(L) + "\n"


# RES corner -> the HBT/CAP/DIO corner it is ganged with (same typ/bcs/wcs
# index, mirroring the TX MOS benches and the spec's ganging proposal).
RES_GANG = (("res_typ", "hbt_typ", "cap_typ", "dio_tt"),
            ("res_bcs", "hbt_bcs", "cap_bcs", "dio_ff"),
            ("res_wcs", "hbt_wcs", "cap_wcs", "dio_ss"))


def res_axes(debug=False):
    """The 27-point grid with the RES corner as the named process axis."""
    gang = RES_GANG[:1] if debug else RES_GANG
    return {
        "process": [
            {"name": res, "sections": [
                {"lib": RES_LIB, "section": res},
                {"lib": HBT_LIB, "section": hbt},
                {"lib": CAP_LIB, "section": cap},
                {"lib": DIO_LIB, "section": dio},
            ]}
            for res, hbt, cap, dio in gang
        ],
        "temperature_c": [27] if debug else [-40, 27, 125],
        "supply_v": {"vdd": [1.2] if debug else [1.08, 1.2, 1.32]},
    }


def p11win_axes():
    """The two p.11 window members: typical ganged sections, nominal V and T,
    rsh_rppd overridden to the source-note window edges."""
    res, hbt, cap, dio = RES_GANG[0]
    return {
        "process": [
            {"name": "res_typ_p11win", "sections": [
                {"lib": RES_LIB, "section": res},
                {"lib": HBT_LIB, "section": hbt},
                {"lib": CAP_LIB, "section": cap},
                {"lib": DIO_LIB, "section": dio},
            ]}
        ],
        "temperature_c": [27],
        "params": {"rsh_rppd": [RSH_RPPD_P11_LO, RSH_RPPD_P11_HI]},
    }


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


# Regeneration decision levels, in volts of |q|. Two fixed absolute levels are
# measured at every corner; neither is swing-relative (a `.meas` card cannot
# reference an earlier `.meas` result -- ngspice rejects it with "Undefined
# parameter" and aborts the whole deck -- and `measurements[].expr` is not
# usable on the fleet runner, klayout-tools#4217. See sim/rx/README.md).
#
# DECISION_LEVEL_V is the level the link benches care about: the sampler
# decision threshold the downstream CMOS stage needs. It is NOT a fixed
# fraction of the swing -- peak |q| over this grid runs 0.148 V to 0.569 V, so
# 0.25 V is 96 % of peak |q| at the weakest corner that reaches it and 44 % at
# the strongest. At the six 1.080 V corners peak |q| never reaches it at all,
# which `on_unreached: "null"` records as `not_reached` rather than an error.
DECISION_LEVEL_V = 0.25
# FLOOR_LEVEL_V is a low fixed level every corner in the grid crosses, so a
# regeneration *speed* is returned even where the decision level is not
# reached. Chosen against the measured worst-case peak |q| in the 27-point grid
# (0.1482 V at hbt_wcs/1.080V/-40C, record 20261110-222737-506b37e), which
# leaves ~1.5x margin; validated at both grid extremes (hbt_wcs/1.080V/-40C and
# hbt_bcs/1.320V/125C) to cross after the trigger edge, inside the intended
# hold phase.
FLOOR_LEVEL_V = 0.10


def latch_meas():
    # Regeneration time: from the clock edge that closes the sample phase (ck
    # falling through 0) to |q| reaching a decision level. The hold pair
    # regenerates only during that phase. First-look limit for both levels: the
    # half period at 5 GHz (100 ps), after which the next sample phase opens.
    # Cycle selection is by td= (data toggles at 250 ps + 400 ps k).
    #
    # Two levels per edge, both plain `.meas` cards:
    #   *_up / *_dn      at DECISION_LEVEL_V, `on_unreached: "null"` so a
    #                    corner whose swing never reaches it is recorded as
    #                    `not_reached` (an explicit "does not regenerate to the
    #                    decision level" verdict) instead of erroring the corner.
    #   *_up_lo / *_dn_lo at FLOOR_LEVEL_V, which every corner crosses, so a
    #                    regeneration speed is always returned. This separates
    #                    "too slow" from "too weak": a corner that misses the
    #                    decision level but returns a fast floor-level time is
    #                    swing-limited, not speed-limited.
    m = [
        {"name": "latch_t_regen_up", "unit": "s",
         "spice": ".meas tran latch_t_regen_up trig v(ck) val=0 fall=1 td=2.35n targ v(q) val=%g rise=1 td=2.35n" % DECISION_LEVEL_V,
         "limits": {"max": 100e-12}, "on_unreached": "null"},
        {"name": "latch_t_regen_dn", "unit": "s",
         "spice": ".meas tran latch_t_regen_dn trig v(ck) val=0 fall=1 td=2.55n targ v(q) val=%g fall=1 td=2.55n" % -DECISION_LEVEL_V,
         "limits": {"max": 100e-12}, "on_unreached": "null"},
        {"name": "latch_t_regen_up_lo", "unit": "s",
         "spice": ".meas tran latch_t_regen_up_lo trig v(ck) val=0 fall=1 td=2.35n targ v(q) val=%g rise=1 td=2.35n" % FLOOR_LEVEL_V,
         "limits": {"max": 100e-12}},
        {"name": "latch_t_regen_dn_lo", "unit": "s",
         "spice": ".meas tran latch_t_regen_dn_lo trig v(ck) val=0 fall=1 td=2.55n targ v(q) val=%g fall=1 td=2.55n" % -FLOOR_LEVEL_V,
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
    rppd_files = {
        "pad_ac_rppd": (pad_rppd_body(), {"kind": "ac", "args": "lin 300 1e8 3e10"}, pad_meas(),
                        res_axes(debug)),
        "pad_ac_rppd_p11win": (pad_rppd_body(win=True), {"kind": "ac", "args": "lin 300 1e8 3e10"},
                               pad_meas(), p11win_axes()),
    }
    for name, (body, ana, meas) in files.items():
        write_bench(out, name, body, ana, meas, units)
    for name, (body, ana, meas, corners) in rppd_files.items():
        write_bench(out, name, body, ana, meas, corners,
                    extra_options={"osdi_preload": OSDI}, lib=RES_LIB)
    return 0


def write_bench(out, name, body, ana, meas, corners, extra_options=None, lib=HBT_LIB):
    rel = os.path.relpath(NET, out)
    with open(os.path.join(out, name + ".sp"), "w") as f:
        f.write(body.replace("../../design/rx/netlists", rel))
    req = request(name + ".sp", ana, meas, corners, extra_options, lib)
    with open(os.path.join(out, name + ".request.json"), "w") as f:
        json.dump(req, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
