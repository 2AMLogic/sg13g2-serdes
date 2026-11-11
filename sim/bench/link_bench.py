#!/usr/bin/env python3
"""Behavioural link benches for spec rows R8, R11, R12, R13, R15 (issue #93, DR-002 chain).

    python3 -I sim/bench/link_bench.py r8|r11|r12|r13|r15 [--quick] [--corners full|edge|<corner id>]
                                       [--channel CH-A|CH-B] [--rate 10] [--swing-mvppd 500] [--ctle-code 7]

Every figure is labelled per DR-002: `simulated (behavioural, fitted to <record>)` or
`extrapolated (<method>, <fit range>)`. Nothing is measured. A model input with no
transistor-level record is printed as an UNFITTED ASSUMPTION, never as a result.
Exit 0 whenever the bench ran (the cold start must complete; the verdict is in the output). With --strict:
3 when a proposed-spec threshold is not met (reported, never relaxed).
The benches run locally in one process (numpy only); multi-corner TRANSISTOR-LEVEL inputs
come from the records under sim/rx/records, produced through `klt sim --wait-for-capacity 600`.
"""
import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import cdrmodel as cm  # noqa: E402
import linkcore as lc  # noqa: E402

A = lc.ASSUMPTIONS


def header(row, args, fits, rec_id):
    p, d = lc.rtl_loop_params(), lc.dr007_delays()
    print(f"== {row}: {args.title} ==  (nothing below is measured)")
    print(f"fit record : sim/rx/records/{rec_id}/ctle_ac.report.json ({len(fits)} corners; latch record "
          f"carries q swing only - no sampler offset/noise statistics)")
    print(f"link       : {args.channel} @ {args.rate:g} Gb/s, pad swing {args.swing_mvppd:g} mVppd, "
          f"CTLE code {args.ctle_code}, PRBS-31 treated as independent symbols over +-{lc.KCUR} cursors")
    print(f"CDR loop   : KP={p['KP']} KI={p['KI']} FMAX={p['FMAX']} from rtl/serdes_cdr_filter.v via "
          f"rtl/tests/serdes_ref.CdrFilter; delay {d['digital']} digital (DR-007, cited) + "
          f"{d['analog_assumed']} analog (UNFITTED ASSUMPTION, DR-007)")
    print("UNFITTED ASSUMPTIONS (no transistor-level record): "
          f"sampler noise {A['sigma_noise_mv']} mV rms, sampler offset {A['sigma_offset_mv']} mV 1-sigma, "
          f"RJ {A['rj_ui']} UI rms, DJ {A['dj_uipp']} UIpp, PD decision noise {args.vote_noise_ui} UI rms, "
          f"CTLE >5 GHz roll-off, TX FFE off")


def pick_corners(args, fits):
    if args.corners == "full":
        return list(fits)
    if args.corners == "edge":
        return lc.edge_corners(fits)
    if args.corners in fits:
        return [args.corners]
    sys.exit(f"link_bench: unknown corner '{args.corners}'")


def corner_pmfs(args, fits, cid):
    p, c0 = lc.pulse_response(args.channel, args.rate, np.array(fits[cid][args.ctle_code]))
    return lc.isi_pmfs(p, c0)


def eye(args, pmfs, offset_v=0.0, extra_rj=0.0):
    """Bathtub at the pad swing; returns (ber array, extrapolation dict)."""
    rj = float(np.hypot(A["rj_ui"], extra_rj))
    ker = lc.jitter_kernel(rj, A["dj_uipp"])
    amp = args.swing_mvppd / 2e3
    ber = lc.bathtub(pmfs, amp, A["sigma_noise_mv"] / 1e3, offset_v, ker)
    order = np.roll(np.arange(lc.M), lc.M // 2 - int(np.argmin(ber)))        # centre the best phase
    tau = (np.arange(lc.M) - lc.M // 2) / lc.M
    ext = lc.wall_extrapolate(tau, ber[order])
    return ber, ext


# ---- R15 ---------------------------------------------------------------------------------
def r15(args, fits, rec_id):
    print("\nCDR recovered-clock jitter feeds the eye (DR-002 step d): PRBS-31, 0 ppm, locked")
    n = 20000 if args.quick else 60000
    e = cm.run(n, vote_noise_ui=args.vote_noise_ui)[n // 2:] / cm.UI
    s_cdr = float(np.std(e))
    print(f"  recovered-clock error: rms {s_cdr:.4f} UI, peak {np.max(np.abs(e)):.4f} UI "
          f"[simulated (behavioural bang-bang, loop per above; vote noise UNFITTED)]")
    print("\ncorner                 floor BER   width@1e-12 (extrap.)  fit resid  direct BER@best  w/o CDR jitter  label")
    worst, fail = None, 0
    for cid in pick_corners(args, fits):
        pm = corner_pmfs(args, fits, cid)
        ber, ext = eye(args, pm, extra_rj=s_cdr)
        direct = float(ber.min())
        _, e0 = eye(args, pm)
        w0 = f"{e0['width']:+.3f} UI" if e0["ok"] else "n/a (floor %.1e)" % e0["floor"]
        if ext["ok"]:
            w = f"{ext['width']:+.3f} UI"
            lab = f"extrapolated (dual-Dirac Q-scale wall fit, {ext['fit_range']}) over " + lc.label_fit(rec_id)
            worst = ext["width"] if worst is None else min(worst, ext["width"])
            res = f"{ext['residual']:.3f}"
        else:
            w, res, lab = "FAILED", "-", f"extrapolation failed: {ext['reason']}"
            fail += 1
        print(f"{cid:22s} {ext['floor']:.2e}   {w:>12s}            {res:>6s}     {direct:.2e}        {w0:>14s}  {lab}")
    print(f"\nworst eye width at BER 1e-12: {'n/a' if worst is None else f'{worst:+.3f} UI'}; "
          f"extrapolation failures: {fail}")
    print("BER figures are simulated/extrapolated, not measured. Fit validation on held-out corners "
          "(DR-002 step 3) is NOT done: there is no transistor-level link-level result to validate against.")
    return 0 if (worst is not None and worst > 0 and not fail) else 3


# ---- R8 ----------------------------------------------------------------------------------
def r8(args, fits, rec_id):
    rng = np.random.default_rng(7)
    ndraw = 6 if args.quick else 16
    offs = np.abs(rng.normal(0.0, A["sigma_offset_mv"] / 1e3, ndraw))
    amps_mv = np.geomspace(3.0, 600.0, 40)
    sig = A["sigma_noise_mv"] / 1e3
    ker = lc.jitter_kernel(A["rj_ui"], A["dj_uipp"])
    print(f"\nMonte Carlo on the sampler: {ndraw} offset draws N(0,{A['sigma_offset_mv']} mV) [UNFITTED]; "
          f"amplitude = settled differential swing at the pad (channel DC gain 0 dB), mVppd")
    print("corner                 worst-draw sens. (extrap.)   median   direct@worst   label")
    allworst, fails = [], 0
    for cid in pick_corners(args, fits):
        pm = corner_pmfs(args, fits, cid)
        base = lc.bathtub(pm, 0.05, sig, 0.0, ker)
        mb = int(np.argmin(base))
        shifts = sorted(ker)
        need = {s: pm[(mb + s) % lc.M] for s in shifts}
        sens, direct = [], []
        for off in offs:
            bers = []
            for a in amps_mv:
                v = 0.0
                for s in shifts:
                    v += ker[s] * lc.ber_phase(need[s], a / 2e3, sig, off)
                bers.append(v)
            x, why, _ = lc.amp_extrapolate(amps_mv, bers)
            if x is None:
                fails += 1
                sens.append(np.nan)
            else:
                sens.append(x)
            lb = np.log10(np.maximum(bers, 1e-300))
            direct.append(float(np.interp(-12, lb[::-1], amps_mv[::-1])) if lb.min() < -12 < lb.max() else np.nan)
        ok = [s for s in sens if not np.isnan(s)]
        if not ok:
            print(f"{cid:22s} EXTRAPOLATION FAILED for all draws ({why})")
            allworst.append(np.nan)
            continue
        w = max(ok)
        allworst.append(w)
        dw = direct[int(np.nanargmax(sens))]
        print(f"{cid:22s} {w:10.1f} mVppd              {np.median(ok):7.1f}  {dw:9.1f}      "
              f"extrapolated (dual-Dirac Q-scale amplitude fit, BER 1e-9..1e-4) over " + lc.label_fit(rec_id))
    good = [w for w in allworst if not np.isnan(w)]
    worst = max(good) if good else float("nan")
    print(f"\nworst sensitivity over {len(allworst)} corners x {ndraw} draws: {worst:.1f} mVppd at BER 1e-12 "
          f"(extrapolated, not measured); extrapolation failures: {fails}")
    print(f"proposed R8 target 50 mVppd: {'MET' if good and worst <= 50 and not fails else 'NOT MET'} "
          f"(reported, not relaxed; sampler offset/noise are UNFITTED)")
    return 0 if good and worst <= 50 and not fails else 3


# ---- R11 / R13 ---------------------------------------------------------------------------
def r11(args, fits, rec_id):
    n = 15000 if args.quick else 40000
    print("\nLock/hold of the behavioural CDR from a 0.4 UI initial phase offset (lock = 64-word mean of e within 0.05 UI for the rest of the run)")
    print("ppm     lock after (words)   hold: peak |e| UI   rms UI   slips   label")
    bad = 0
    for ppm in (0, 300, -300):
        e = cm.run(n, ppm=ppm, init_offset_ui=0.4, vote_noise_ui=args.vote_noise_ui) / cm.UI
        mavg = np.convolve(e, np.ones(64) / 64, mode="same")
        out = np.nonzero(np.abs(mavg[32:-32]) >= 0.05)[0]
        lock = int(out[-1]) + 33 if len(out) else 0
        tail = e[n // 2:]
        sl = int(np.count_nonzero(np.abs(e[lock:]) >= 0.5))
        ok = lock < n // 2 and sl == 0
        bad += not ok
        print(f"{ppm:+5d}   {lock:10d}           {np.max(np.abs(tail)):.4f}              {np.std(tail):.4f}   {sl:3d}    "
              f"simulated (behavioural bang-bang) {'locks+holds' if ok else 'DOES NOT LOCK/HOLD'}")
    print("PVT-edge: the loop model has no per-corner input (PI/sampler delay and aperture jitter have no record). "
          "The latch fit enters through R12's eye; R11 is corner-independent and says so.")
    return 3 if bad else 0


def r13(args, fits, rec_id):
    settle, win = (15000, 62500) if args.quick else (30000, 62500)     # 62500 words x 16 UI = 1e6 UI
    print(f"\nFrequency offset: lock for {settle} words, then count slips (|e| >= 0.5 UI) over {win * 16} UI")
    print("ppm     analog delay   peak |e| UI   slips   label")
    bad = 0
    for ppm in (300, -300):
        for ad in (None, 0, 2):
            flt_run = cm.run(settle + win, ppm=ppm, vote_noise_ui=args.vote_noise_ui, analog_delay=ad, fmax=args.fmax)
            e = flt_run[settle:] / cm.UI
            sl = cm.slips(flt_run, settle)
            bad += (ad is None) and sl > 0
            tag = "assumed" if ad is None else f"{ad} (sens.)"
            print(f"{ppm:+5d}   {tag:12s}   {np.max(np.abs(e)):.4f}        {sl:5d}   "
                  f"simulated (behavioural bang-bang) {'no slips' if sl == 0 else 'SLIPS'}")
    print("PVT-edge: corner-independent in this model (see r11); analog delay sensitivity shown instead.")
    print(f"proposed R13 (+-300 ppm, zero slips over 1e6 UI): {'MET' if not bad else 'NOT MET'}")
    return 3 if bad else 0


# ---- R12 ---------------------------------------------------------------------------------
def mask(f_hz):
    return max(0.15, 1.5e6 / f_hz)


def r12(args, fits, rec_id):
    freqs = [1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8]
    grid = np.geomspace(0.05, 30.0, 12 if args.quick else 18)
    print("\nSJ sweep through the behavioural CDR: peak recovered-clock error vs SJ amplitude (UIpp), per frequency")
    peaks = {}
    for f in freqs:
        n = int(min(40000, max(15000, 4 / (f * cm.WORD_S))))
        settle = n // 3
        peaks[f] = [float(np.max(np.abs(cm.run(n, sj_uipp=a, sj_hz=f, vote_noise_ui=args.vote_noise_ui)[settle:])) / cm.UI)
                    for a in grid]
    print("Strict tolerance = largest amplitude whose peak error stays within half the 1e-12 eye width of the corner "
          "(eye without CDR jitter; the CDR's own dither is in the peak error). 0.00 = the eye is already consumed at "
          "the smallest swept amplitude. Slip-free bound = largest amplitude with peak error < 0.5 UI.")
    print("corner                 eye@1e-12   " + "  ".join(f"{f / 1e6:g}M".rjust(7) for f in freqs) + "   vs mask")
    bad = 0
    for cid in pick_corners(args, fits):
        ber, ext = eye(args, corner_pmfs(args, fits, cid))
        if not ext["ok"]:
            print(f"{cid:22s} eye width unavailable ({ext['reason']}): tolerance not graded")
            bad += 1
            continue
        half = ext["width"] / 2
        tol = []
        for f in freqs:
            t = 0.0
            for a, pk in zip(grid, peaks[f]):
                if pk > half:
                    break
                t = a
            tol.append(t)
        ok = all(t >= mask(f) for t, f in zip(tol, freqs))
        bad += not ok
        print(f"{cid:22s} {ext['width']:+.3f} UI  " + "  ".join(f"{t:7.2f}" for t in tol)
              + f"   {'meets' if ok else 'BELOW MASK'}")
    sf = []
    for f in freqs:
        t = 0.0
        for a, pk in zip(grid, peaks[f]):
            if pk >= 0.5:
                break
            t = a
        sf.append(t)
    print("slip-free bound (corner-independent)  " + "  ".join(f"{t:7.2f}" for t in sf))
    print("mask UIpp  " + " " * 24 + "  ".join(f"{mask(f):7.2f}" for f in freqs))
    print("labels: eye width = extrapolated (dual-Dirac Q-scale wall fit, BER 1e-9..1e-4) over "
          + lc.label_fit(rec_id) + "; tolerance = simulated (behavioural bang-bang). Not measured. "
          "Grid ceiling 30 UIpp: a value of 30 means 'at least'.")
    return 3 if bad else 0


BENCH = {"r8": (r8, "R8 RX sensitivity, BER 1e-12 (dual-Dirac extrapolated), PVT-full + sampler MC"),
         "r11": (r11, "R11 CDR lock/hold (behavioural bang-bang)"),
         "r12": (r12, "R12 sinusoidal jitter tolerance vs mask"),
         "r13": (r13, "R13 +-300 ppm offset, slips over 1e6 UI"),
         "r15": (r15, "R15 PRBS-31 statistical eye + CDR, 1e-12 by dual-Dirac extrapolation")}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bench", choices=sorted(BENCH))
    ap.add_argument("--corners", default=None, help="full (27 HBT PVT points) | edge (8) | a corner id")
    ap.add_argument("--channel", default="CH-A", choices=sorted(lc.channel_model.CHANNELS))
    ap.add_argument("--rate", type=float, default=10.0, help="Gb/s")
    ap.add_argument("--swing-mvppd", type=float, default=500.0, help="pad swing (R4 500 mVppd, channel DC gain 0 dB)")
    ap.add_argument("--ctle-code", type=int, default=7, choices=range(8))
    ap.add_argument("--vote-noise-ui", type=float, default=A["rj_ui"],
                    help="rms noise on each PD decision, UI (UNFITTED; 0 = noise-free DR-007 case)")
    ap.add_argument("--fmax", type=int, default=None, help="override FMAX (negative control only)")
    ap.add_argument("--strict", action="store_true", help="exit 3 when a proposed-spec threshold is not met")
    ap.add_argument("--quick", action="store_true", help="short configuration (smoke test)")
    args = ap.parse_args(argv)
    run, args.title = BENCH[args.bench]
    if args.corners is None:
        args.corners = "full" if args.bench in ("r8", "r15") else "edge"
    fits, rec_id = lc.ctle_fits()
    header(args.bench.upper(), args, fits, rec_id)
    rc = run(args, fits, rec_id)
    print(f"result: {'thresholds met' if rc == 0 else 'a proposed-spec threshold is NOT met (see above)'}")
    return rc if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
