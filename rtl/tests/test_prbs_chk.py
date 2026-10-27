"""serdes_prbs_chk vs serdes_ref.PrbsChk, bit-exact on every word, plus the
behavioural properties the reference alone does not prove (exact error counts,
lock from an arbitrary seed, no lock on stuck-at-0, loss of lock)."""
import random

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu
import serdes_ref as ref


async def setup(dut, sel31):
    dut.en.value = 0
    dut.clear.value = 0
    dut.rx_word.value = 0
    dut.sel31.value = sel31
    await bu.start(dut)


class Drv:
    def __init__(self, dut, order):
        self.d, self.m = dut, ref.PrbsChk(order)

    async def word(self, w):
        """Feed one word; compare all DUT outputs to the model after it."""
        d = self.d
        d.rx_word.value = w
        d.en.value = 1
        self.m.word(w)
        await FallingEdge(d.clk)      # state updated at the rising edge
        d.en.value = 1
        got = (int(d.locked.value), int(d.err_cnt.value), int(d.bit_cnt.value),
               int(d.word_err.value))
        want = (int(self.m.locked), self.m.err, self.m.bits, self.m.word_err)
        if got != want:
            bu.fail("model", f"locked/err/bits/word_err got {got}, want {want}")
        return self.m


def stream(order, nwords, seed_state=None, errors=(), shift=0):
    """Words from the PRBS stream, optionally starting at an arbitrary state, a
    bit offset `shift` (deserialiser misalignment) and with bit errors at the
    given absolute bit positions."""
    h = ref.mask(order) if seed_state is None else seed_state
    bits = ref.prbs_bits(order, nwords * 16 + shift, h)[shift:]
    for pos in errors:
        bits[pos] ^= 1
    return [ref.pack(bits[i * 16:(i + 1) * 16]) for i in range(nwords)]


@cocotb.test()
async def clean_prbs7_locks(dut):
    await setup(dut, 0)
    c = Drv(dut, 7)
    for w in stream(7, 40):
        m = await c.word(w)
    if not m.locked or m.err != 0 or m.bits == 0:
        bu.fail("lock", f"PRBS-7 clean stream: locked={m.locked} err={m.err} bits={m.bits}")


@cocotb.test()
async def clean_prbs31_locks(dut):
    await setup(dut, 1)
    c = Drv(dut, 31)
    for w in stream(31, 40):
        m = await c.word(w)
    if not m.locked or m.err != 0:
        bu.fail("lock", f"PRBS-31 clean stream: locked={m.locked} err={m.err}")


@cocotb.test()
async def lock_from_arbitrary_seed_and_alignment(dut):
    rng = random.Random(23)
    for order in (7, 31):
        for trial in range(6):
            await setup(dut, 1 if order == 31 else 0)
            c = Drv(dut, order)
            st = rng.randrange(1, ref.mask(order) + 1)
            for w in stream(order, 50, st, shift=rng.randrange(16)):
                m = await c.word(w)
            if not m.locked or m.err != 0:
                bu.fail("lock", f"PRBS-{order} seed {st:#x}: locked={m.locked} err={m.err}")


@cocotb.test()
async def injected_errors_counted_once(dut):
    """Single line errors after lock are counted exactly once each (the
    free-running reference does not multiply them by the number of taps)."""
    rng = random.Random(7)
    for order in (7, 31):
        await setup(dut, 1 if order == 31 else 0)
        c = Drv(dut, order)
        nwords = 400
        pos = sorted(rng.sample(range(16 * 60, 16 * nwords - 16, 1), 25))
        # keep errors far enough apart that no word reaches the loss-of-lock threshold
        pos = [p for i, p in enumerate(pos) if i == 0 or p - pos[i - 1] > 40]
        for w in stream(order, nwords, errors=pos):
            m = await c.word(w)
        if m.err != len(pos) or not m.locked:
            bu.fail("count", f"PRBS-{order}: injected {len(pos)}, counted {m.err}, locked={m.locked}")


@cocotb.test()
async def stuck_at_zero_never_locks(dut):
    await setup(dut, 0)
    c = Drv(dut, 7)
    for _ in range(100):
        m = await c.word(0)
    if m.locked:
        bu.fail("stuck0", "checker locked onto an all-zero line")


@cocotb.test()
async def random_data_does_not_hold_lock(dut):
    rng = random.Random(5)
    await setup(dut, 0)
    c = Drv(dut, 7)
    locked_words = 0
    for _ in range(300):
        m = await c.word(rng.getrandbits(16))
        locked_words += m.locked
    if locked_words > 5:
        bu.fail("randlock", f"locked for {locked_words} of 300 random words")


@cocotb.test()
async def loss_of_lock_and_relock(dut):
    await setup(dut, 0)
    c = Drv(dut, 7)
    rng = random.Random(9)
    for w in stream(7, 40):
        m = await c.word(w)
    assert m.locked
    for _ in range(4):
        m = await c.word(rng.getrandbits(16))
    if m.locked:
        bu.fail("loss", "lock not dropped under random data")
    err_before = m.err
    for w in stream(7, 60, 0x55):
        m = await c.word(w)
    if not m.locked or m.err != err_before:
        bu.fail("relock", f"relock failed: locked={m.locked} err {m.err} vs {err_before}")


@cocotb.test()
async def clear_and_saturation(dut):
    await setup(dut, 0)
    c = Drv(dut, 7)
    for w in stream(7, 40):
        await c.word(w)
    dut.err_cnt.value = 0xFFFFFFF8
    dut.bit_cnt.value = 0xFFFFFFF8
    c.m.err = c.m.bits = 0xFFFFFFF8
    # continue the stream from the model state, one flipped bit in every word
    g = c.m.h
    for _ in range(10):   # 8 errors to saturate from ...F8 (+1 per word), 10 words
        bits = []
        for _ in range(16):
            g, b = ref.prbs_step(g, 7)
            bits.append(b)
        bits[0] ^= 1
        await c.word(ref.pack(bits))
    got = (int(dut.err_cnt.value), int(dut.bit_cnt.value))
    if got != (0xFFFFFFFF, 0xFFFFFFFF):
        bu.fail("saturate", f"err/bits {got[0]:#x}/{got[1]:#x}, want both 0xffffffff")
    dut.clear.value = 1
    dut.en.value = 1
    await FallingEdge(dut.clk)
    dut.clear.value = 0
    c.m.clear()
    got = (int(dut.err_cnt.value), int(dut.bit_cnt.value), int(dut.locked.value))
    if got != (0, 0, 0):
        bu.fail("clear", f"clear left err/bits/locked = {got}")
