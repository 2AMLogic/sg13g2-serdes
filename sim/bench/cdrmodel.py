"""Time-domain behavioural bang-bang CDR (DR-002 step d), word-rate (625 MHz).

The loop filter IS rtl/tests/serdes_ref.CdrFilter (bit-exact against rtl/serdes_cdr_filter.v) built with
KP/KI/FMAX parsed from the RTL; the loop delay is DR-007's digital value plus its ASSUMED analog value.
Data is the real PRBS-31 sequence (serdes_ref.prbs_bits). Phase unit: 1 LSB = 1/8192 UI.
SIMULATED, never measured. The PD decision noise and the analog delay are UNFITTED assumptions.
"""
import functools
import math

import numpy as np

import linkcore as lc

UI = 8192.0
HALF_UI = UI / 2
PPM_LSB = 0.131072                 # LSB per word per ppm (DR-007)
WORD_S = 1.6e-9                    # 625 MHz word clock
UI_PER_WORD = 16


@functools.lru_cache(maxsize=4)
def transitions(n_words):
    """Transitions per 16-bit word of the PRBS-31 line sequence (previous word's last bit included)."""
    bits = np.array(lc.serdes_ref.prbs_bits(31, 16 * n_words + 1), dtype=np.int8)
    return (bits[1:] != bits[:-1]).reshape(n_words, 16).sum(axis=1)


class ArchFilter:
    """MODEL-ONLY loop filter for the DR-011 candidates (not the RTL; the RTL is serdes_ref.CdrFilter).
    Same structure as the RTL filter with four extra knobs, all off by default (then this class is not used):
      frac   : integral accumulator carries `frac` extra fractional bits (frequency step = 2^-frac LSB/word)
      decim  : the integral path accumulates `decim` words of votes, then updates once
      gear   : (kp_acq, ki_acq, words): acquisition gains for the first `words` words, then kp/ki (timer gear shift)
    fmax is in whole LSB/word (same unit as the RTL FMAX)."""

    def __init__(self, kp, ki, fmax, phase_init, frac=0, decim=1, gear=None):
        self.kp, self.ki, self.fmax, self.frac, self.decim, self.gear = kp, ki, fmax, frac, decim, gear
        self.phase, self.freq, self.acc, self.cnt, self.n = phase_init, 0, 0, 0, 0

    def update(self, corr):
        kp, ki = self.kp, self.ki
        if self.gear is not None and self.n < self.gear[2]:
            kp, ki = self.gear[0], self.gear[1]
        self.n += 1
        self.acc += corr
        self.cnt += 1
        if self.cnt >= self.decim:
            lim = self.fmax << self.frac
            self.freq = max(-lim, min(lim, self.freq + ki * self.acc))
            self.acc, self.cnt = 0, 0
        self.phase = (self.phase + kp * corr + (self.freq >> self.frac)) & 0x3FFF


def run(n_words, ppm=0.0, sj_uipp=0.0, sj_hz=0.0, init_offset_ui=0.0, vote_noise_ui=0.02, analog_delay=None,
        fmax=None, seed=1, kp=None, ki=None, frac=0, decim=1, gear=None, vote="sum", digital_delay=None, pi_shift=7):
    """Returns e (phase error, LSB) per word. Slip = |e| >= 0.5 UI.
    kp/ki/fmax/analog_delay default to the RTL / DR-007 values; an override is a MODEL what-if (the RTL is unchanged).
    DR-011 model-only options (defaults reproduce DR-009 exactly): frac/decim/gear (ArchFilter), vote='sign' (majority
    of the word's PD decisions, +-1 per word), digital_delay (words, default DR-007's 7), pi_shift (PI step 2^pi_shift LSB,
    default 7 = 1/64 UI)."""
    p = lc.rtl_loop_params()
    dl = lc.dr007_delays()
    L = (dl["digital"] if digital_delay is None else digital_delay) + (dl["analog_assumed"] if analog_delay is None else analog_delay)
    D = max(L - 1, 0)
    if frac == 0 and decim == 1 and gear is None:
        flt = lc.serdes_ref.CdrFilter(p["KP"] if kp is None else kp, p["KI"] if ki is None else ki,
                                      p["FMAX"] if fmax is None else fmax, p["PHASE_INIT"])
    else:
        flt = ArchFilter(p["KP"] if kp is None else kp, p["KI"] if ki is None else ki,
                         p["FMAX"] if fmax is None else fmax, p["PHASE_INIT"], frac, decim, gear)
    rng = np.random.default_rng(seed)
    nt = transitions(n_words)
    delay = [0] * D
    unw = float(flt.phase)
    theta0 = flt.phase + init_offset_ui * UI
    sj_amp = sj_uipp / 2 * UI
    e = np.empty(n_words)
    sigma = vote_noise_ui * UI
    for n in range(n_words):
        theta = theta0 + ppm * PPM_LSB * n
        if sj_amp:
            theta += sj_amp * math.sin(2 * math.pi * sj_hz * WORD_S * n)
        err = theta - (1 << pi_shift) * (int(unw) >> pi_shift)
        e[n] = err
        k = int(nt[n])
        if k == 0:
            corr = 0
        elif sigma == 0:
            corr = k if err > 0 else (-k if err < 0 else 0)
        else:
            p_late = 0.5 * math.erfc(err / sigma / math.sqrt(2))   # P(e + noise < 0)
            late = int(rng.binomial(k, p_late))
            corr = k - 2 * late
        if vote == "sign":
            corr = (corr > 0) - (corr < 0)
        delay.append(corr)
        u = delay.pop(0)
        old = flt.phase
        flt.update(u)
        unw += ((flt.phase - old + 8192) % 16384) - 8192
    return e


def slips(e, start):
    return int(np.count_nonzero(np.abs(e[start:]) >= HALF_UI))
