"""serdes_ctrl: SPI register interface, register map, pulses, snapshot, aborted frames."""
import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu


async def setup(dut):
    for n in ("chk_locked", "chk_err", "chk_bits", "freq_sat", "eye_busy", "eye_done",
              "eye_invalid", "eye_err", "eye_bits", "pi_code", "freq"):
        getattr(dut, n).value = 0
    await bu.start(dut)
    return bu.Spi(dut)


@cocotb.test()
async def reset_values(dut):
    spi = await setup(dut)
    bu.expect("ctrl", await spi.read(0x00), 0x0002, "CTRL reset value")
    bu.expect("id", await spi.read(0x11), 0x5E2D, "ID")
    bu.expect("dwell", await spi.read(0x09), 0x0100, "EYE_DWELL reset value")
    bu.expect("eph", await spi.read(0x07), 0, "EYE_PH")
    bu.expect("status", await spi.read(0x06), 0, "STATUS")
    for sig, want in (("prbs_en", 0), ("src_ext", 1), ("sel31", 0), ("chk_en", 0),
                      ("par_lb", 0), ("ser_lb", 0), ("cdr_en", 0), ("cdr_hold", 0)):
        if int(getattr(dut, sig).value) != want:
            bu.fail("reset", f"{sig} resets to {int(getattr(dut, sig).value)}, want {want}")
    if int(dut.spi_miso_oe.value):
        bu.fail("oe", "miso output enable high while deselected")


@cocotb.test()
async def write_read_roundtrip(dut):
    spi = await setup(dut)
    await spi.write(0x00, 0x00FD)
    bu.expect("ctrl", await spi.read(0x00), 0x00FD, "CTRL readback")
    ctl = {"prbs_en": 1, "src_ext": 0, "sel31": 1, "chk_en": 1, "par_lb": 1,
           "ser_lb": 1, "cdr_en": 1, "cdr_hold": 1}
    for sig, want in ctl.items():
        if int(getattr(dut, sig).value) != want:
            bu.fail("ctrl-out", f"{sig} = {int(getattr(dut, sig).value)}, want {want}")
    await spi.write(0x07, 0x7F)
    await spi.write(0x08, 0x2A)
    await spi.write(0x09, 0xBEEF)
    bu.expect("eph", await spi.read(0x07), 0x7F, "EYE_PH")
    bu.expect("eofs", await spi.read(0x08), 0x2A, "EYE_OFS")
    bu.expect("dwell", await spi.read(0x09), 0xBEEF, "EYE_DWELL")
    bu.expect("pin-eph", int(dut.eye_ph_off.value), 0x7F, "eye_ph_off pin")
    bu.expect("pin-eofs", int(dut.eye_smp_off.value), 0x2A, "eye_smp_off pin")
    bu.expect("pin-dwell", int(dut.eye_dwell.value), 0xBEEF, "eye_dwell")
    # width masking
    await spi.write(0x07, 0xFFFF)
    bu.expect("eph-mask", await spi.read(0x07), 0x7F, "EYE_PH is 7 bits")
    await spi.write(0x08, 0xFFFF)
    bu.expect("eofs-mask", await spi.read(0x08), 0x3F, "EYE_OFS is 6 bits")


@cocotb.test()
async def pulses_and_snapshot(dut):
    spi = await setup(dut)
    dut.chk_err.value = 0x12345678
    dut.chk_bits.value = 0x9ABCDEF0
    seen = {"chk_clear": 0, "gen_restart": 0, "cdr_clear": 0}

    async def watch():
        while True:
            await FallingEdge(dut.clk)
            for k in seen:
                seen[k] += int(getattr(dut, k).value)
    cocotb.start_soon(watch())
    bu.expect("snap0", await spi.read32(0x02), 0, "ERR snapshot before snap")
    await spi.write(0x00, 0x0002 | (1 << 8) | (1 << 9) | (1 << 10) | (1 << 11))
    for k, n in seen.items():
        if n != 1:
            bu.fail("pulse", f"{k} pulsed {n} times, want exactly 1")
    bu.expect("ctrl-pulse", await spi.read(0x00), 0x0002, "pulse bits must read back 0")
    bu.expect("err", await spi.read32(0x02), 0x12345678, "ERR snapshot")
    bu.expect("bits", await spi.read32(0x04), 0x9ABCDEF0, "BIT snapshot")
    dut.chk_err.value = 0x11111111          # live value changes, snapshot holds
    bu.expect("err-held", await spi.read32(0x02), 0x12345678, "ERR snapshot held")
    # eye start pulse
    seen["eye_start"] = 0
    await spi.write(0x0A, 1)
    if seen["eye_start"] != 1:
        bu.fail("pulse", f"eye_start pulsed {seen['eye_start']} times")


@cocotb.test()
async def status_and_readouts(dut):
    spi = await setup(dut)
    dut.chk_locked.value, dut.freq_sat.value = 1, 1
    dut.eye_busy.value, dut.eye_done.value, dut.eye_invalid.value = 1, 0, 1
    bu.expect("status", await spi.read(0x06), 0b10111, "STATUS")
    dut.eye_err.value, dut.eye_bits.value = 0xCAFE0001, 0x00000040
    bu.expect("eye-err", await spi.read32(0x0B), 0xCAFE0001, "EYE_ERR")
    bu.expect("eye-bits", await spi.read32(0x0D), 0x40, "EYE_BIT")
    dut.pi_code.value = 0x55
    bu.expect("pi", await spi.read(0x0F), 0x55, "PI_CODE")
    dut.freq.value = -39
    bu.expect("freq", await spi.read(0x10), 0xFFD9, "FREQ sign-extended")
    # status pin: lock only counts while the checker is enabled
    if int(dut.status_o.value):
        bu.fail("status_o", "status pin high with the checker disabled")
    await spi.write(0x00, 0x000A)
    await FallingEdge(dut.clk)
    if not int(dut.status_o.value):
        bu.fail("status_o", "status pin low with lock and chk_en")


@cocotb.test()
async def unmapped_and_aborted(dut):
    spi = await setup(dut)
    await spi.write(0x55, 0xFFFF)              # unmapped write: ignored
    for a in (0x01, 0x0A, 0x12, 0x55, 0x7F):
        bu.expect("unmapped", await spi.read(a), 0, f"unmapped address {a:#x} reads 0")
    bu.expect("ctrl", await spi.read(0x00), 0x0002, "CTRL untouched by unmapped write")
    # aborted frame: 23 clocks of a write, then cs_n high -> nothing happens
    await spi.xfer(1, 0x09, 0x1234, nbits=23)
    bu.expect("abort", await spi.read(0x09), 0x0100, "aborted write must not commit")
    # a read frame never writes, even with a data field on MOSI
    await spi.xfer(0, 0x09, 0x1234)
    bu.expect("read-nowrite", await spi.read(0x09), 0x0100, "read frame must not write")
    # back-to-back frames still work
    await spi.write(0x09, 0x0042)
    bu.expect("after", await spi.read(0x09), 0x0042, "frame after aborted frames")
