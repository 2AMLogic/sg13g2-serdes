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


LOCK_N = 40000
MARGIN_UI = 0.10      # record-defined margin threshold on the worst 1e-12 width (NOT a spec row; R15 only requires > 0)


def lock_words(arch, kw):
    """Words to lock from a 0.4 UI offset (link_bench r11 definition: 64-word mean within 0.05 UI to the end); 0/+300/-300 ppm."""
    out = []
    for ppm in (0, 300, -300):
        e = cm.run(LOCK_N, ppm=ppm, init_offset_ui=0.4, **kw, **arch) / cm.UI
        m = np.convolve(e, np.ones(64) / 64, mode="same")
        o = np.nonzero(np.abs(m[32:-32]) >= 0.05)[0]
        out.append(int(o[-1]) + 33 if len(o) else 0)
    return out


def arow(eye, n, label, arch=None, **kv):
    """DR-011 candidate row: dither, R15 width (27 corners), slips at +-300 (ratified R13) and +-500 ppm (stretch),
    slew proxy at the R12 mask's steepest point, lock time. `ok` = width > 0 in every corner, no slip at +-300 ppm and the
    15 UIpp / 100 kHz peak error within half the no-CDR-jitter eye width (r12's rule; a PROXY for the full mask, which
    link_bench r12 grades), and lock within r11's limit (< 20000 words) at 0 / +300 / -300 ppm.
    'pass+margin' additionally has worst width >= MARGIN_UI."""
    arch = arch or {}
    c = dict(BASE, **kv)
    kw = dict(kp=c["kp"], ki=c["ki"], analog_delay=c["ad"], vote_noise_ui=c["vn"])
    e = cm.run(n, **kw, **arch)[n // 2:] / cm.UI
    rms, pk = float(np.std(e)), float(np.max(np.abs(e)))
    sl = {ppm: cm.slips(cm.run(n // 2 + 20000, ppm=ppm, **kw, **arch), 20000) for ppm in (300, -300, 500, -500)}
    sj = float(np.max(np.abs(cm.run(30000, sj_uipp=15.0, sj_hz=1e5, **kw, **arch)[10000:])) / cm.UI)
    w, fail, _ = eye.width(rms, c["rj"], c["dj"], c["sn"], c["so"])
    nc = len(eye.pm)
    w0, _, _ = eye.width(0.0, c["rj"], c["dj"], c["sn"], c["so"])        # eye without CDR jitter: the r12 bench's grading eye
    lk = lock_words(arch, kw)
    ok = (w is not None and w > 0 and not fail and sl[300] == 0 and sl[-300] == 0 and w0 is not None and sj <= w0 / 2
          and max(lk) < LOCK_N // 2)
    ws = f"{w:+.3f}" if w is not None else "  n/a "
    print(f"{label:46s} {rms:6.4f} {pk:6.4f} {ws:>7s} {nc - fail:2d}/{nc} {sl[300]:5d}/{sl[-300]:<5d} {sl[500]:5d}/{sl[-500]:<5d}"
          f" {sj:6.3f}  {lk[0]:5d}/{lk[1]:5d}/{lk[2]:5d}  {('pass+margin' if w >= MARGIN_UI else 'pass') if ok else 'FAIL'}")
    return ok, w


def ahead(title):
    print(f"\n{title}")
    print(f"{'candidate / input changed':46s} {'rms':>6s} {'pk':>6s} {'worst w':>7s} extrap  slips+-300   slips+-500   pk@mask  lock 0/+300/-300  verdict")


def head(title):
    print(f"\n{title}")
    print(f"{'row (one input changed)':34s} {'rms UI':>7s} {'pk UI':>7s}   {'worst w@1e-12':>13s}  extrap  worst floor   slips +300/-300 ppm  pk@15UIpp,100k")


DR009 = dict(kp=8, ki=0)
A2 = dict(kp=8, ki=1)                                    # recommended: centre of the passing region (E2)
ARCH2 = dict(frac=6, decim=16, fmax=1023)


MASK_PTS = {1e5: 15.0, 3e5: 5.0, 1e6: 1.5, 3e6: 0.5, 1e7: 0.15}     # link_bench.mask() amplitudes


def sj_slip_free_bound(f, arch, kw):
    """Largest SJ amplitude (UIpp) at f with peak recovered-clock error < 0.5 UI (bisection, 13 steps, 0.05..40 UIpp)."""
    n = int(min(40000, max(15000, 4 / (f * cm.WORD_S))))

    def peak(a):
        return float(np.max(np.abs(cm.run(n, sj_uipp=a, sj_hz=f, **kw, **arch)[n // 3:])) / cm.UI)
    lo, hi = 0.05, 40.0
    if peak(hi) < 0.5:
        return hi
    for _ in range(13):
        mid = (lo * hi) ** 0.5
        lo, hi = (mid, hi) if peak(mid) < 0.5 else (lo, mid)
    return lo


def slew_row(label, arch, kw):
    b = [sj_slip_free_bound(f, arch, kw) for f in MASK_PTS]
    print(f"{label:34s} " + "  ".join(f"{x:6.2f} ({x / m:4.2f}x)" for x, m in zip(b, MASK_PTS.values())) + f"   min {min(x / m for x, m in zip(b, MASK_PTS.values())):.2f}x")


def arch_section(eye, n, quick):
    """DR-011: loop architectures on the unchanged benches. Every arch flag is a MODEL option; rtl/ is untouched."""
    print("\n== DR-011 loop architecture comparison ==  (simulated / extrapolated, nothing measured)")
    print("PI step 1/64 UI (pi_code), vote = sum of the word's PD decisions unless stated, delay 7 digital + 1 analog, "
          "frac = integral accumulator fractional bits, decim = integral update every N words.")
    ahead("E1. candidates (baseline inputs)")
    arow(eye, n, "RTL KP=16 KI=1 (baseline)")
    arow(eye, n, "DR-009 KP=8 KI=0", **DR009)
    arow(eye, n, "2nd-order KP=8 KI=1 frac6 decim16 (recommended)", arch=ARCH2, **A2)
    arow(eye, n, "2nd-order, decim 1 (integral every word)", arch=dict(ARCH2, decim=1), **A2)
    arow(eye, n, "2nd-order, decim 64", arch=dict(ARCH2, decim=64), **A2)
    arow(eye, n, "KP=8 KI=1 frac0 decim16 (no fractional bits)", arch=dict(ARCH2, frac=0), **A2)
    arow(eye, n, "RTL gain, digital delay 3 (shorter latency)", arch=dict(digital_delay=3))
    arow(eye, n, "KP=16 KI=0, digital delay 3", arch=dict(digital_delay=3), kp=16, ki=0)
    arow(eye, n, "2nd-order, digital delay 4", arch=dict(ARCH2, digital_delay=4), **A2)
    for kp in (8, 16):
        arow(eye, n, f"sign vote KP={kp} KI=0", arch=dict(vote="sign"), kp=kp, ki=0)
    arow(eye, n, "sign vote KP=16 KI=1 frac6 decim16", arch=dict(ARCH2, vote="sign"), kp=16, ki=1)
    arow(eye, n, "KP=8 KI=0, PI step 1/256 UI", arch=dict(pi_shift=5), **DR009)
    arow(eye, n, "2nd-order, PI step 1/256 UI", arch=dict(ARCH2, pi_shift=5), **A2)
    arow(eye, n, "2nd-order + gear 24,2,2000", arch=dict(ARCH2, gear=(24, 2, 2000)), **A2)
    ahead("E2. passing region of the 2nd-order loop: KP x integral fractional bits (KI=1, decim16)")
    ok_pts = []
    for kp in ((6, 8, 12) if quick else (5, 6, 7, 8, 9, 10, 12, 16)):
        for fr in ((6,) if quick else (3, 4, 6, 8, 10, 12)):
            ok, _ = arow(eye, n, f"KP={kp} KI=1 frac{fr} decim16", arch=dict(ARCH2, frac=fr), kp=kp, ki=1)
            ok_pts.append((kp, fr, ok))
    print("passing points (KP, frac): " + ", ".join(f"({a},{b})" for a, b, o in ok_pts if o))
    print("\nE4. slew margin: largest SJ amplitude with no slip (peak error < 0.5 UI), UIpp (ratio to the R12 mask amplitude)")
    print(f"{'loop':34s} " + "  ".join(f"{f / 1e6:g} MHz".rjust(14) for f in MASK_PTS))
    slew_row("DR-009 KP=8 KI=0", {}, DR009)
    for kp in ((6, 8) if quick else (5, 6, 7, 8, 9, 10, 12)):
        slew_row(f"2nd-order KP={kp} KI=1 frac6 d16", ARCH2, dict(kp=kp, ki=1))
    ahead("E3. unfitted inputs, DR-009 setting vs the 2nd-order loop (same ranges as section A)")
    for tag, arch, kv in (("DR-009", {}, DR009), ("2nd-order KP8", ARCH2, A2)):
        for lab, extra in (("baseline", {}), ("PD noise 0.0", dict(vn=0.0)), ("PD noise 0.01", dict(vn=0.01)),
                           ("PD noise 0.03", dict(vn=0.03)), ("PD noise 0.05", dict(vn=0.05)),
                           ("analog delay 0", dict(ad=0)), ("analog delay 2", dict(ad=2)), ("analog delay 3", dict(ad=3)),
                           ("analog delay 5", dict(ad=5)),
                           ("RJ 0.008 (grid floor), DJ 0", dict(rj=0.008, dj=0.0)), ("sampler noise 1 mV", dict(sn=1.0)),
                           ("sampler noise 4 mV", dict(sn=4.0)), ("sampler offset 5 mV", dict(so=5.0)),
                           ("sampler offset 10 mV", dict(so=10.0))):
            arow(eye, n, f"{tag}: {lab}", arch=arch, **dict(kv, **extra))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="8 PVT-edge corners, short runs")
    ap.add_argument("--section", default="all", choices=("attribution", "loop", "delay", "arch", "all"))
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
    if args.section in ("arch", "all"):
        arch_section(eye, n, args.quick)
    print("\nNo result above is measured; the varied inputs need transistor-level records (sampler, PI, "
          "deserialiser) that do not exist yet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
