"""Shared cocotb helpers. Cycle convention: inputs are driven at a falling edge,
registered outputs are read at the next falling edge (after one rising edge)."""
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge


async def start(dut, zero=(), reset_cycles=4):
    """Start the clock, zero the named inputs, apply synchronous reset."""
    cocotb.start_soon(Clock(dut.clk, 10, unit="ns").start())
    for n in zero:
        getattr(dut, n).value = 0
    dut.rst_n.value = 0
    for _ in range(reset_cycles):
        await FallingEdge(dut.clk)
    dut.rst_n.value = 1


def fail(kind, msg):
    cocotb.log.error("CHECK TRIPPED: %s", kind)
    raise AssertionError(f"[{kind}] {msg}")


def expect(kind, got, want, what):
    if got != want:
        fail(kind, f"{what}: got {got:#x}, want {want:#x}")


class Spi:
    """Bit-banged SPI master (mode 0) for serdes_ctrl / serdes_digital_top."""

    def __init__(self, dut, half=6):
        self.d, self.half = dut, half
        dut.spi_cs_n.value = 1
        dut.spi_sclk.value = 0
        dut.spi_mosi.value = 0

    async def _wait(self, n):
        for _ in range(n):
            await FallingEdge(self.d.clk)

    async def xfer(self, rw, addr, data=0, nbits=24):
        d = self.d
        frame = ((rw & 1) << 23) | ((addr & 0x7F) << 16) | (data & 0xFFFF)
        miso = 0
        d.spi_cs_n.value = 0
        await self._wait(3)
        for i in range(nbits):
            bit = (frame >> (23 - i)) & 1
            d.spi_mosi.value = bit
            await self._wait(self.half)
            if i >= 8:
                miso = (miso << 1) | int(d.spi_miso.value)
            d.spi_sclk.value = 1
            await self._wait(self.half)
            d.spi_sclk.value = 0
        await self._wait(2)
        d.spi_cs_n.value = 1
        await self._wait(4)
        return miso & 0xFFFF

    async def write(self, addr, data):
        await self.xfer(1, addr, data)

    async def read(self, addr):
        return await self.xfer(0, addr)

    async def read32(self, lo):
        return (await self.read(lo)) | ((await self.read(lo + 1)) << 16)
