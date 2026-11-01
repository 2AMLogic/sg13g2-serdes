#!/usr/bin/env python3
"""CDR loop delay analysis (DR-007, issue #62).  Analytical / simulated, not measured.

Models the word-rate (625 MHz) digital bang-bang loop of rtl/serdes_cdr_filter.v:
    f[n+1] = sat(f[n] + KI*u[n]);  phi[n+1] = phi[n] + KP*u[n] + f[n]   (mod 2^14)
    pi_code = phi[13:7]  (applied phase = 128 * pi_code)
    u[n]    = corr measured (L-1) words earlier  (L = total clocks from a word to
              the pi_code that reflects it = DIGITAL + ANALOG)
Phase unit: 1 LSB = 1/16384 clock period = 1/8192 UI (half-rate).

Usage: python3 -I scripts/cdr-loop-analysis.py        (numpy only, ~1 min)
"""
import numpy as np

KP, KI, FMAX = 16, 1, 1023
UI = 8192.0                      # LSB per UI
HALF_UI = UI / 2
PPM_LSB = 0.131072               # LSB per word per ppm  (16 UI * 1e-6 * 8192)
DIGITAL = 7                      # RX reg 1 + PD 3 + filter->pi_code 3 (DR-006)
ANALOG_ASSUMED = 1               # words; ASSUMPTION, not traced (see DR-007)
CRIT_PK_UI = 0.05                # limit-cycle peak error criterion, chosen before running
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
    phi, f = float(1 << 13), 0
    theta0 = phi
    hist = [0] * (D + 1)         # delay line for corr
    errs = []
    for n in range(NWORDS):
        theta = theta0 + ppm * PPM_LSB * n
        applied = 128 * (int(phi) >> 7 & 127) + (int(phi) // 16384) * 16384
        e = theta - applied
        nt = 16 if mode == "all16" else rng.binomial(16, 0.5)
        if nt:
            s = e + (rng.normal(0, sigma_lsb, nt) if sigma_lsb else 0.0)
            corr = int(np.sum(np.sign(s)))
        else:
            corr = 0
        hist.append(corr)
        u = hist.pop(0)
        phi = phi + KP * u + f
        f = max(-FMAX, min(FMAX, f + KI * u))
        if n >= SETTLE:
            errs.append(e)
    errs = np.array(errs)
    return np.max(np.abs(errs)), np.std(errs), f


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
