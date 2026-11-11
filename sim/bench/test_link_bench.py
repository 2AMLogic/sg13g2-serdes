#!/usr/bin/env python3
"""Smoke tests for the behavioural link benches (issue #93). Short configurations only.

    python3 -I sim/bench/test_link_bench.py

Includes the negative controls: the benches must be able to fail.
"""
import contextlib
import io
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import cdrmodel as cm  # noqa: E402
import link_bench as lb  # noqa: E402
import linkcore as lc  # noqa: E402

CORNER = "hbt_typ/1.200V/27C"


def run_bench(*argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = lb.main(list(argv))
    return rc, buf.getvalue()


def test_inputs_come_from_the_repo():
    assert lc.rtl_loop_params() == {"KP": 16, "KI": 1, "FMAX": 1023, "PHASE_INIT": 0x2000}
    assert lc.dr007_delays() == {"digital": 7, "analog_assumed": 1}


def test_entry_points_run():
    for b in ("r8", "r11", "r12", "r13", "r15"):
        rc, out = run_bench(b, "--quick", "--corners", CORNER)
        assert rc in (0, 3), (b, rc)
        assert "nothing below is measured" in out and "UNFITTED" in out, b
        assert "measured)" not in out.replace("not measured", "").replace("nothing below is measured)", ""), b


def test_r13_can_fail():
    n, settle = 40000, 20000
    ok = cm.slips(cm.run(n, ppm=300), settle)
    # The real loop tracks even +-5000 ppm (655 LSB/word < FMAX); with the integrator disabled the
    # proportional path alone (<= 16 votes x KP) cannot follow 5000 ppm, so the bench must report slips.
    assert cm.slips(cm.run(n, ppm=5000), settle) == 0
    bad = cm.slips(cm.run(n, ppm=5000, fmax=0), settle)
    assert ok == 0 and bad > 0, (ok, bad)


def test_extrapolation_failure_is_reported():
    tau = np.linspace(-0.5, 0.5, 64)
    r = lc.wall_extrapolate(tau, np.full(64, 0.1))
    assert not r["ok"] and "never reaches" in r["reason"]
    x, why, _ = lc.amp_extrapolate([1, 2, 3], [0.4, 0.3, 0.2])
    assert x is None and "need 3" in why


def test_eye_closes_without_signal():
    fits, _ = lc.ctle_fits()
    p, c0 = lc.pulse_response("CH-A", 10.0, np.array(fits[CORNER][7]))
    pm = lc.isi_pmfs(p, c0)
    ker = lc.jitter_kernel(0.02, 0.0625)
    assert lc.bathtub(pm, 0.25, 0.002, 0.0, ker).min() < 1e-12
    assert lc.bathtub(pm, 0.001, 0.002, 0.0, ker).min() > 1e-3


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
