"""serdes_cdr_filter: bit-exact against serdes_ref.CdrFilter, saturation, hold,
clear, and a +-300 ppm (R13) drive at the filter-input level.

The ppm run closes the loop around a bench plant (data phase drifting at the
offset, a bang-bang detector with random transition density). It checks the
FILTER's arithmetic and tracking at the filter input only; it is not the
statistical link/CDR behavioural model (DR-002) and is not link evidence."""
import random

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu
import serdes_ref as ref

WORD_UI = 16
LSB_PER_UI = 16384 / 2            # one clock period = 2 UI (half rate)


async def setup(dut, **inp):
    dut.clear.value = 0
    dut.en.value = 1
    dut.hold.value = 0
    dut.corr_valid.value = 0
    dut.corr.value = 0
    await bu.start(dut)


def sgn(sig):
    v = sig.value
    return v.to_signed() if hasattr(v, "to_signed") else int(v)


async def step(dut, m, corr, valid=1, check=True):
    dut.corr.value = corr
    dut.corr_valid.value = valid
    await FallingEdge(dut.clk)
    if check:
        got = (int(dut.pi_code.value), sgn(dut.freq_o), int(dut.freq_sat.value))
        want = (m.pi_code, m.freq, int(m.sat))
        if got != want:
            bu.fail("model", f"pi/freq/sat got {got}, want {want}")


@cocotb.test()
async def reset_state(dut):
    await setup(dut)
    await FallingEdge(dut.clk)
    m = ref.CdrFilter()
    bu.expect("reset", int(dut.pi_code.value), m.pi_code, "pi_code at reset (mid-scale)")
    if sgn(dut.freq_o) != 0 or int(dut.freq_sat.value):
        bu.fail("reset", "freq/sat not clear at reset")


@cocotb.test()
async def random_votes_match_model(dut):
    rng = random.Random(3)
    await setup(dut)
    m = ref.CdrFilter()
    for _ in range(20000):
        c = rng.randint(-16, 16)
        valid = rng.random() < 0.9
        if valid:
            m.update(c)
        await step(dut, m, c, valid)


@cocotb.test()
async def saturation_and_phase_wrap(dut):
    await setup(dut)
    m = ref.CdrFilter()
    for _ in range(1200):              # +16 per word: freq rails at +1023
        m.update(16)
        await step(dut, m, 16)
    if sgn(dut.freq_o) != 1023 or not int(dut.freq_sat.value):
        bu.fail("saturate+", f"freq {sgn(dut.freq_o)} sat {int(dut.freq_sat.value)}")
    for _ in range(2400):
        m.update(-16)
        await step(dut, m, -16)
    if sgn(dut.freq_o) != -1023 or not int(dut.freq_sat.value):
        bu.fail("saturate-", f"freq {sgn(dut.freq_o)} sat {int(dut.freq_sat.value)}")
    for _ in range(40):                # recover: sat clears once off the rail
        m.update(1)
        await step(dut, m, 1)


@cocotb.test()
async def hold_clear_enable(dut):
    await setup(dut)
    m = ref.CdrFilter()
    for c in (5, -3, 7, 7, 2):
        m.update(c)
        await step(dut, m, c)
    dut.hold.value = 1
    for c in (9, 9, 9):
        await step(dut, m, c)           # model unchanged
    dut.hold.value = 0
    dut.en.value = 0
    for c in (9, 9):
        await step(dut, m, c)
    dut.en.value = 1
    m.update(4)
    await step(dut, m, 4)
    dut.clear.value = 1
    m.clear()
    await step(dut, m, 4)
    dut.clear.value = 0
    bu.expect("clear", int(dut.pi_code.value), 64, "pi_code after clear")


async def ppm_run(dut, ppm, words, seed):
    rng = random.Random(seed)
    await setup(dut)
    m = ref.CdrFilter()
    drift = 8e-6 * ppm * 16384         # phase LSB per word
    data_ph = float(m.phase)           # data starts aligned with the clock
    worst = 0.0
    worst_after = 0.0
    for w in range(words):
        data_ph += drift
        err = ((m.phase - data_ph + 8192) % 16384) - 8192     # clock minus data, LSB
        ntrans = sum(rng.getrandbits(1) for _ in range(WORD_UI))
        corr = -ntrans if err > 0 else ntrans   # clock late (err>0) -> advance (neg)
        m.update(corr)
        await step(dut, m, corr)
        worst = max(worst, abs(err))
        if w > 6000:
            worst_after = max(worst_after, abs(err))
    return m, worst, worst_after


@cocotb.test()
async def tracks_plus_300ppm(dut):
    m, worst, after = await ppm_run(dut, +300, 62500, 1)    # 62500 words = 1e6 UI
    slip = 0.5 * LSB_PER_UI                                 # half a UI
    cocotb.log.info("+300 ppm: freq %d (ideal 39), worst err %.0f LSB, after-acq %.0f LSB, slip limit %.0f",
                    m.freq, worst, after, slip)
    if worst >= slip:
        bu.fail("slip", f"+300 ppm: phase error {worst:.0f} LSB reached half a UI ({slip:.0f})")
    if abs(m.freq - 39) > 6:
        bu.fail("freq", f"+300 ppm: integrator {m.freq}, ideal ~39")


@cocotb.test()
async def tracks_minus_300ppm(dut):
    m, worst, after = await ppm_run(dut, -300, 62500, 2)
    slip = 0.5 * LSB_PER_UI
    cocotb.log.info("-300 ppm: freq %d (ideal -39), worst err %.0f LSB, after-acq %.0f LSB", m.freq, worst, after)
    if worst >= slip:
        bu.fail("slip", f"-300 ppm: phase error {worst:.0f} LSB reached half a UI ({slip:.0f})")
    if abs(m.freq + 39) > 6:
        bu.fail("freq", f"-300 ppm: integrator {m.freq}, ideal ~-39")
