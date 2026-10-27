"""serdes_eye_mon dwell controller against a bench model."""
import random

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu

SETTLE = 16


async def setup(dut):
    for n in ("start", "dwell", "chk_locked", "word_valid", "word_err"):
        getattr(dut, n).value = 0
    await bu.start(dut)


async def point(dut, dwell, rng, locked=lambda i: 1, errs=lambda i: 0, start_twice=False):
    """Run one measurement point; returns (err, bits, invalid) and checks timing."""
    dut.dwell.value = dwell
    dut.start.value = 1
    await FallingEdge(dut.clk)
    dut.start.value = 1 if start_twice else 0   # a second start while busy is ignored
    if not int(dut.busy.value):
        bu.fail("busy", "busy not raised after start")
    exp_err, exp_inv, i = 0, 0, 0
    words = SETTLE + max(dwell, 1)
    for w in range(words):
        dut.word_valid.value = 1
        dut.chk_locked.value = locked(w)
        e = errs(w)
        dut.word_err.value = e
        if w >= SETTLE:
            exp_err += e
            exp_inv |= 1 - locked(w)
        await FallingEdge(dut.clk)
        dut.start.value = 0
        dut.word_valid.value = 0
        if rng.random() < 0.5:                       # idle gaps between words
            await FallingEdge(dut.clk)
        if w < words - 1 and not int(dut.busy.value):
            bu.fail("busy", f"busy dropped early at word {w} of {words}")
    await FallingEdge(dut.clk)
    if int(dut.busy.value) or not int(dut.done.value):
        bu.fail("done", f"busy={int(dut.busy.value)} done={int(dut.done.value)} after dwell")
    return int(dut.err_cnt.value), int(dut.bit_cnt.value), int(dut.invalid.value), exp_err, exp_inv


@cocotb.test()
async def clean_and_errored_points(dut):
    rng = random.Random(8)
    await setup(dut)
    for dwell in (1, 5, 64):
        err, bits, inv, e_err, e_inv = await point(
            dut, dwell, rng, errs=lambda i: rng.choice((0, 0, 0, 1, 3)))
        bu.expect("err", err, e_err, f"error count, dwell {dwell}")
        bu.expect("bits", bits, 16 * dwell, f"bit count, dwell {dwell}")
        bu.expect("valid", inv, 0, "invalid flag on a locked point")


@cocotb.test()
async def deterministic_error_count(dut):
    rng = random.Random(1)
    await setup(dut)
    err, bits, inv, e_err, e_inv = await point(dut, 32, rng, errs=lambda i: (i % 5 == 0) * 2)
    bu.expect("err", err, e_err, "error count (settle words excluded)")
    bu.expect("bits", bits, 32 * 16, "bit count")
    err, bits, inv, e_err, e_inv = await point(dut, 0, rng)         # dwell 0 counts as 1
    bu.expect("bits0", bits, 16, "dwell 0 -> one word")


@cocotb.test()
async def lost_lock_flags_point_invalid(dut):
    rng = random.Random(2)
    await setup(dut)
    err, bits, inv, e_err, e_inv = await point(dut, 20, rng, locked=lambda i: 0 if i == SETTLE + 7 else 1)
    bu.expect("invalid", inv, 1, "point flagged invalid after lock loss")
    err, bits, inv, e_err, e_inv = await point(dut, 20, rng, locked=lambda i: 0 if i == 3 else 1)
    bu.expect("settle-unlocked", inv, 0, "unlocked during settle only is not invalid")


@cocotb.test()
async def restart_while_busy_ignored(dut):
    rng = random.Random(6)
    await setup(dut)
    err, bits, inv, e_err, e_inv = await point(dut, 10, rng, start_twice=True)
    bu.expect("bits", bits, 160, "bit count with a start pulse held through the run")
