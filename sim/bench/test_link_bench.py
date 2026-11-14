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


def test_loop_override_is_model_only():
    n = 20000
    base = cm.run(n, vote_noise_ui=0.02)[n // 2:] / cm.UI
    fix = cm.run(n, vote_noise_ui=0.02, kp=8, ki=0)[n // 2:] / cm.UI
    assert lc.rtl_loop_params()["KP"] == 16                      # the RTL value is untouched by an override
    assert np.std(fix) < 0.5 * np.std(base)                      # issue #102: dither falls with the lower gain
    rc, out = run_bench("r15", "--quick", "--corners", CORNER, "--kp", "8", "--ki", "0")
    assert "LOOP WHAT-IF: KP=8 KI=0" in out and "rtl/ is unchanged" in out and rc == 0


def test_r12_grid_contains_the_mask_amplitude():
    rc, out = run_bench("r12", "--quick", "--corners", CORNER, "--kp", "8", "--ki", "0")
    assert "meets" in out and "BELOW MASK" not in out, out        # exact mask amplitude graded, not a coarse grid


def test_loop_too_slow_for_ppm_is_reported():
    n, settle = 40000, 20000
    assert cm.slips(cm.run(n, ppm=300, kp=4, ki=0), settle) > 0    # KP*votes < 300 ppm slew: the bench must fail it


def test_arch_defaults_reproduce_dr009():
    """DR-011 options off: the model is the DR-009 model, bit for bit (the RTL baseline and the KP=8 KI=0 what-if)."""
    n = 12000
    for kw in (dict(), dict(kp=8, ki=0)):
        a = cm.run(n, **kw)
        b = cm.run(n, **kw, frac=0, decim=1, gear=None, vote="sum", digital_delay=None, pi_shift=7)
        assert np.array_equal(a, b), kw
    assert abs(np.std(cm.run(20000, kp=8, ki=0)[10000:] / cm.UI) - 0.0284) < 0.001      # DR-009's 0.0286 UI (run length differs)


def test_arch_options_run_and_are_model_only():
    n = 20000
    rec = dict(kp=8, ki=1, frac=6, decim=16, fmax=1023)
    e = cm.run(n, **rec)[n // 2:] / cm.UI
    assert np.std(e) < 0.04                                              # dither as low as DR-009's setting
    assert cm.slips(cm.run(40000, ppm=500, **rec), 20000) == 0           # the +-500 ppm stretch column holds
    assert cm.slips(cm.run(40000, ppm=500, kp=8, ki=0), 20000) > 0       # DR-009's proportional-only loop does not
    assert np.std(cm.run(n, digital_delay=3)[n // 2:]) < np.std(cm.run(n)[n // 2:])      # shorter latency lowers dither
    assert cm.slips(cm.run(40000, ppm=300, vote="sign", kp=8, ki=0), 20000) > 0          # negative control: sign vote slews too slowly
    assert lc.rtl_loop_params()["KP"] == 16                              # no flag touches the RTL value
    rc, out = run_bench("r11", "--quick", "--kp", "8", "--ki", "1", "--frac", "6", "--decim", "16")
    assert "ARCH WHAT-IF (DR-011" in out and "rtl/ is unchanged" in out and rc == 0, out


def test_r13_reports_the_500ppm_stretch_column_ungraded():
    rc, out = run_bench("r13", "--quick", "--kp", "8", "--ki", "0")
    assert "stretch column, not graded" in out and "SLIPS (stretch" in out and "R13 (+-300 ppm, zero slips over 1e6 UI): MET" in out


def test_graded_rules_have_one_definition():
    """Issue #159: the R12 mask and the R11 lock rule are graded values, so they live in linkcore only.

    The mask amplitudes are pinned to the proposed R12 numbers here, which is what makes the single
    definition traceable: link_bench r12 grades tolerance against it and link_sensitivity ratios its
    slew table to it, and neither may carry its own copy.
    """
    import link_sensitivity as ls
    freqs = (1e5, 3e5, 1e6, 3e6, 1e7)
    assert [lc.r12_mask(f) for f in freqs] == [15.0, 5.0, 1.5, 0.5, 0.15]      # 1.5 UIpp.MHz slope
    assert lc.r12_mask(3e7) == 0.15 and lc.r12_mask(1e8) == 0.15               # ... onto the floor
    assert ls.MASK_PTS == {f: lc.r12_mask(f) for f in freqs}                   # not a second copy
    assert not hasattr(lb, "mask"), "link_bench must grade against lc.r12_mask"

    # lock_word on a step: 0.4 UI for 2000 words, then 0. The 64-word mean (mode='same', so centred on
    # its window) last leaves +-0.05 UI at word 2024, reported with the window's half-lag: 2024 + 1 + 32.
    e = np.concatenate([np.full(2000, 0.4), np.zeros(8000)])
    assert lc.lock_word(e) == 2025, lc.lock_word(e)
    assert lc.lock_word(np.zeros(4000)) == 0            # never outside the band: locked from word 0
    assert lc.lock_limit(40000) == 20000                # r11's pass limit, one definition


def test_sensitivity_arch_section_runs():
    import link_sensitivity as ls
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ls.main(["--quick", "--section", "arch"])
    out = buf.getvalue()
    assert rc == 0 and "DR-011" in out and "recommended" in out and "E4. slew margin" in out and "FAIL" in out


def test_sensitivity_runs():
    import link_sensitivity as ls
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = ls.main(["--quick", "--section", "loop"])
    out = buf.getvalue()
    assert rc == 0 and "KP=8 KI=0" in out and "UNFITTED" in out and "nothing below is measured" in out


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
