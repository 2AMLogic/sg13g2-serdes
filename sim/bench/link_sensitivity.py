#!/usr/bin/env python3
"""One-factor-at-a-time sensitivity of the R12/R15 closure to the CDR's unfitted inputs (issue #102).

    python3 -I sim/bench/link_sensitivity.py [--quick] [--section attribution|loop|all]

Reuses the existing model (cdrmodel.run on the RTL CdrFilter, linkcore eye); no second CDR model.
Each row changes ONE input from the baseline (RTL KP/KI, delay 7+1, PD noise 0.02 UI, sampler 2 mV / 5 mV,
RJ 0.02 UI, DJ 0.0625 UIpp) and reports the CDR error (rms/peak, 0 ppm, locked), the worst 1e-12 eye width
over the 27 HBT PVT-full corners (CDR rms added as RJ, as R15 does) and R13 slips at +-300 ppm.
Every figure is simulated (behavioural) / extrapolated (dual-Dirac wall fit). Nothing is measured. All the
varied inputs are UNFITTED ASSUMPTIONS: no transistor-level record exists for them.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import cdrmodel as cm  # noqa: E402
import linkcore as lc  # noqa: E402

A = lc.ASSUMPTIONS
BASE = dict(kp=None, ki=None, ad=None, vn=A["rj_ui"], rj=A["rj_ui"], dj=A["dj_uipp"],
            sn=A["sigma_noise_mv"], so=0.0)
CTLE_CODE, SWING_MVPPD = 7, 500.0


class Eye:
    """Per-corner ISI pmfs, computed once."""

    def __init__(self, quick):
        fits, self.rec = lc.ctle_fits()
        ids = lc.edge_corners(fits) if quick else list(fits)
        self.pm = {}
        for cid in ids:
            p, c0 = lc.pulse_response("CH-A", 10.0, np.array(fits[cid][CTLE_CODE]))
            self.pm[cid] = lc.isi_pmfs(p, c0)

    def width(self, cdr_rms, rj, dj, sn_mv, offset_mv):
        """(worst width UI or None, #failed extrapolations, best floor BER)."""
        ker = lc.jitter_kernel(float(np.hypot(rj, cdr_rms)), dj)
        worst, fail, floor = None, 0, 0.0
        for pm in self.pm.values():
            ber = lc.bathtub(pm, SWING_MVPPD / 2e3, sn_mv / 1e3, offset_mv / 1e3, ker)
            order = np.roll(np.arange(lc.M), lc.M // 2 - int(np.argmin(ber)))
            tau = (np.arange(lc.M) - lc.M // 2) / lc.M
            ext = lc.wall_extrapolate(tau, ber[order])
            floor = max(floor, ext["floor"])
            if ext["ok"]:
                worst = ext["width"] if worst is None else min(worst, ext["width"])
            else:
                fail += 1
        return worst, fail, floor


def row(eye, n, label, **kv):
    c = dict(BASE, **kv)
    kw = dict(kp=c["kp"], ki=c["ki"], analog_delay=c["ad"], vote_noise_ui=c["vn"])
    e = cm.run(n, **kw)[n // 2:] / cm.UI
    rms, pk = float(np.std(e)), float(np.max(np.abs(e)))
    sl = {}
    for ppm in (300, -300):
        r = cm.run(n // 2 + 20000, ppm=ppm, **kw)
        sl[ppm] = cm.slips(r, 20000)
    # slew margin: peak error with the R12 mask amplitude at 100 kHz (15 UIpp), the steepest point of the mask
    sj = float(np.max(np.abs(cm.run(30000, sj_uipp=15.0, sj_hz=1e5, **kw)[10000:])) / cm.UI)
    w, fail, floor = eye.width(rms, c["rj"], c["dj"], c["sn"], c["so"])
    ws = f"{w:+.3f}" if w is not None else "  n/a "
    nc = len(eye.pm)
    print(f"{label:34s} {rms:7.4f} {pk:7.4f}   {ws:>7s} UI  {nc - fail:2d}/{nc}  {floor:8.1e}   {sl[300]:3d}/{sl[-300]:3d}   {sj:7.3f}")
    return rms, pk, w, fail


def head(title):
    print(f"\n{title}")
    print(f"{'row (one input changed)':34s} {'rms UI':>7s} {'pk UI':>7s}   {'worst w@1e-12':>13s}  extrap  worst floor   slips +300/-300 ppm  pk@15UIpp,100k")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="8 PVT-edge corners, short runs")
    ap.add_argument("--section", default="all", choices=("attribution", "loop", "delay", "all"))
    args = ap.parse_args(argv)
    n = 16000 if args.quick else 40000
    eye = Eye(args.quick)
    p, d = lc.rtl_loop_params(), lc.dr007_delays()
    print("== CDR dither closure attribution (issue #102) ==  (nothing below is measured)")
    print(f"fit record : sim/rx/records/{eye.rec}/ctle_ac.report.json; {len(eye.pm)} corners; CH-A @ 10 Gb/s, "
          f"{SWING_MVPPD:g} mVppd, CTLE code {CTLE_CODE}")
    print(f"baseline   : KP={p['KP']} KI={p['KI']} delay {d['digital']} digital + {d['analog_assumed']} analog; "
          f"PD noise {A['rj_ui']} UI, sampler {A['sigma_noise_mv']} mV rms (offset 0), RJ {A['rj_ui']} UI, DJ {A['dj_uipp']} UIpp")
    print("ALL VARIED INPUTS ARE UNFITTED ASSUMPTIONS (no record). labels: CDR rms/peak/slips = simulated "
          "(behavioural bang-bang); width = extrapolated (dual-Dirac Q-scale wall fit) over " + lc.label_fit(eye.rec))
    if args.section in ("attribution", "all"):
        head("A. one unfitted input at a time (RTL loop)")
        row(eye, n, "baseline")
        for v in (0.0, 0.01, 0.03, 0.05):
            row(eye, n, f"PD decision noise {v} UI", vn=v)
        for a in (0, 2, 3):
            row(eye, n, f"analog delay {a} words", ad=a)
        row(eye, n, "RJ 0, DJ 0 (eye side)", rj=0.005, dj=0.0)
        row(eye, n, "sampler noise 1 mV", sn=1.0)
        row(eye, n, "sampler noise 4 mV", sn=4.0)
        row(eye, n, "sampler offset 5 mV (1 sigma)", so=5.0)
        row(eye, n, "sampler offset 10 mV", so=10.0)
    if args.section in ("loop", "all"):
        head("B. loop gain sweep (KP, KI) at baseline noise/delay")
        for ki in (1, 0):
            for kp in (4, 6, 8, 9, 10, 11, 12, 16, 24, 32):
                row(eye, n, f"KP={kp} KI={ki}", kp=kp, ki=ki)
        head("C. candidate loop gains vs the unfitted inputs (KI=0)")
        for kp in (8, 10):
            for v in (0.0, 0.03, 0.05):
                row(eye, n, f"KP={kp} KI=0, PD noise {v} UI", kp=kp, ki=0, vn=v)
            for a in (0, 2, 3):
                row(eye, n, f"KP={kp} KI=0, analog delay {a}", kp=kp, ki=0, ad=a)
    if args.section in ("delay", "all"):
        head("D. DR-007 delay budget re-checked in THIS model (digital 7 + analog a; L = 7 + a)")
        for a in range(0, 8):
            row(eye, n, f"RTL KP=16 KI=1, L={7 + a}", ad=a)
        for a in range(0, 8):
            row(eye, n, f"KP=8 KI=0, L={7 + a}", kp=8, ki=0, ad=a)
    print("\nNo result above is measured; the varied inputs need transistor-level records (sampler, PI, "
          "deserialiser) that do not exist yet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
