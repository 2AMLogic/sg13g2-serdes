"""serdes_loopback: TX source mux, registered TX word, parallel loopback mux."""
import random

import cocotb
from cocotb.triggers import FallingEdge

import bench_util as bu


@cocotb.test()
async def mux_matrix(dut):
    rng = random.Random(4)
    for n in ("src_ext", "prbs_en", "par_lb", "ser_lb_ctl"):
        getattr(dut, n).value = 0
    for n in ("prbs_word", "ext_word", "rx_d_in", "rx_e_in"):
        getattr(dut, n).value = 0
    await bu.start(dut)
    tx_model = 0
    for _ in range(800):
        s_ext, p_en, plb, slb = (rng.getrandbits(1) for _ in range(4))
        pw, ew, rd, re = (rng.getrandbits(16) for _ in range(4))
        dut.src_ext.value, dut.prbs_en.value = s_ext, p_en
        dut.par_lb.value, dut.ser_lb_ctl.value = plb, slb
        dut.prbs_word.value, dut.ext_word.value = pw, ew
        dut.rx_d_in.value, dut.rx_e_in.value = rd, re
        # combinational outputs react to the loopback select and the CURRENT tx_word
        await FallingEdge(dut.clk)
        want_tx = ew if s_ext else (pw if p_en else 0)
        bu.expect("tx", int(dut.tx_word.value), want_tx, "registered TX word")
        bu.expect("rx_d", int(dut.rx_d.value), want_tx if plb else rd, "rx data word")
        bu.expect("rx_e", int(dut.rx_e.value), 0 if plb else re, "rx edge word")
        bu.expect("ser_lb", int(dut.ser_lb.value), slb, "serial loopback control")


@cocotb.test()
async def reset_state(dut):
    dut.src_ext.value = 1
    dut.ext_word.value = 0xFFFF
    for n in ("prbs_en", "par_lb", "ser_lb_ctl", "prbs_word", "rx_d_in", "rx_e_in"):
        getattr(dut, n).value = 0
    await bu.start(dut, reset_cycles=3)
    dut.rst_n.value = 0
    await FallingEdge(dut.clk)
    await FallingEdge(dut.clk)
    bu.expect("reset", int(dut.tx_word.value), 0, "TX word during reset")
