v {xschem version=3.4.6 file_version=1.2
* rx_top: RX high-speed path (DR-001): termination/pad -> CTLE -> four CML
* sampling latches (data 0/180 deg, edge 90/270 deg, Alexander bang-bang) with
* the 5 GHz clock buffers, then latch-to-CMOS conversion. Bias generation (vcm,
* control levels) and the clock source are NOT in this cell. Sizing choice, not
* a result.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=padp}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=padn}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=vcm}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=ck0}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=ck180}
C {devices/iopin.sym} -120 -100 0 0 {name=p6 lab=ck90}
C {devices/iopin.sym} -120 -80 0 0 {name=p7 lab=ck270}
C {devices/iopin.sym} -120 -60 0 0 {name=p8 lab=c0}
C {devices/iopin.sym} -120 -40 0 0 {name=p9 lab=c0b}
C {devices/iopin.sym} -120 -20 0 0 {name=p10 lab=c1}
C {devices/iopin.sym} -120 0 0 0 {name=p11 lab=c1b}
C {devices/iopin.sym} -120 20 0 0 {name=p12 lab=c2}
C {devices/iopin.sym} -120 40 0 0 {name=p13 lab=c2b}
C {devices/iopin.sym} -120 60 0 0 {name=p14 lab=vdd}
C {devices/iopin.sym} -120 80 0 0 {name=p15 lab=vss}
C {devices/iopin.sym} -120 100 0 0 {name=p16 lab=d0}
C {devices/iopin.sym} -120 120 0 0 {name=p17 lab=d180}
C {devices/iopin.sym} -120 140 0 0 {name=p18 lab=e90}
C {devices/iopin.sym} -120 160 0 0 {name=p19 lab=e270}
C {rx_term_pad.sym} 100 60 0 0 {name=Xpad}
C {devices/lab_pin.sym} 70 20 0 0 {name=l1 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 70 40 0 0 {name=l2 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 70 60 0 0 {name=l3 sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 70 80 0 0 {name=l4 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 70 100 0 0 {name=l5 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 130 20 2 0 {name=l6 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 130 40 2 0 {name=l7 sig_type=std_logic lab=inn}
C {ctle.sym} 400 60 0 0 {name=Xctle}
C {devices/lab_pin.sym} 370 -40 0 0 {name=l8 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 370 -20 0 0 {name=l9 sig_type=std_logic lab=inn}
C {devices/lab_pin.sym} 370 0 0 0 {name=l10 sig_type=std_logic lab=vcm}
C {devices/lab_pin.sym} 370 20 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 370 40 0 0 {name=l12 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 370 60 0 0 {name=l13 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 370 80 0 0 {name=l14 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 370 100 0 0 {name=l15 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 370 120 0 0 {name=l16 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 370 140 0 0 {name=l17 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 370 160 0 0 {name=l18 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 430 -40 2 0 {name=l19 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 430 -20 2 0 {name=l20 sig_type=std_logic lab=dn}
C {clk_buf_quad.sym} 700 60 0 0 {name=Xclk}
C {devices/lab_pin.sym} 670 10 0 0 {name=l21 sig_type=std_logic lab=ck0}
C {devices/lab_pin.sym} 670 30 0 0 {name=l22 sig_type=std_logic lab=ck180}
C {devices/lab_pin.sym} 670 50 0 0 {name=l23 sig_type=std_logic lab=ck90}
C {devices/lab_pin.sym} 670 70 0 0 {name=l24 sig_type=std_logic lab=ck270}
C {devices/lab_pin.sym} 670 90 0 0 {name=l25 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 670 110 0 0 {name=l26 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 730 10 2 0 {name=l27 sig_type=std_logic lab=b0}
C {devices/lab_pin.sym} 730 30 2 0 {name=l28 sig_type=std_logic lab=b180}
C {devices/lab_pin.sym} 730 50 2 0 {name=l29 sig_type=std_logic lab=b90}
C {devices/lab_pin.sym} 730 70 2 0 {name=l30 sig_type=std_logic lab=b270}
C {latch_cml.sym} 100 460 0 0 {name=Xlat_d0}
C {devices/lab_pin.sym} 70 410 0 0 {name=l31 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 70 430 0 0 {name=l32 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 70 450 0 0 {name=l33 sig_type=std_logic lab=b0}
C {devices/lab_pin.sym} 70 470 0 0 {name=l34 sig_type=std_logic lab=b180}
C {devices/lab_pin.sym} 70 490 0 0 {name=l35 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 70 510 0 0 {name=l36 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 130 410 2 0 {name=l37 sig_type=std_logic lab=qp_d0}
C {devices/lab_pin.sym} 130 430 2 0 {name=l38 sig_type=std_logic lab=qn_d0}
C {lvl_cml2cmos.sym} 100 860 0 0 {name=Xlvl_d0}
C {devices/lab_pin.sym} 70 830 0 0 {name=l39 sig_type=std_logic lab=qp_d0}
C {devices/lab_pin.sym} 70 850 0 0 {name=l40 sig_type=std_logic lab=qn_d0}
C {devices/lab_pin.sym} 70 870 0 0 {name=l41 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 70 890 0 0 {name=l42 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 130 830 2 0 {name=l43 sig_type=std_logic lab=d0}
C {latch_cml.sym} 400 460 0 0 {name=Xlat_d180}
C {devices/lab_pin.sym} 370 410 0 0 {name=l44 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 370 430 0 0 {name=l45 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 370 450 0 0 {name=l46 sig_type=std_logic lab=b180}
C {devices/lab_pin.sym} 370 470 0 0 {name=l47 sig_type=std_logic lab=b0}
C {devices/lab_pin.sym} 370 490 0 0 {name=l48 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 370 510 0 0 {name=l49 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 430 410 2 0 {name=l50 sig_type=std_logic lab=qp_d180}
C {devices/lab_pin.sym} 430 430 2 0 {name=l51 sig_type=std_logic lab=qn_d180}
C {lvl_cml2cmos.sym} 400 860 0 0 {name=Xlvl_d180}
C {devices/lab_pin.sym} 370 830 0 0 {name=l52 sig_type=std_logic lab=qp_d180}
C {devices/lab_pin.sym} 370 850 0 0 {name=l53 sig_type=std_logic lab=qn_d180}
C {devices/lab_pin.sym} 370 870 0 0 {name=l54 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 370 890 0 0 {name=l55 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 430 830 2 0 {name=l56 sig_type=std_logic lab=d180}
C {latch_cml.sym} 700 460 0 0 {name=Xlat_e90}
C {devices/lab_pin.sym} 670 410 0 0 {name=l57 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 670 430 0 0 {name=l58 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 670 450 0 0 {name=l59 sig_type=std_logic lab=b90}
C {devices/lab_pin.sym} 670 470 0 0 {name=l60 sig_type=std_logic lab=b270}
C {devices/lab_pin.sym} 670 490 0 0 {name=l61 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 670 510 0 0 {name=l62 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 730 410 2 0 {name=l63 sig_type=std_logic lab=qp_e90}
C {devices/lab_pin.sym} 730 430 2 0 {name=l64 sig_type=std_logic lab=qn_e90}
C {lvl_cml2cmos.sym} 700 860 0 0 {name=Xlvl_e90}
C {devices/lab_pin.sym} 670 830 0 0 {name=l65 sig_type=std_logic lab=qp_e90}
C {devices/lab_pin.sym} 670 850 0 0 {name=l66 sig_type=std_logic lab=qn_e90}
C {devices/lab_pin.sym} 670 870 0 0 {name=l67 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 670 890 0 0 {name=l68 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 730 830 2 0 {name=l69 sig_type=std_logic lab=e90}
C {latch_cml.sym} 1000 460 0 0 {name=Xlat_e270}
C {devices/lab_pin.sym} 970 410 0 0 {name=l70 sig_type=std_logic lab=dp}
C {devices/lab_pin.sym} 970 430 0 0 {name=l71 sig_type=std_logic lab=dn}
C {devices/lab_pin.sym} 970 450 0 0 {name=l72 sig_type=std_logic lab=b270}
C {devices/lab_pin.sym} 970 470 0 0 {name=l73 sig_type=std_logic lab=b90}
C {devices/lab_pin.sym} 970 490 0 0 {name=l74 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 970 510 0 0 {name=l75 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1030 410 2 0 {name=l76 sig_type=std_logic lab=qp_e270}
C {devices/lab_pin.sym} 1030 430 2 0 {name=l77 sig_type=std_logic lab=qn_e270}
C {lvl_cml2cmos.sym} 1000 860 0 0 {name=Xlvl_e270}
C {devices/lab_pin.sym} 970 830 0 0 {name=l78 sig_type=std_logic lab=qp_e270}
C {devices/lab_pin.sym} 970 850 0 0 {name=l79 sig_type=std_logic lab=qn_e270}
C {devices/lab_pin.sym} 970 870 0 0 {name=l80 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 970 890 0 0 {name=l81 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1030 830 2 0 {name=l82 sig_type=std_logic lab=e270}
