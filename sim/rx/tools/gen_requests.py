#!/usr/bin/env python3
"""Generate the sim/rx bench bodies and `klt sim` request files.

    python3 -I sim/rx/tools/gen_requests.py            # write sim/rx/*.sp, *.request.json
    python3 -I sim/rx/tools/gen_requests.py --debug OUTDIR
        # one-unit (typ, 27 C, 1.2 V) variants of every request for a quick
        # local check; never the grid, never a recorded result

Node-stress measurements are derived from the exported netlists in
design/rx/netlists/, so they follow the schematics: max collector voltage,
max Vce (against BVCEO 1.4 V, issue #242) and max reverse Vbe of every HBT.
Everything measured here is sizing evidence, not a spec result.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SIM = os.path.join(HERE, "..")
NET = os.path.join(SIM, "..", "..", "design", "rx", "netlists")

sys.path.insert(0, os.path.join(SIM, "..", "tools"))
from hbt_corners import HBT_LIB, corner_axes  # noqa: E402

VC_MAX = 1.32   # DR-003: no HBT collector node above this
VCE_MAX = 1.4   # DR-003: npn13G2 open-base BVCEO (target-spec HBT breakdown table), hard limit (issues #242, #256)
VBE_REV = 1.0   # DR-003: no reverse Vbe above this

# Differential input amplitudes of the ctle_tran bench (issue #256), as the
# single-ended half-swing A of each source about vcm: each side swings +-A, so
# the differential peak-to-peak swing is 4*A (mVppd). The spec declares no
# MAXIMUM RX input swing -- R8 gives only the minimum sensitivity -- so both
# levels are bench bounds named here and restated in the record, not spec
# limits:
# - lo: 50 mVppd -- R8 nominal RX input sensitivity (spec/target-spec.md R8),
#   the smallest swing the RX must resolve, so the stress floor.
# - hi: 800 mVppd -- R4 stretch TX output swing (the R4 maximum), taken as the
#   pad amplitude at zero channel loss: the committed channel model
#   (spec/channel/) has S11 = S22 = 0 and IL(f) -> 0 dB as f -> 0, so the
#   largest pad amplitude it admits is the TX swing itself.
CTLE_TRAN_SENS_V = 0.0125
CTLE_TRAN_MAX_V = 0.2


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


def stress_meas(inst, cell, portmap, prefix, kind, vce=True, vce_first=False):
    """`.meas` cards for max collector V, max Vce and max reverse Vbe of every HBT.

    kind "dc": operating-point value via a two-point dummy sweep (`at=0`);
    kind "tran": maximum over the run. Plain `spice` cards, because the fleet
    runner's `expr` support is not usable (see sim/rx/README.md). Unless
    `vce=False`, a third card per HBT, max Vce (DR-003/BVCEO), through another
    B source (issues #242, #256). `vce_first` only orders that card before
    `_vbe_rev_max`, as the ctle_tran request has it.
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
        cards = [("_vc_max", "v(%s)" % node(c), VC_MAX)]
        if vce:
            vce_node = base + "_vce_node"
            lines.append("B%s %s 0 V=v(%s)-v(%s)" % (vce_node, vce_node, node(c), node(e)))
            vce_card = ("_vce_max", "v(%s)" % vce_node, VCE_MAX)
            vbe_card = ("_vbe_rev_max", "v(%s)" % vbe, VBE_REV)
            # Card order is kept per bench so every already-committed request
            # (and the record generated from it) stays byte-identical:
            # ctle_tran (issue #256) lists vce before vbe_rev, the others after.
            cards += [vce_card, vbe_card] if vce_first else [vbe_card, vce_card]
        else:
            cards.append(("_vbe_rev_max", "v(%s)" % vbe, VBE_REV))
        for suffix, sig, lim in cards:
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


def _tran_pwl(amp, sign):
    """PWL text for one source of the ctle_tran bench: +-`amp` about vcm,
    `sign` = +1 for the p side, -1 for the n side (the pair is complementary).
    Both polarities of the long run are exercised, so every device of the
    symmetric pair sees its settled worst-case collector level:
      0-2 ns      settled at -amp (the .op state)
      2-3 ns      5 cycles of 5 GHz alternation (200 ps, 20 ps edges), first
                  edge -amp -> +amp
      3-6 ns      held at +amp (3 ns > 8*tau of the 300 ps Rca*Cca feed-forward,
                  so hpp/hpn settle back to vcm)
      6-7 ns      5 cycles of 5 GHz alternation, first edge +amp -> -amp
      7-7.1 ns    held at +amp
    """
    E, P = 20e-12, 200e-12   # edge time, period
    pts = [(0.0, -amp)]

    def alt(t0, lvl):
        for i in range(5):
            t = t0 + i * P
            pts.extend([(t, lvl), (t + E, -lvl), (t + P / 2, -lvl), (t + P / 2 + E, lvl)])
        return t0 + 5 * P

    t = alt(2e-9, -amp)            # ends at -amp
    pts.extend([(t, -amp), (t + E, amp)])   # then held at +amp until alt() at 6 ns
    alt(6e-9, amp)                 # ends at +amp
    pts.append((7.1e-9, amp))
    return "pwl(" + " ".join("%.4gn %g" % (a * 1e9, sign * b) for a, b in pts) + ")"


def ctle_tran_body(extra=()):
    """16 copies of ctle (codes 0-7 at each of two differential input levels)
    driven by ideal differential PWL sources that exercise BOTH polarities of
    the settled long run (see _tran_pwl): the ctle input network is a
    symmetric pair with AC-coupled feed-forward paths, so a single-polarity
    long run under-stresses one half of it."""
    L = ["* CTLE transient node-stress bench (issue #256): ctle_op's stress cards",
         "* are quiescent (Vip/Vin at dc 0); this bench drives a real differential",
         "* swing so the R3 per-device table gets transient peaks. 16 copies of",
         "* ctle: codes 0-7 at each of two input levels (lo/hi below), same ideal",
         "* source, same placeholder 80 fF load as ctle_ac/ctle_op. Stimulus per",
         "* side (pwl, both polarities): 2 ns settled, 1 ns of 5 GHz alternation",
         "* (200 ps period, 20 ps edges), a 3 ns long run at the opposite polarity,",
         "* then 1 ns of 5 GHz alternation again. Sizing evidence, not a spec",
         "* result.",
         ".include ../../design/rx/netlists/ctle.spice",
         "Vdd vdd 0 1.2",
         "Bvcm vcm 0 V=0.7917*v(vdd)",
         "Vip inp vcm " + _tran_pwl(CTLE_TRAN_SENS_V, +1),
         "Vin inn vcm " + _tran_pwl(CTLE_TRAN_SENS_V, -1),
         "Vjp jnp vcm " + _tran_pwl(CTLE_TRAN_MAX_V, +1),
         "Vjn jnn vcm " + _tran_pwl(CTLE_TRAN_MAX_V, -1)]
    _ctle_copies(L, "l", "inp", "inn")
    _ctle_copies(L, "h", "jnp", "jnn")
    L += list(extra)
    return "\n".join(L) + "\n"


def _ctle_copies(L, tag, inp, inn):
    """Append the 8 peaking-code copies of ctle for one input source pair,
    with node names prefixed `tag` so the two amplitude levels of ctle_tran
    (and the ac/op benches) never collide."""
    for c in range(8):
        for k in range(3):
            bit = (c >> k) & 1
            hi, lo = "v(vdd)", "v(vdd)-0.25"
            L.append("Bk%s%d_%d %s%dk%d 0 V=%s" % (tag, c, k, tag, c, k, hi if bit else lo))
            L.append("Bk%s%d_%db %s%dk%db 0 V=%s" % (tag, c, k, tag, c, k, lo if bit else hi))
        L.append("Xd%s%d %s %s vcm vdd 0 %s%dk0 %s%dk0b %s%dk1 %s%dk1b %s%dk2 %s%dk2b op%s%d on%s%d ctle"
                 % (tag, c, inp, inn, tag, c, tag, c, tag, c, tag, c, tag, c, tag, c, tag, c, tag, c))
        L.append("Clp%s%d op%s%d 0 80f" % (tag, c, tag, c))
        L.append("Cln%s%d on%s%d 0 80f" % (tag, c, tag, c))
        L.append("Bd%s%d dif%s%d 0 V=v(op%s%d)-v(on%s%d)" % (tag, c, tag, c, tag, c, tag, c))


def ctle_tran_meas():
    """Stress cards (with Vce) per HBT per code per level, plus the
    differential output max/min per copy as nonzero-swing evidence."""
    lines, m = [], []
    for lvl, tag, inp, inn in (("lo", "l", "inp", "inn"), ("hi", "h", "jnp", "jnn")):
        for c in range(8):
            pm = {"inp": inp, "inn": inn, "vcm": "vcm", "vdd": "vdd",
                  "outp": "op%s%d" % (tag, c), "outn": "on%s%d" % (tag, c)}
            for k in range(3):
                pm["c%d" % k] = "%s%dk%d" % (tag, c, k)
                pm["c%db" % k] = "%s%dk%db" % (tag, c, k)
            l_, m_ = stress_meas("Xd%s%d" % (tag, c), "ctle", pm, "ctle_%s_c%d" % (lvl, c), "tran", vce_first=True)
            lines += l_
            m += m_
            for ext, fn in (("_dif_max_v", "max"), ("_dif_min_v", "min")):
                n = "ctle_%s_c%d%s" % (lvl, c, ext)
                m.append({"name": n, "unit": "V",
                          "spice": ".meas tran %s %s v(dif%s%d)" % (n, fn, tag, c)})
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
    tran_lines, tran_meas = ctle_tran_meas()
    lat_lines, lat_meas = latch_meas()
    files = {
        "ctle_ac": (ctle_body(), {"kind": "ac", "args": "lin 300 1e8 3e10"}, ctle_ac_meas()),
        "ctle_op": (ctle_op_body(op_lines), {"kind": "dc", "args": "Vdmy 0 1m 1m"}, op_meas),
        "ctle_tran": (ctle_tran_body(tran_lines), {"kind": "tran", "args": "2p 7.1n"}, tran_meas),
        "pad_ac": (pad_body(), {"kind": "ac", "args": "lin 300 1e8 3e10"}, pad_meas()),
        "latch_regen": (latch_body(lat_lines), {"kind": "tran", "args": "2p 3n"}, lat_meas),
    }
    # 16 CTLE copies at 7.1 ns is a much larger transient deck than
    # latch_regen; give it a longer per-unit timeout than the default 120 s.
    timeouts = {"ctle_tran": {"timeout_s": 1800}}
    for name, (body, ana, meas) in files.items():
        rel = os.path.relpath(NET, out)
        with open(os.path.join(out, name + ".sp"), "w") as f:
            f.write(body.replace("../../design/rx/netlists", rel))
        req = request(name + ".sp", ana, meas, units, timeouts.get(name))
        with open(os.path.join(out, name + ".request.json"), "w") as f:
            json.dump(req, f, indent=2)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
