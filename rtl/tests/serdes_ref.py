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
    """Mirror of serdes_prbs_chk (see the RTL header for the rule set)."""

    def __init__(self, order, lock_run=32, loss_thr=8):
        self.order, self.lock_run, self.loss_thr = order, lock_run, loss_thr
        self.clear()

    def clear(self):
        self.h, self.good, self.locked = 0, 0, False
        self.err, self.bits, self.word_err = 0, 0, 0

    def word(self, w):
        n, k = N_K[self.order]
        h, good, lk = self.h, self.good, self.locked
        werr = nbits = 0
        for i in range(16):
            r = (w >> i) & 1
            p = ((h >> (n - 1)) ^ (h >> (n - 1 - k))) & 1
            e = p ^ r
            if lk:
                nbits += 1
                werr += e
                h = ((h << 1) | p) & mask(self.order)
            else:
                h = ((h << 1) | r) & mask(self.order)
                if e:
                    good = 0
                elif good != 255:
                    good += 1
                if not e and good >= self.lock_run and h != 0:
                    lk = True
        if self.locked and werr >= self.loss_thr:
            lk, good = False, 0
        self.h, self.good, self.locked = h, good, lk
        self.word_err = werr
        self.err = min(self.err + werr, 0xFFFFFFFF)
        self.bits = min(self.bits + nbits, 0xFFFFFFFF)


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
