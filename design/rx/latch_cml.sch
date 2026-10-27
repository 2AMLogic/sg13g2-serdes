v {xschem version=3.4.6 file_version=1.2
* latch_cml: HBT CML sampling latch. Sample pair (dp/dn) and cross-coupled hold
* pair share nothing but the loads; each pair has its own clocked tail HBT
* (clkp gates sample, clkn gates hold) with emitter resistor, so the stack is
* two levels (pair + tail) rather than three, because 1.2 V does not fit the
* conventional three-level latch with ~0.85 V Vbe. Transparent while clkp is
* high. Sizing choice, not a result.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=dp}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=dn}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=clkp}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=clkn}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=vdd}
C {devices/iopin.sym} -120 -100 0 0 {name=p6 lab=vss}
C {devices/iopin.sym} -120 -80 0 0 {name=p7 lab=qp}
C {devices/iopin.sym} -120 -60 0 0 {name=p8 lab=qn}
C {sg13g2_pr/npn13G2.sym} 100 60 0 0 {name=Qs1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 30 2 0 {name=l1 sig_type=std_logic lab=qn}
C {devices/lab_pin.sym} 80 60 0 0 {name=l2 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 120 90 2 0 {name=l3 sig_type=std_logic lab=es}
C {devices/lab_pin.sym} 120 60 2 0 {name=l4 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 60 0 0 {name=Qs2 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 30 2 0 {name=l5 sig_type=std_logic lab=qp}
C {devices/lab_pin.sym} 240 60 0 0 {name=l6 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 280 90 2 0 {name=l7 sig_type=std_logic lab=es}
C {devices/lab_pin.sym} 280 60 2 0 {name=l8 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 420 60 0 0 {name=Qh1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 440 30 2 0 {name=l9 sig_type=std_logic lab=qn}
C {devices/lab_pin.sym} 400 60 0 0 {name=l10 sig_type=std_logic lab=qp}
C {devices/lab_pin.sym} 440 90 2 0 {name=l11 sig_type=std_logic lab=eh}
C {devices/lab_pin.sym} 440 60 2 0 {name=l12 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 580 60 0 0 {name=Qh2 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 600 30 2 0 {name=l13 sig_type=std_logic lab=qp}
C {devices/lab_pin.sym} 560 60 0 0 {name=l14 sig_type=std_logic lab=qn}
C {devices/lab_pin.sym} 600 90 2 0 {name=l15 sig_type=std_logic lab=eh}
C {devices/lab_pin.sym} 600 60 2 0 {name=l16 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 100 190 0 0 {name=Qts model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 160 2 0 {name=l17 sig_type=std_logic lab=es}
C {devices/lab_pin.sym} 80 190 0 0 {name=l18 sig_type=std_logic lab=clkp}
C {devices/lab_pin.sym} 120 220 2 0 {name=l19 sig_type=std_logic lab=ets}
C {devices/lab_pin.sym} 120 190 2 0 {name=l20 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 420 190 0 0 {name=Qth model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 440 160 2 0 {name=l21 sig_type=std_logic lab=eh}
C {devices/lab_pin.sym} 400 190 0 0 {name=l22 sig_type=std_logic lab=clkn}
C {devices/lab_pin.sym} 440 220 2 0 {name=l23 sig_type=std_logic lab=eth}
C {devices/lab_pin.sym} 440 190 2 0 {name=l24 sig_type=std_logic lab=vss}
C {devices/res.sym} 260 190 0 0 {name=Rts value=40 m=1}
C {devices/lab_pin.sym} 260 160 0 0 {name=l25 sig_type=std_logic lab=ets}
C {devices/lab_pin.sym} 260 220 0 0 {name=l26 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 190 0 0 {name=Rth value=40 m=1}
C {devices/lab_pin.sym} 580 160 0 0 {name=l27 sig_type=std_logic lab=eth}
C {devices/lab_pin.sym} 580 220 0 0 {name=l28 sig_type=std_logic lab=vss}
C {devices/res.sym} 740 60 0 0 {name=RLp value=100 m=1}
C {devices/lab_pin.sym} 740 30 0 0 {name=l29 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 90 0 0 {name=l30 sig_type=std_logic lab=qp}
C {devices/res.sym} 900 60 0 0 {name=RLn value=100 m=1}
C {devices/lab_pin.sym} 900 30 0 0 {name=l31 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 900 90 0 0 {name=l32 sig_type=std_logic lab=qn}
