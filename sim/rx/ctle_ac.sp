* CTLE sizing bench (issue #22): 8 copies of ctle, one per peaking code,
* driven by the same ideal differential source. Sizing evidence, not a spec result.
* vcm and the control levels track the supply (vcm = 0.7917 vdd; control
* high = vdd, low = vdd - 0.25 V). Output load is a 80 fF placeholder per side
* (stand-in for the four latch inputs; replaced by extraction in #24/#28).
.include ../../design/rx/netlists/ctle.spice
Vdd vdd 0 1.2
Bvcm vcm 0 V=0.7917*v(vdd)
Vip inp vcm dc 0 ac 0.5
Vin inn vcm dc 0 ac -0.5
Bk0_0 c0k0 0 V=v(vdd)-0.25
Bk0_0b c0k0b 0 V=v(vdd)
Bk0_1 c0k1 0 V=v(vdd)-0.25
Bk0_1b c0k1b 0 V=v(vdd)
Bk0_2 c0k2 0 V=v(vdd)-0.25
Bk0_2b c0k2b 0 V=v(vdd)
Xd0 inp inn vcm vdd 0 c0k0 c0k0b c0k1 c0k1b c0k2 c0k2b op0 on0 ctle
Clp0 op0 0 80f
Cln0 on0 0 80f
Bd0 d0 0 V=v(op0)-v(on0)
Bk1_0 c1k0 0 V=v(vdd)
Bk1_0b c1k0b 0 V=v(vdd)-0.25
Bk1_1 c1k1 0 V=v(vdd)-0.25
Bk1_1b c1k1b 0 V=v(vdd)
Bk1_2 c1k2 0 V=v(vdd)-0.25
Bk1_2b c1k2b 0 V=v(vdd)
Xd1 inp inn vcm vdd 0 c1k0 c1k0b c1k1 c1k1b c1k2 c1k2b op1 on1 ctle
Clp1 op1 0 80f
Cln1 on1 0 80f
Bd1 d1 0 V=v(op1)-v(on1)
Bk2_0 c2k0 0 V=v(vdd)-0.25
Bk2_0b c2k0b 0 V=v(vdd)
Bk2_1 c2k1 0 V=v(vdd)
Bk2_1b c2k1b 0 V=v(vdd)-0.25
Bk2_2 c2k2 0 V=v(vdd)-0.25
Bk2_2b c2k2b 0 V=v(vdd)
Xd2 inp inn vcm vdd 0 c2k0 c2k0b c2k1 c2k1b c2k2 c2k2b op2 on2 ctle
Clp2 op2 0 80f
Cln2 on2 0 80f
Bd2 d2 0 V=v(op2)-v(on2)
Bk3_0 c3k0 0 V=v(vdd)
Bk3_0b c3k0b 0 V=v(vdd)-0.25
Bk3_1 c3k1 0 V=v(vdd)
Bk3_1b c3k1b 0 V=v(vdd)-0.25
Bk3_2 c3k2 0 V=v(vdd)-0.25
Bk3_2b c3k2b 0 V=v(vdd)
Xd3 inp inn vcm vdd 0 c3k0 c3k0b c3k1 c3k1b c3k2 c3k2b op3 on3 ctle
Clp3 op3 0 80f
Cln3 on3 0 80f
Bd3 d3 0 V=v(op3)-v(on3)
Bk4_0 c4k0 0 V=v(vdd)-0.25
Bk4_0b c4k0b 0 V=v(vdd)
Bk4_1 c4k1 0 V=v(vdd)-0.25
Bk4_1b c4k1b 0 V=v(vdd)
Bk4_2 c4k2 0 V=v(vdd)
Bk4_2b c4k2b 0 V=v(vdd)-0.25
Xd4 inp inn vcm vdd 0 c4k0 c4k0b c4k1 c4k1b c4k2 c4k2b op4 on4 ctle
Clp4 op4 0 80f
Cln4 on4 0 80f
Bd4 d4 0 V=v(op4)-v(on4)
Bk5_0 c5k0 0 V=v(vdd)
Bk5_0b c5k0b 0 V=v(vdd)-0.25
Bk5_1 c5k1 0 V=v(vdd)-0.25
Bk5_1b c5k1b 0 V=v(vdd)
Bk5_2 c5k2 0 V=v(vdd)
Bk5_2b c5k2b 0 V=v(vdd)-0.25
Xd5 inp inn vcm vdd 0 c5k0 c5k0b c5k1 c5k1b c5k2 c5k2b op5 on5 ctle
Clp5 op5 0 80f
Cln5 on5 0 80f
Bd5 d5 0 V=v(op5)-v(on5)
Bk6_0 c6k0 0 V=v(vdd)-0.25
Bk6_0b c6k0b 0 V=v(vdd)
Bk6_1 c6k1 0 V=v(vdd)
Bk6_1b c6k1b 0 V=v(vdd)-0.25
Bk6_2 c6k2 0 V=v(vdd)
Bk6_2b c6k2b 0 V=v(vdd)-0.25
Xd6 inp inn vcm vdd 0 c6k0 c6k0b c6k1 c6k1b c6k2 c6k2b op6 on6 ctle
Clp6 op6 0 80f
Cln6 on6 0 80f
Bd6 d6 0 V=v(op6)-v(on6)
Bk7_0 c7k0 0 V=v(vdd)
Bk7_0b c7k0b 0 V=v(vdd)-0.25
Bk7_1 c7k1 0 V=v(vdd)
Bk7_1b c7k1b 0 V=v(vdd)-0.25
Bk7_2 c7k2 0 V=v(vdd)
Bk7_2b c7k2b 0 V=v(vdd)-0.25
Xd7 inp inn vcm vdd 0 c7k0 c7k0b c7k1 c7k1b c7k2 c7k2b op7 on7 ctle
Clp7 op7 0 80f
Cln7 on7 0 80f
Bd7 d7 0 V=v(op7)-v(on7)
