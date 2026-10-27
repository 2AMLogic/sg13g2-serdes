"""serdes_digital_top: system-level benches through the real SPI interface.

* TX word -> bench serialiser (bit 0 first) -> arbitrary bit misalignment ->
  bench deserialiser -> RX word: the 16:1 word-order round trip and PRBS lock.
* Parallel loopback; serial-loopback pin; counted injected errors read over SPI.
* CDR closed loop at +300 ppm around a bench plant (filter-input level only).
* Pin budget (R22: <= 8 pins) parsed from the top-level port list.
"""
import random
import re
from pathlib import Path

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu
import serdes_ref as ref

CTRL_PRBS_EN, CTRL_EXT, CTRL_S31, CTRL_CHK, CTRL_PLB, CTRL_SLB, CTRL_CDR, CTRL_HOLD = (
    1 << i for i in range(8))
PULSE_CLR, PULSE_SNAP, PULSE_RESTART, PULSE_CDRCLR = 1 << 8, 1 << 9, 1 << 10, 1 << 11


async def setup(dut):
    for n in ("ext_tx_word", "rx_data_word", "rx_edge_word"):
        getattr(dut, n).value = 0
    await bu.start(dut)
    return bu.Spi(dut)


class SerialLoop:
    """Bench stand-in for the analog partition: serialise the TX word (bit 0
    first), delay by `shift` bits, deserialise back into 16-bit RX data words,
    optionally flipping line bits. `run()` keeps it going in the background."""

    def __init__(self, dut, shift=0, flips=()):
        self.d, self.buf, self.flips, self.n = dut, [0] * shift, set(flips), 0
        self.tx_log, self.rx_log = [], []

    async def cycle(self):
        d = self.d
        await FallingEdge(d.clk)
        tx = int(d.tx_word.value)
        self.tx_log.append(tx)
        self.buf += ref.bits_of(tx)
        w = self.buf[:16]
        self.buf = self.buf[16:]
        for k in range(16):
            if self.n + k in self.flips:
                w[k] ^= 1
        self.n += 16
        self.rx_log.append(ref.pack(w))
        d.rx_data_word.value = ref.pack(w)

    async def run(self):
        while True:
            await self.cycle()


@cocotb.test()
async def word_order_round_trip(dut):
    """External words through the TX register, a bit-0-first serialiser at every
    misalignment and the deserialiser: the RX stream is the TX stream delayed by
    `shift` bits, so 16:1 word ordering is intact in both directions."""
    spi = await setup(dut)
    rng = random.Random(1)
    for shift in (0, 1, 7, 15):
        sl = SerialLoop(dut, shift)
        sent = [rng.getrandbits(16) for _ in range(24)]
        for w in sent:
            dut.ext_tx_word.value = w
            await sl.cycle()
        # tx_word is a register loaded at the clock edge that follows the drive
        for i in range(len(sent)):
            bu.expect("tx-reg", sl.tx_log[i], sent[i], f"TX word {i}, shift {shift}")
        stream = [0] * shift
        for w in sl.tx_log:
            stream += ref.bits_of(w)
        for i, g in enumerate(sl.rx_log):
            bu.expect("order", g, ref.pack(stream[16 * i:16 * i + 16]), f"RX word {i}, shift {shift}")


@cocotb.test()
async def prbs_through_serial_path(dut):
    spi = await setup(dut)
    for order, s31 in ((7, 0), (31, CTRL_S31)):
        await spi.write(0x00, PULSE_CLR | PULSE_RESTART)
        await spi.write(0x00, CTRL_PRBS_EN | CTRL_CHK | s31)
        sl = SerialLoop(dut, shift=5, flips={16 * 300 + 3, 16 * 450 + 9, 16 * 451 + 1})
        task = cocotb.start_soon(sl.run())
        for _ in range(700):
            await FallingEdge(dut.clk)
        await spi.write(0x00, CTRL_PRBS_EN | CTRL_CHK | s31 | PULSE_SNAP)
        st = await spi.read(0x06)
        errs = await spi.read32(0x02)
        bits = await spi.read32(0x04)
        if not st & 1 or not int(dut.status_o.value):
            bu.fail("lock", f"PRBS-{order} through serial path: STATUS {st:#x}")
        if errs != 3:
            bu.fail("errcount", f"PRBS-{order}: injected 3 errors, SPI reports {errs}")
        if bits < 16 * 600:
            bu.fail("bits", f"PRBS-{order}: only {bits} checked bits")
        task.cancel()
        await spi.write(0x00, CTRL_EXT)     # everything off between passes


@cocotb.test()
async def parallel_loopback_and_serial_pin(dut):
    spi = await setup(dut)
    await spi.write(0x00, CTRL_PRBS_EN | CTRL_CHK | CTRL_PLB | CTRL_SLB | CTRL_S31)
    rd = random.Random(3)
    for _ in range(300):
        dut.rx_data_word.value = rd.getrandbits(16)    # garbage on the RX pins: ignored
        dut.rx_edge_word.value = rd.getrandbits(16)
        await FallingEdge(dut.clk)
    bu.expect("plb", await spi.read(0x06) & 1, 1, "checker locks in parallel loopback")
    if not int(dut.ser_lb.value):
        bu.fail("ser_lb", "serial-loopback pin low with ser_lb set")
    await spi.write(0x00, CTRL_PRBS_EN | CTRL_CHK | CTRL_PLB | CTRL_S31 | PULSE_SNAP)
    bu.expect("plb-err", await spi.read32(0x02), 0, "no errors in parallel loopback")
    if int(dut.ser_lb.value):
        bu.fail("ser_lb", "serial-loopback pin high with ser_lb clear")


@cocotb.test()
async def cdr_closed_loop_plus_300ppm(dut):
    """CDR through the real PD + filter around a bench plant: the data phase
    drifts at +300 ppm (R13), the edge samples follow the sign of the phase error
    seen through the 7-bit PI code. Filter-input level only; not link evidence."""
    spi = await setup(dut)
    await spi.write(0x00, CTRL_EXT | CTRL_CDR | PULSE_CDRCLR)
    rng = random.Random(5)
    drift = 8e-6 * 300 * 16384
    st = {"data_ph": 64 * 128 + 64.0, "prev": 0, "worst": 0.0, "w": 0}

    async def plant():
        while True:
            st["data_ph"] += drift
            pi = int(dut.pi_code.value)
            err = ((pi * 128 + 64 - st["data_ph"] + 8192) % 16384) - 8192
            bits = [rng.getrandbits(1) for _ in range(16)]
            e, a = 0, st["prev"]
            for k in range(16):
                b = bits[k]
                t = rng.getrandbits(1) if a == b else (a if err < 0 else b)
                e |= t << k
                a = b
            st["prev"] = bits[15]
            dut.rx_data_word.value, dut.rx_edge_word.value = ref.pack(bits), e
            await FallingEdge(dut.clk)
            st["w"] += 1
            if st["w"] > 5000:
                st["worst"] = max(st["worst"], abs(err))

    task = cocotb.start_soon(plant())
    while st["w"] < 24000:
        await FallingEdge(dut.clk)
    worst = st["worst"]                       # tracking is judged before the hold
    await spi.write(0x00, CTRL_EXT | CTRL_CDR | CTRL_HOLD)    # freeze before reading
    freq = await spi.read(0x10)
    freq = freq - 0x10000 if freq & 0x8000 else freq
    code = int(dut.pi_code.value)
    cocotb.log.info("closed loop +300 ppm: freq %d (ideal 39), worst |err| after acquisition %.0f LSB", freq, worst)
    if abs(freq - 39) > 10:
        bu.fail("freq", f"integrator {freq}, ideal ~39")
    if worst > 1024:
        bu.fail("track", f"phase error {worst:.0f} LSB after acquisition")
    for _ in range(200):                      # hold: the plant keeps running, code stays put
        await FallingEdge(dut.clk)
    bu.expect("hold", int(dut.pi_code.value), code, "pi_code moved while cdr_hold")
    task.cancel()
    await spi.write(0x00, CTRL_EXT | CTRL_HOLD | PULSE_CDRCLR)
    bu.expect("cdrclr", await spi.read(0x0F), 64, "PI code after cdr_clear")


@cocotb.test()
async def pin_budget(dut):
    """R22: control/readout through at most 8 pins. Pins are the ports listed
    before the 'boundary to the analog partition' comment in the top module."""
    src = (Path(__file__).resolve().parents[1] / "serdes_digital_top.v").read_text()
    head = src.split("// boundary to the analog partition")[0].split("module serdes_digital_top (")[1]
    pins = re.findall(r"(?:input|output)\s+wire\s+(?:\[[^\]]*\]\s+)?(\w+)", head)
    cocotb.log.info("pins: %s", pins)
    if len(pins) > 8:
        bu.fail("pins", f"{len(pins)} pins {pins} exceeds the 8-pin budget (R22)")
