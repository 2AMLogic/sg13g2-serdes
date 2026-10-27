"""serdes_prbs_gen vs serdes_ref.PrbsGen, bit-exact (spec R22, R15)."""
import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu
import serdes_ref as ref


async def setup(dut, sel31):
    dut.en.value = 0
    dut.restart.value = 0
    dut.sel31.value = sel31
    await bu.start(dut)
    dut.restart.value = 1
    await FallingEdge(dut.clk)
    dut.restart.value = 0


async def run_words(dut, order, n, en=1):
    """Call aligned to a falling edge. Word i is read at the falling edge before
    the rising edge that consumes it."""
    g = ref.PrbsGen(order)
    dut.en.value = en
    for i in range(n):
        bu.expect("word", int(dut.word.value), g.next_word(), f"PRBS-{order} word {i}")
        await FallingEdge(dut.clk)


@cocotb.test()
async def prbs7_words(dut):
    await setup(dut, 0)
    await run_words(dut, 7, 3000)


@cocotb.test()
async def prbs31_words(dut):
    await setup(dut, 1)
    await run_words(dut, 31, 3000)


@cocotb.test()
async def prbs7_period_127(dut):
    """The serial stream repeats with period 127 and no shorter one."""
    await setup(dut, 0)
    bits = []
    dut.en.value = 1
    for _ in range(40):
        await FallingEdge(dut.clk)
        bits += ref.bits_of(int(dut.word.value))
    if bits[:127] != bits[127:254]:
        bu.fail("period", "PRBS-7 does not repeat with period 127")
    for p in range(1, 127):
        if bits[:127] == bits[p:p + 127]:
            bu.fail("period", f"PRBS-7 shorter period {p}")
    if sum(bits[:127]) != 64:
        bu.fail("balance", f"PRBS-7 ones per period {sum(bits[:127])}, want 64")


@cocotb.test()
async def enable_holds_and_restart(dut):
    await setup(dut, 1)
    await run_words(dut, 31, 5)
    g = ref.PrbsGen(31)
    for _ in range(5):
        g.next_word()
    nxt = g.next_word()
    dut.en.value = 0
    for _ in range(6):
        bu.expect("hold", int(dut.word.value), nxt, "word changed while en=0")
        await FallingEdge(dut.clk)
    dut.en.value = 1
    bu.expect("resume", int(dut.word.value), nxt, "word after resume")
    await FallingEdge(dut.clk)
    bu.expect("resume+1", int(dut.word.value), g.next_word(), "word after resume")
    # restart reloads the seed
    dut.restart.value = 1
    await FallingEdge(dut.clk)
    dut.restart.value = 0
    bu.expect("restart", int(dut.word.value), ref.PrbsGen(31).next_word(), "word after restart")


@cocotb.test()
async def zero_state_is_escaped(dut):
    """Forcing the all-zero lock-up state reloads the seed (never stuck at 0)."""
    await setup(dut, 0)
    dut.en.value = 1
    await FallingEdge(dut.clk)
    dut.h.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    if int(dut.word.value) == 0:
        bu.fail("lockup", "generator stuck in the all-zero state")
    g = ref.PrbsGen(7)
    g.next_word()
    # after the reload the stream is the seed stream, one word ahead
    bu.expect("reseed", int(dut.h.value) & 0x7F, g.h, "state after zero-state reload")


@cocotb.test()
async def sel_switch_with_restart(dut):
    await setup(dut, 0)
    await run_words(dut, 7, 20)
    dut.sel31.value = 1
    dut.restart.value = 1
    await FallingEdge(dut.clk)
    dut.restart.value = 0
    await run_words(dut, 31, 50)
