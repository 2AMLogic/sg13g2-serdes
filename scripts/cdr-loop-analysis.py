#!/usr/bin/env python3
"""CDR loop delay analysis (DR-007 issue #62; noise-free vote count fixed in #106, see DR-010).  Analytical / simulated, not measured.

Models the word-rate (625 MHz) digital bang-bang loop of rtl/serdes_cdr_filter.v:
    f[n+1] = sat(f[n] + KI*u[n]);  phi[n+1] = phi[n] + KP*u[n] + f[n]   (mod 2^14)
    pi_code = phi[13:7]  (applied phase = 128 * pi_code)
    u[n]    = corr measured D = L-1 words earlier, i.e. corr[n-(L-1)]
              L = clocks around the whole loop (pi_code -> analog -> RX reg -> PD ->
              filter -> pi_code) = DIGITAL + ANALOG.  The filter's own phi[n+1]
              update is one of those L clocks (the model with D=0 is a 1-clock loop),
              so the filter's 3 clocks to pi_code count inside DIGITAL, not on top.
    The same D = L-1 is used by stable_gain_max() and simulate().
Phase unit: 1 LSB = 1/16384 clock period = 1/8192 UI (half-rate).

That recurrence is NOT re-implemented here: simulate() steps
rtl/tests/serdes_ref.CdrFilter, the reference model rtl/tests/test_cdr.py checks
bit-exact against the RTL, and KP/KI/FMAX/PHASE_INIT and the loop delays are read
from the RTL and from DR-007 by sim/bench/loop_inputs.py -- the same inputs
sim/bench/cdrmodel.py uses.  Nothing on this page is a re-typed copy (issue #154).

Usage: python3 -I scripts/cdr-loop-analysis.py        (numpy only, ~20 s)
"""
import pathlib
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sim/bench"))     # loop_inputs (python3 -I omits the script dir)
sys.path.insert(0, str(REPO / "rtl/tests"))     # serdes_ref

import loop_inputs  # noqa: E402
import serdes_ref  # noqa: E402

# ---- inputs read from the repo, never re-typed (sim/bench/linkcore.py's convention) ----
_RTL = loop_inputs.rtl_loop_params()     # rtl/serdes_cdr_filter.v parameter defaults
_DLY = loop_inputs.dr007_delays()        # spec/decisions/DR-007-cdr-loop-analysis.md
KP, KI, FMAX = _RTL["KP"], _RTL["KI"], _RTL["FMAX"]
PHASE_INIT = _RTL["PHASE_INIT"]
DIGITAL = _DLY["digital"]                # RX reg 1 + PD 3 + filter->pi_code 3 (DR-006, via DR-007)
ANALOG_ASSUMED = _DLY["analog_assumed"]  # words; ASSUMPTION, not traced (see DR-007)

UI = 8192.0                      # LSB per UI
HALF_UI = UI / 2
PPM_LSB = 0.131072               # LSB per word per ppm  (16 UI * 1e-6 * 8192)
CRIT_PK_UI = 0.05                # limit-cycle peak error criterion (builder's stated choice)
NWORDS, SETTLE = 120000, 60000


def stable_gain_max(D):
    """Largest linearised PD gain g (votes/LSB) with all roots of
    (z-1)^2 z^D + g (KP (z-1) + KI) = 0 inside the unit circle (D = extra delay)."""
    def stable(g):
        p = np.polymul(np.polymul([1, -1], [1, -1]), [1] + [0] * D)   # (z-1)^2 z^D
        q = g * np.array([KP, KI - KP])                               # g(KP z + KI-KP)
        c = p.astype(float)
        c[-2:] += q
        return np.max(np.abs(np.roots(c))) < 1.0
    lo, hi = 0.0, 1.0
    while stable(hi):
        hi *= 2
        if hi > 1e6:
            return np.inf
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if stable(mid) else (lo, mid)
    return lo


def simulate(L, ppm, mode, sigma_lsb=0.0, seed=1):
    rng = np.random.default_rng(seed)
    D = L - 1
    flt = serdes_ref.CdrFilter(KP, KI, FMAX, PHASE_INIT)
    phi = flt.phase              # unwrapped phase; flt.phase itself is masked to 14 bits
    theta0 = float(phi)
    hist = [0] * D               # delay line: append then pop(0) yields corr[n-D]
    errs = []
    for n in range(NWORDS):
        theta = theta0 + ppm * PPM_LSB * n
        applied = 128 * (phi >> 7)   # = 16384*floor(phi/16384) + 128*pi_code
        e = theta - applied
        nt = 16 if mode == "all16" else rng.binomial(16, 0.5)
        if nt:
            # nt votes per word.  Noise-free, all nt decisions see the same e, so
            # the sum is nt*sign(e); a scalar np.sign(e) would be one vote (DR-007
            # defect, issue #106, superseded by DR-010).
            s = e + (rng.normal(0, sigma_lsb, nt) if sigma_lsb else np.zeros(nt))
            corr = int(np.sum(np.sign(s)))
        else:
            corr = 0
        hist.append(corr)
        u = hist.pop(0)
        prev = flt.phase
        flt.update(u)
        # Unwrap the masked phase: |KP*u + freq| <= KP*16 + FMAX = 1279 < 8192, so the
        # 14-bit wrapped delta fixes the unwrapped step uniquely (cdrmodel.py:97-101).
        phi += ((flt.phase - prev + 8192) % 16384) - 8192
        if n >= SETTLE:
            errs.append(e)
    errs = np.array(errs)
    return np.max(np.abs(errs)), np.std(errs), flt.freq


def main():
    print("# Linearised stability: max PD gain g_max (votes/LSB) vs total delay L")
    print("L  D=L-1  g_max")
    for L in range(2, 15):
        print(f"{L:2d} {L-1:3d}   {stable_gain_max(L-1):.5f}")
    sig = 0.03 * UI
    print(f"\n# Bang-bang sim, +300 ppm, KP={KP} KI={KI}; peak |e| in UI "
          f"(0.5 UI = slip), criterion peak <= {CRIT_PK_UI} UI")
    print("L   all16(noise-free)  Bin(16,.5)(noise-free)  Bin+3%UI rms noise   slip?  PASS")
    rows = {}
    for L in range(2, 15):
        a = simulate(L, 300, "all16")
        b = simulate(L, 300, "bin")
        c = simulate(L, 300, "bin", sigma_lsb=sig)
        slip = max(a[0], b[0], c[0]) >= HALF_UI
        ok = (b[0] / UI <= CRIT_PK_UI) and not slip
        rows[L] = ok
        print(f"{L:2d}  {a[0]/UI:8.4f} (sd {a[1]/UI:.4f})  {b[0]/UI:8.4f} (sd {b[1]/UI:.4f})  "
              f"{c[0]/UI:8.4f} (sd {c[1]/UI:.4f})   {'YES' if slip else 'no ':3s}   {'PASS' if ok else 'fail'}")
    maxL = max([l for l, v in rows.items() if v and all(rows[k] for k in rows if k <= l)], default=None)
    print(f"\nmax total delay L meeting criterion (contiguous from 2): {maxL}")
    print(f"digital = {DIGITAL}, assumed analog = {ANALOG_ASSUMED}, total L = {DIGITAL + ANALOG_ASSUMED}: "
          f"{'PASS' if rows.get(DIGITAL + ANALOG_ASSUMED) else 'FAIL'}")
    print(f"max allowed digital delay at analog={ANALOG_ASSUMED}: {None if maxL is None else maxL - ANALOG_ASSUMED}")
    for ppm in (0, -300):
        r = simulate(DIGITAL + ANALOG_ASSUMED, ppm, "bin")
        print(f"L={DIGITAL + ANALOG_ASSUMED}, {ppm:+d} ppm, Bin noise-free: peak {r[0]/UI:.4f} UI, final freq {r[2]}")


if __name__ == "__main__":
    main()
