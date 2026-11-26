#!/usr/bin/env python3
"""Generate the R4 swing-shortfall sweep benches and klt sim requests (issue #286).

SIZING EVIDENCE, not a spec result and not a measurement. Reuses the issue #21 TX
sizing bench (sim/tx/make_tb.py: same bias / predriver / driver_ffe cells, same
stimulus, same R18 pad stand-in of 4 ohm + 70.66 fF extracted pad C + PDK ESD
diodes, same fixed external 100 ohm differential load) and varies ONE thing per
candidate in the driver_ffe main stage, FFE off:

  dvb_<mV>   main-tail base bias offset: the XQTM base is driven from a bench node
             vbm = vbn + dvb instead of vbn (REM and everything else unchanged; the
             predriver and bias cell keep vbn). Raises/lowers the main tail current.
  rtk_<x100> symmetric back-termination: RT1 and RT2 length scaled by the same
             factor (1.00 = 50 ohm each at typical sheet R). The 100 ohm load, REM and
             the bias are unchanged.

The control (dvb 0, rtk 1.00) is the unmodified driver, so it reproduces the
tx_sizing_ffe0_wcs row. Instrumentation added on top of the issue #21 measurements:
  - tail_ic_main_a and tail_ie_main_a: XQTM collector and emitter currents, respectively,
    measured by series 0 V sources (positive into the collector and out of REM);
  - r4_prbs_*  settled pad swing sampled at the end of the longest run of ones / zeros
               in the PRBS-7 slice, and the pad swing extrema over the whole PRBS-7
               slice, so the static-preamble figure can be compared with the R4
               PRBS-7 method;
  - vce_min_drv_tail_main (already in the issue #21 set) is kept: tail headroom.
The R3 cards probe the same physical terminals for every candidate.

The corner block per request is one process pairing x 3 supplies x 3 temperatures.
The resistor sheet scale and the candidate parameters are baked into each deck (the
batch worker does not honour corners.params, see sim/tx/README.md).

Usage: python3 -I sim/tx/make_sweep_r4.py            (from the repo root)
Writes sim/tx/r4sweep_<cand>_<proc>.sp / .request.json and sim/tx/r4sweep_candidates.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_tb as tb  # noqa: E402

# (candidate id, main-tail bias offset in V, RT length scale)
CANDIDATES = [
    ("ctl", 0.0, 1.00),
    ("dvb_m40", -0.04, 1.00),
    ("dvb_p40", 0.04, 1.00),
    ("dvb_p80", 0.08, 1.00),
    ("dvb_p120", 0.12, 1.00),
    ("rtk_125", 0.0, 1.25),
    ("rtk_150", 0.0, 1.50),
    ("rtk_200", 0.0, 2.00),
    # combined bias + termination, added after the single-variable sweep (stage 2)
    ("c_p80_r200", 0.08, 2.00),
    ("c_p80_r300", 0.08, 3.00),
    ("c_p120_r300", 0.12, 3.00),
    # stage 3: push the termination further at +80 mV bias
    ("c_p80_r400", 0.08, 4.00),
    ("c_p80_r600", 0.08, 6.00),
]
RT_L = 114.3  # um, design/tx/netlists/driver_ffe.spice XRT1/XRT2

# PRBS-7 slice (bits >= 38): longest run of ones is bits 62..65 (ends 6.6 ns), longest
# run of zeros is bits 38..43 (ends 4.4 ns); sample 10 ps before the run's end.
PRBS_START = 3.9e-9
T_PRBS_HI = 6.59e-9
T_PRBS_LO = 4.39e-9
T_TAIL_A, T_TAIL_B = 0.9e-9, 1.35e-9  # tail current averaging window, inside the steady high


def candidate_deck(rscale, dvb, rtk):
    text = tb.deck(0, rscale)
    # driver_ffe edits: sense source in the main tail, separate tail base node, RT scale
    old_tail = "XQTM em vbn etm vss npn13G2 Nx=8"
    old_rem = "XREM etm vss vss rsil w=16u l=18.29u m=1 b=0"
    assert old_tail in text and old_rem in text
    text = text.replace(old_tail, "Vsc em ctm 0\n"
                        "XQTM ctm vbm etm vss npn13G2 Nx=8\n"
                        "Voffset vbm vbn {dvb}")
    text = text.replace(old_rem, "XREM etm etmx vss rsil w=16u l=18.29u m=1 b=0\n"
                        "Vse etmx vss 0")
    for leg in ("XRT1 vdd outp", "XRT2 vdd outn"):
        o = "%s vss rsil w=16u l=%gu m=1 b=0" % (leg, RT_L)
        assert o in text
        text = text.replace(o, "%s vss rsil w=16u l='%gu*rtk' m=1 b=0" % (leg, RT_L))
    # vbm is built inside the subckt from the vbn port; dvb and rtk are bench-level params
    text += ".param dvb=%g\n.param rtk=%g\n" % (dvb, rtk)
    return text


def meas_list():
    ms = tb.meas_json(0)
    # The baseline deck connects the base directly to vbn. Probe XQTM after the offset.
    for card in ms:
        if card["name"] == "vbe_rev_max_drv_tail_main":
            card["spice"] = ".meas tran vbe_rev_max_drv_tail_main max par('v(xdrv.etm)-v(xdrv.vbm)')"
    for name, source in (("tail_ic_main_a", "vsc"), ("tail_ie_main_a", "vse")):
        ms.append({"name": name, "unit": "A",
                   "spice": f".meas tran {name} avg par('i(v.xdrv.{source})') "
                            f"from={T_TAIL_A:g} to={T_TAIL_B:g}"})
    ms += [
        {"name": "r4_prbs_run_hi", "unit": "V",
         "spice": ".meas tran r4_prbs_run_hi find v(vd) at=%.4g" % T_PRBS_HI},
        {"name": "r4_prbs_run_lo", "unit": "V",
         "spice": ".meas tran r4_prbs_run_lo find v(vd) at=%.4g" % T_PRBS_LO},
        {"name": "r4_prbs_max_v", "unit": "V",
         "spice": ".meas tran r4_prbs_max_v max v(vd) from=%.4g to=%.4g" % (PRBS_START, tb.T_END)},
        {"name": "r4_prbs_min_v", "unit": "V",
         "spice": ".meas tran r4_prbs_min_v min v(vd) from=%.4g to=%.4g" % (PRBS_START, tb.T_END)},
        {"name": "vce_min_drv_pair_p", "unit": "V",
         "spice": ".meas tran vce_min_drv_pair_p min par('v(cop)-v(xdrv.em)')"},
        {"name": "vce_min_drv_pair_n", "unit": "V",
         "spice": ".meas tran vce_min_drv_pair_n min par('v(con)-v(xdrv.em)')"},
    ]
    return ms


def request(cand, proc):
    r = tb.request("ffe0_" + proc, 0, proc)
    r["netlist"] = "r4sweep_%s_%s.sp" % (cand, proc)
    r["measurements"] = meas_list()
    r["options"]["timeout_s"] = 120
    return r


if __name__ == "__main__":
    # args: <proc>... ; env R4_CANDS=a,b limits the candidates written (stage-2 reruns)
    procs = sys.argv[1:] or ["wcs"]
    only = [c for c in os.environ.get("R4_CANDS", "").split(",") if c]
    for cand, dvb, rtk in CANDIDATES:
        if only and cand not in only:
            continue
        for proc in procs:
            with open(os.path.join(HERE, "r4sweep_%s_%s.sp" % (cand, proc)), "w") as fh:
                fh.write(candidate_deck(tb.RSCALE[proc], dvb, rtk))
            with open(os.path.join(HERE, "r4sweep_%s_%s.request.json" % (cand, proc)), "w") as fh:
                json.dump(request(cand, proc), fh, indent=2)
                fh.write("\n")
    with open(os.path.join(HERE, "r4sweep_candidates.json"), "w") as fh:
        json.dump([{"id": c, "dvb_v": d, "rt_length_scale": k} for c, d, k in CANDIDATES], fh, indent=2)
        fh.write("\n")
