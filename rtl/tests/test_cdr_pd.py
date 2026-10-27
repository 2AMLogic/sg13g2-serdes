"""serdes_cdr_pd vs serdes_ref.CdrPd (Alexander word reduction)."""
import random

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu
import serdes_ref as ref


async def setup(dut):
    dut.en.value = 0
    dut.d_word.value = 0
    dut.e_word.value = 0
    await bu.start(dut)


async def feed(dut, m, d, e):
    dut.d_word.value, dut.e_word.value, dut.en.value = d, e, 1
    want = m.word(d, e)
    await FallingEdge(dut.clk)
    dut.en.value = 0
    got = int(dut.corr.value.to_signed()) if hasattr(dut.corr.value, "to_signed") else int(dut.corr.value)
    if got != want or int(dut.corr_valid.value) != 1:
        bu.fail("model", f"corr got {got} valid {int(dut.corr_valid.value)}, want {want}")
    return want


@cocotb.test()
async def random_words_match_model(dut):
    rng = random.Random(11)
    await setup(dut)
    m = ref.CdrPd()
    for _ in range(4000):
        await feed(dut, m, rng.getrandbits(16), rng.getrandbits(16))


@cocotb.test()
async def directed_early_late(dut):
    await setup(dut)
    m = ref.CdrPd()
    d = 0xAAAA                       # 0101...: a transition at every bit but bit 0 vs dprev=0
    # edge sample equals the previous data bit -> clock early (+1 per transition)
    e_early = ((d << 1) & 0xFFFF)    # e[k] = d[k-1]
    c = await feed(dut, m, d, e_early)
    if c != 15:
        bu.fail("early", f"all-early word gave {c}, want 15")
    # edge sample equals the current data bit -> clock late (-1 per transition);
    # bit 0 of 0x5555 matches the previous word's last bit (1), so 15 transitions
    nd = ~d & 0xFFFF
    c = await feed(dut, m, nd, nd)
    if c != -15:
        bu.fail("late", f"all-late word gave {c}, want -15")


@cocotb.test()
async def no_transitions_no_votes_and_enable(dut):
    await setup(dut)
    m = ref.CdrPd()
    await feed(dut, m, 0xFFFF, 0x0000)       # dprev=0 -> only bit 0 can transition
    await feed(dut, m, 0xFFFF, 0x1234)
    c = await feed(dut, m, 0xFFFF, 0xBEEF)   # all ones: nothing to vote on
    if c != 0:
        bu.fail("flat", f"flat data produced corr {c}")
    # disabled: corr_valid stays low, dprev not updated
    dut.d_word.value = 0x0000
    dut.en.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    if int(dut.corr_valid.value) != 0:
        bu.fail("enable", "corr_valid raised while en=0")
