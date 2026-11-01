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


LATENCY = 3     # clocks from the word's edge to corr / corr_valid (P1, P2, P3)


def corr_of(dut):
    v = dut.corr.value
    return int(v.to_signed()) if hasattr(v, "to_signed") else int(v)


async def feed(dut, m, d, e, flush=True):
    """Drive one word; with flush, wait out the pipeline and check the result."""
    dut.d_word.value, dut.e_word.value, dut.en.value = d, e, 1
    want = m.word(d, e)
    await FallingEdge(dut.clk)
    dut.en.value = 0
    if flush:
        for _ in range(LATENCY - 1):
            await FallingEdge(dut.clk)
        got = corr_of(dut)
        if got != want or int(dut.corr_valid.value) != 1:
            bu.fail("model", f"corr got {got} valid {int(dut.corr_valid.value)}, want {want}")
    return want


@cocotb.test()
async def random_words_match_model(dut):
    """Back to back: one word per clock, results checked LATENCY clocks later."""
    rng = random.Random(11)
    await setup(dut)
    m = ref.CdrPd()
    pending = []
    for n in range(4000 + LATENCY - 1):
        if n < 4000:
            d, e = rng.getrandbits(16), rng.getrandbits(16)
            dut.d_word.value, dut.e_word.value, dut.en.value = d, e, 1
            pending.append(m.word(d, e))
        else:
            dut.en.value = 0
        await FallingEdge(dut.clk)
        if n >= LATENCY - 1:
            want = pending.pop(0)
            got = corr_of(dut)
            if got != want or int(dut.corr_valid.value) != 1:
                bu.fail("model", f"word {n - LATENCY + 1}: corr got {got} valid {int(dut.corr_valid.value)}, want {want}")
    dut.en.value = 0
    await FallingEdge(dut.clk)
    if int(dut.corr_valid.value) != 0 or pending:
        bu.fail("drain", "corr_valid still high / results left after the last word")


@cocotb.test()
async def spaced_words_match_model(dut):
    rng = random.Random(12)
    await setup(dut)
    m = ref.CdrPd()
    for _ in range(300):
        await feed(dut, m, rng.getrandbits(16), rng.getrandbits(16))
        for _ in range(rng.randrange(3)):
            await FallingEdge(dut.clk)


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
    for _ in range(LATENCY + 1):
        await FallingEdge(dut.clk)
    if int(dut.corr_valid.value) != 0:
        bu.fail("enable", "corr_valid raised while en=0")
