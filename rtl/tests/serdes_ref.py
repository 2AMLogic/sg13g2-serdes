"""Pure-Python reference models for the digital partition (no dependencies).

Every RTL module under rtl/ with a defined arithmetic is checked bit-exact
against the model of the same name here. Conventions (also in the RTL headers):

* A "word" is 16 bits; bit i of a word is the i-th bit on the line (bit 0 first).
* PRBS-7  : x^7  + x^6  + 1     PRBS-31 : x^31 + x^28 + 1
  State h holds the last N emitted bits (h[0] newest);
  new bit = h[N-1] ^ h[N-1-K]  with (N, K) = (7, 1) / (31, 3).
"""

N_K = {7: (7, 1), 31: (31, 3)}


def mask(order):
    return (1 << N_K[order][0]) - 1


def prbs_step(h, order):
    n, k = N_K[order]
    nb = ((h >> (n - 1)) ^ (h >> (n - 1 - k))) & 1
    return ((h << 1) | nb) & mask(order), nb


def prbs_bits(order, count, h=None):
    """First `count` bits of the sequence from the all-ones seed (or state h)."""
    h = mask(order) if h is None else h
    out = []
    for _ in range(count):
        h, b = prbs_step(h, order)
        out.append(b)
    return out


def pack(bits):
    w = 0
    for i, b in enumerate(bits):
        w |= (b & 1) << i
    return w


def bits_of(word, n=16):
    return [(word >> i) & 1 for i in range(n)]


class PrbsGen:
    def __init__(self, order):
        self.order = order
        self.h = mask(order)

    def next_word(self):
        w = 0
        for i in range(16):
            self.h, b = prbs_step(self.h, self.order)
            w |= b << i
        return w


class PrbsChk:
    """Register-level mirror of serdes_prbs_chk (the RTL header has the rule set).

    The checker is a pipeline (issue #36): call `clock(word)` once per clock edge
    (word=None for an idle clock, en = 0); the attributes then hold what the DUT
    outputs show after that edge. `err` / `bits` are the resolved counter values
    (the RTL err_cnt port includes its pending carry)."""

    def __init__(self, order, lock_words=4, loss_thr=8):
        self.order, self.lock_words, self.loss_thr = order, lock_words, loss_thr
        self.clear()

    def clear(self):
        self.rr = self.f = 0
        self.good, self.locked, self.was_locked = 0, False, False
        self.vA = self.hcA = False
        self.rxA = 0
        self.vB = self.wlB = False
        self.eB = 0
        self.vC = self.wlC = False
        self.pcC = 0
        self.word_valid, self.word_err = False, 0
        self.err, self.bits = 0, 0

    def _tbits(self, hist, extra):
        n = N_K[self.order][0]
        return [(hist >> (n - 1 - j)) & 1 for j in range(n)] + extra

    def clock(self, word=None, clear=False):
        if clear:
            self.clear()
            return
        n, k = N_K[self.order]
        # ---- combinational values from the current state ----
        hc_now, rr_new = False, self.rr
        if word is not None:
            rx = bits_of(word)
            t = self._tbits(self.rr, rx)
            e_h = [rx[i] ^ t[i] ^ t[i + k] for i in range(16)]
            rr_new = sum(rx[15 - j] << j if j < 16 else ((self.rr >> (j - 16)) & 1) << j
                         for j in range(n))
            hc_now = not any(e_h) and rr_new != 0
        t = self._tbits(self.f, [0] * 16)
        for i in range(16):
            t[n + i] = t[i] ^ t[i + k]
        ref_w = [t[n + i] for i in range(16)]
        f_adv = sum(ref_w[15 - j] << j if j < 16 else ((self.f >> (j - 16)) & 1) << j
                    for j in range(n))
        lost = (self.locked and self.word_valid and self.was_locked
                and self.word_err >= self.loss_thr)
        gain = self.vA and not self.locked and self.hcA and self.good + 1 >= self.lock_words
        # ---- next state (all from the values above) ----
        e_err, e_bits = self.err, self.bits
        if self.word_valid:
            e_err = min(e_err + self.word_err, 0xFFFFFFFF)
            if self.was_locked:
                e_bits = min(e_bits + 16, 0xFFFFFFFF)
        nxt = {}
        nxt["word_valid"] = self.vC
        if self.vC:
            nxt["word_err"] = self.pcC if self.wlC else 0
            nxt["was_locked"] = self.wlC
        if self.vB:
            nxt["pcC"] = bin(self.eB).count("1")
            nxt["wlC"] = self.wlB
        nxt["vC"] = self.vB
        nxt["vB"] = self.vA
        if self.vA:
            nxt["eB"] = pack([a ^ b for a, b in zip(bits_of(self.rxA), ref_w)])
            nxt["wlB"] = self.locked
            nxt["f"] = self.rr if gain else f_adv
        locked, good = self.locked, self.good
        if lost:
            locked, good = False, 0
        elif self.vA and not self.locked:
            if self.hcA:
                if gain:
                    locked = True
                good = min(good + 1, 15)
            else:
                good = 0
        nxt["locked"], nxt["good"] = locked, good
        nxt["vA"] = word is not None
        if word is not None:
            nxt["hcA"], nxt["rxA"], nxt["rr"] = hc_now, word, rr_new
        nxt["err"], nxt["bits"] = e_err, e_bits
        for key, val in nxt.items():
            setattr(self, key, val)

    def word(self, w):
        self.clock(w)


class CdrPd:
    def __init__(self):
        self.dprev = 0

    def word(self, d, e):
        c = 0
        for i in range(16):
            a = self.dprev if i == 0 else (d >> (i - 1)) & 1
            b = (d >> i) & 1
            t = (e >> i) & 1
            if a != b:
                c += 1 if t == a else -1
        self.dprev = (d >> 15) & 1
        return c


class CdrFilter:
    def __init__(self, kp=16, ki=1, fmax=1023, phase_init=0x2000):
        self.kp, self.ki, self.fmax, self.phase_init = kp, ki, fmax, phase_init
        self.clear()

    def clear(self):
        self.phase, self.freq, self.sat = self.phase_init, 0, False

    @property
    def pi_code(self):
        return (self.phase >> 7) & 0x7F

    def update(self, corr):
        f = self.freq + self.ki * corr
        p = self.phase + self.kp * corr + self.freq
        if f > self.fmax:
            self.freq, self.sat = self.fmax, True
        elif f < -self.fmax:
            self.freq, self.sat = -self.fmax, True
        else:
            self.freq, self.sat = f, False
        self.phase = p & 0x3FFF
