"""Statistical-eye core and fit inputs for the link benches (DR-002 step c).

Everything here is SIMULATED / EXTRAPOLATED. Nothing is measured. numpy only
(scipy.special.erfc is used when present, else math.erfc).

Chain (DR-002): transistor-level record -> behavioural model -> statistical eye
over the R14 channel -> dual-Dirac tail extrapolation.
  * channel   : spec/channel/channel_model.py (R14), zero-dispersion phase (pure delay,
                so the pulse is symmetric about its peak: pessimistic precursor ISI).
  * CTLE      : per-corner piecewise-linear |H| fitted to the ctle_ac record's
                gain at 0.1 / 2.5 / 5 GHz; -20 dB/dec beyond 5 GHz (UNFITTED).
  * sampler   : input-referred noise and offset sigma are UNFITTED ASSUMPTIONS: no
                record carries a sampler Monte Carlo (rx latch records hold q swing only).
"""
import importlib.util
import json
import math
import pathlib
import re
import sys

import numpy as np

try:
    from scipy.special import erfc as _erfc
except ImportError:  # pragma: no cover
    _erfc = np.frompyfunc(math.erfc, 1, 1)

REPO = pathlib.Path(__file__).resolve().parents[2]
M = 64                      # samples per UI of the pulse response
NUI = 256                   # pulse record length, UI
KCUR = 24                   # cursors each side

ASSUMPTIONS = {             # UNFITTED: no transistor-level record exists for these
    "sigma_noise_mv": 2.0,  # sampler input-referred rms noise, differential, at the latch input
    "sigma_offset_mv": 5.0, # sampler input-referred offset, 1 sigma (Monte Carlo draws)
    "rj_ui": 0.02,          # random jitter, rms
    "dj_uipp": 0.0625,      # dual-Dirac deterministic jitter, pk-pk
}


def qfun(x):
    return 0.5 * np.asarray(_erfc(np.asarray(x, dtype=float) / math.sqrt(2.0)), dtype=float)


def qinv(p):
    """Inverse Q for scalar p in (0, 0.5], by bisection."""
    lo, hi = 0.0, 40.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if 0.5 * math.erfc(mid / math.sqrt(2.0)) > p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, REPO / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


channel_model = load_module("spec/channel/channel_model.py", "channel_model")
serdes_ref = load_module("rtl/tests/serdes_ref.py", "serdes_ref")


# ---- inputs read from the repo, never re-typed -------------------------------------------
def rtl_loop_params():
    """KP/KI/FMAX/PHASE_INIT defaults of rtl/serdes_cdr_filter.v."""
    src = (REPO / "rtl/serdes_cdr_filter.v").read_text()

    def num(name):
        m = re.search(rf"parameter\s+(?:signed\s+)?(?:\[[^\]]*\]\s+)?{name}\s*=\s*(?:\d+'s?([dh]))?([0-9a-fA-F]+)", src)
        if not m:
            raise SystemExit(f"linkcore: cannot read {name} from rtl/serdes_cdr_filter.v")
        return int(m.group(2), 16 if m.group(1) == "h" else 10)
    return {"KP": num("KP"), "KI": num("KI"), "FMAX": num("FMAX"), "PHASE_INIT": num("PHASE_INIT")}


def dr007_delays():
    """Digital delay (clocks) from DR-007's table; analog delay is the ASSUMED value stated there."""
    src = (REPO / "spec/decisions/DR-007-cdr-loop-analysis.md").read_text()
    d = re.search(r"\|\s*Digital\s*\|\s*\*\*(\d+)\*\*", src)
    a = re.search(r"\|\s*Analog[^|]*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*ASSUMED", src)
    if not (d and a):
        raise SystemExit("linkcore: cannot read the delay table of DR-007")
    return {"digital": int(d.group(1)), "analog_assumed": int(a.group(1))}


def latest_rx_record():
    recs = sorted(p for p in (REPO / "sim/rx/records").iterdir() if (p / "ctle_ac.report.json").exists())
    if not recs:
        raise SystemExit("linkcore: no sim/rx/records/*/ctle_ac.report.json")
    return recs[-1]


def ctle_fits(record=None):
    """{corner_id: {code: (g0.1, g2.5, g5) dB}} from the ctle_ac record, plus the record id."""
    rec = pathlib.Path(record) if record else latest_rx_record()
    rep = json.loads((rec / "ctle_ac.report.json").read_text())
    fits = {}
    for c in rep["corners"]:
        if c.get("status") != "pass":
            continue
        v = {m["name"]: m["value"] for m in c["measurements"] if m["value"] is not None}
        fits[c["corner_id"]] = {k: (v[f"ctle_c{k}_g0p1g_db"], v[f"ctle_c{k}_g2p5g_db"], v[f"ctle_c{k}_g5g_db"])
                                for k in range(8)}
    return fits, rec.name


def edge_corners(fits):
    """PVT-edge: both slow/fast HBT corners at the low-V/hot and high-V/cold extremes."""
    want = [(p, v, t) for p in ("hbt_bcs", "hbt_wcs") for (v, t) in ((1.08, 125), (1.32, -40))]
    out = []
    for cid in fits:
        p, v, t = cid.split("/")
        if (p, float(v[:-1]), int(t[:-1])) in want:
            out.append(cid)
    return out


# ---- pulse response ----------------------------------------------------------------------
def ctle_gain_db(f_ghz, pts):
    lf = np.log10(np.maximum(f_ghz, 1e-3))
    xs = np.log10([0.1, 2.5, 5.0])
    g = np.interp(lf, xs, pts)
    hi = f_ghz > 5.0
    g = np.where(hi, pts[2] - 20.0 * np.log10(np.maximum(f_ghz, 5.0) / 5.0), g)
    return g


def pulse_response(channel, rate_gbps, ctle_pts):
    """Single-bit response of TX (rect, 1 UI, unit level) -> channel -> CTLE. Returns (p, centre index)."""
    ui_ns = 1.0 / rate_gbps
    n = M * NUI
    dt = ui_ns / M
    rect = np.zeros(n)
    rect[:M] = 1.0
    f = np.fft.rfftfreq(n, dt)                       # GHz
    il = channel_model.CHANNELS[channel][0] * np.sqrt(f) + channel_model.CHANNELS[channel][1] * f
    gain_db = -il + (ctle_gain_db(f, ctle_pts) if ctle_pts is not None else 0.0)
    p = np.fft.irfft(np.fft.rfft(rect) * 10 ** (gain_db / 20.0), n)
    c0 = int(np.argmax(p))
    return p, c0


def isi_pmfs(p, c0, nbins=4096):
    """Per sampling phase m (tau=(m-M/2)/M UI): (h0, x, pmf) with ISI support x (unit level, V per V of
    symbol amplitude), PRBS-31 treated as independent +-1 symbols over +-KCUR cursors."""
    out = []
    for m in range(M):
        base = c0 + m - M // 2
        h = np.array([p[(base + k * M) % len(p)] for k in range(-KCUR, KCUR + 1)])
        h0 = h[KCUR]
        isi = np.abs(np.delete(h, KCUR))
        vmax = float(isi.sum()) + 1e-12
        half = nbins // 2 - 4
        dv = vmax / half
        pmf = np.zeros(nbins)
        pmf[nbins // 2] = 1.0
        for b in isi:
            s = b / dv
            if s < 1e-3:
                continue
            i, fr = int(s), s - int(s)
            pmf = 0.5 * ((1 - fr) * np.roll(pmf, i) + fr * np.roll(pmf, i + 1)
                         + (1 - fr) * np.roll(pmf, -i) + fr * np.roll(pmf, -i - 1))
        keep = pmf > 1e-18
        out.append((h0, (np.nonzero(keep)[0] - nbins // 2) * dv, pmf[keep] / pmf[keep].sum()))
    return out


def ber_phase(pm, amp_v, sigma_v, offset_v):
    """BER at one sampling phase for symbol amplitude amp_v (V, i.e. Vppd/2 at the pad), noise sigma_v and
    sampler offset offset_v, both at the latch input. ISI taken from pmf pm = (h0, x, pmf)."""
    h0, x, w = pm
    v = amp_v * (h0 + x)
    return 0.5 * float(np.dot(w, qfun((v - offset_v) / sigma_v) + qfun((v + offset_v) / sigma_v)))


def jitter_kernel(rj_ui, dj_uipp):
    """Dual-Dirac (+-dj/2) x Gaussian rj on the 1/M UI grid: {grid shift: weight}."""
    g = 1.0 / M
    if rj_ui < 0.5 * g:
        raise SystemExit(f"linkcore: rj {rj_ui} UI is below the {g / 2:.4f} UI grid resolution")
    half = int(round(dj_uipp / 2 / g))
    k = np.arange(-int(8 * rj_ui / g) - 1, int(8 * rj_ui / g) + 2)
    w = np.exp(-0.5 * ((k * g) / rj_ui) ** 2)
    w /= w.sum()
    ker = {}
    for s in (-half, half):
        for ki, wi in zip(k, w):
            ker[s + int(ki)] = ker.get(s + int(ki), 0.0) + 0.5 * wi
    return ker


def bathtub(pmfs, amp_v, sigma_v, offset_v, kernel):
    """BER vs sampling phase (index m on the 1/M UI grid), jitter-convolved. Returns array length M."""
    b0 = np.array([ber_phase(pm, amp_v, sigma_v, offset_v) for pm in pmfs])
    out = np.zeros(M)
    for s, wi in kernel.items():
        out += wi * np.roll(b0, -s)          # sample phase m+s sees BER0 at m+s
    return out


def wall_extrapolate(tau, ber, target=1e-12, lo=1e-9, hi=1e-4):
    """Dual-Dirac Q-scale fit of each bathtub wall (DR-002 step 4). tau in UI (ascending, one UI centred on
    the best phase). Returns dict(width, tl, tr, residual, fit_range, ok, reason)."""
    i0 = int(np.argmin(ber))
    res = {"ok": False, "fit_range": f"BER {lo:.0e}..{hi:.0e}", "floor": float(ber[i0])}
    if ber[i0] > lo:
        res["reason"] = f"bathtub floor {ber[i0]:.2e} never reaches {lo:.0e}: no data to extrapolate from"
        return res
    fits = []
    for side in (-1, 1):
        idx = [i for i in (range(i0, -1, -1) if side < 0 else range(i0, len(ber))) if lo <= ber[i] <= hi]
        if len(idx) < 3:
            res["reason"] = f"{'left' if side < 0 else 'right'} wall has {len(idx)} points in the fit range (need 3)"
            return res
        q = np.array([qinv(float(ber[i])) for i in idx])
        t = tau[idx]
        a, b = np.polyfit(t, q, 1)
        if a * side >= 0:
            res["reason"] = "wall slope has the wrong sign"
            return res
        fits.append((a, b, float(np.sqrt(np.mean((np.polyval([a, b], t) - q) ** 2)))))
    q12 = qinv(target)
    tl, tr = (q12 - fits[0][1]) / fits[0][0], (q12 - fits[1][1]) / fits[1][0]
    res.update(ok=True, tl=tl, tr=tr, width=tr - tl, residual=max(f[2] for f in fits))
    return res


def amp_extrapolate(amps, bers, target=1e-12, lo=1e-9, hi=1e-4):
    """Q-scale fit of BER vs amplitude (mV) at the best phase. Returns (amp at target or None, reason, residual)."""
    idx = [i for i, b in enumerate(bers) if lo <= b <= hi]
    if len(idx) < 3:
        return None, f"only {len(idx)} amplitude points with BER in {lo:.0e}..{hi:.0e} (need 3)", None
    q = np.array([qinv(float(bers[i])) for i in idx])
    a, b = np.polyfit(np.asarray(amps)[idx], q, 1)
    if a <= 0:
        return None, "Q does not grow with amplitude", None
    return (qinv(target) - b) / a, "", float(np.sqrt(np.mean((np.polyval([a, b], np.asarray(amps)[idx]) - q) ** 2)))


def label_fit(rec_id, extra=""):
    return f"simulated (behavioural, fitted to sim/rx/records/{rec_id}/ctle_ac){extra}"
