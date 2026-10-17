#!/usr/bin/env python3
"""Analytic channel model for the sg13g2-serdes link study (spec/channel/README.md).

Insertion loss, f in GHz:   IL(f) = k_skin * sqrt(f) + k_diel * f   [dB]
Phase: pure delay TD_NS (S21 = 10^(-IL/20) * exp(-j*2*pi*f*TD)).
Ports matched and ideal: S11 = S22 = 0. Standard library only.

    python3 -I channel_model.py table            # loss table, prints markdown
    python3 -I channel_model.py s2p CH-A out.s2p # Touchstone, 0..20 GHz, 10 MHz step
"""
import cmath
import math
import sys

CHANNELS = {
    # name: (k_skin dB/sqrt(GHz), k_diel dB/GHz)
    "CH-A": (1.2, 1.5),
    "CH-B": (0.6, 0.75),
}
TD_NS = 1.0
NYQUIST_GHZ = {"5 Gb/s": 2.5, "10 Gb/s": 5.0, "12.5 Gb/s": 6.25}


def il_db(ch, f_ghz):
    k_skin, k_diel = CHANNELS[ch]
    return k_skin * math.sqrt(f_ghz) + k_diel * f_ghz


def s21(ch, f_ghz):
    return 10 ** (-il_db(ch, f_ghz) / 20) * cmath.exp(-2j * math.pi * f_ghz * TD_NS)


def table():
    print("| Channel | " + " | ".join(f"{r} (Nyquist {f} GHz)" for r, f in NYQUIST_GHZ.items()) + " |")
    print("|---|" + "---|" * len(NYQUIST_GHZ))
    for ch in CHANNELS:
        print(f"| {ch} | " + " | ".join(f"{il_db(ch, f):.2f} dB" for f in NYQUIST_GHZ.values()) + " |")


def write_s2p(ch, path):
    with open(path, "w") as out:
        out.write(f"! {ch}: IL = {CHANNELS[ch][0]}*sqrt(f_GHz) + {CHANNELS[ch][1]}*f_GHz dB, delay {TD_NS} ns\n")
        out.write("# GHZ S RI R 50\n")
        for i in range(0, 2001):
            f = i * 0.01
            s = s21(ch, f)
            out.write(f"{f:.2f} 0 0 {s.real:.9g} {s.imag:.9g} {s.real:.9g} {s.imag:.9g} 0 0\n")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "table":
        table()
    elif len(sys.argv) == 4 and sys.argv[1] == "s2p" and sys.argv[2] in CHANNELS:
        write_s2p(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
