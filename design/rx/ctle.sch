v {xschem version=3.4.6 file_version=1.2
* ctle: two parallel paths summed into RL. Path 1 is a flat HBT pair (always
* on). Path 2 is AC-coupled (MIM + bias resistor) and built from a fixed
* weight-7 cell plus binary cells of weight 1/2/4, each steered +/- onto the
* outputs by a switch pair driven from (cK, cKb). Peaking at HF relative to DC
* is 1 + 2*code*gu/g1 with code = c2c1c0 in 0..7, so 8 steps from 0 dB; total
* current, and so the output common mode, is the same for every code. HBT only
* (spec R3). Control inputs are differential levels (cK high = positive).
* Sizing choice, not a result.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=inp}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=inn}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=vcm}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=vdd}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=vss}
C {devices/iopin.sym} -120 -100 0 0 {name=p6 lab=c0}
C {devices/iopin.sym} -120 -80 0 0 {name=p7 lab=c0b}
C {devices/iopin.sym} -120 -60 0 0 {name=p8 lab=c1}
C {devices/iopin.sym} -120 -40 0 0 {name=p9 lab=c1b}
C {devices/iopin.sym} -120 -20 0 0 {name=p10 lab=c2}
C {devices/iopin.sym} -120 0 0 0 {name=p11 lab=c2b}
C {devices/iopin.sym} -120 20 0 0 {name=p12 lab=outp}
C {devices/iopin.sym} -120 40 0 0 {name=p13 lab=outn}
C {sg13g2_pr/npn13G2.sym} 100 60 0 0 {name=Q1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 30 2 0 {name=l1 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 80 60 0 0 {name=l2 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 120 90 2 0 {name=l3 sig_type=std_logic lab=e1}
C {devices/lab_pin.sym} 120 60 2 0 {name=l4 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 60 0 0 {name=Q2 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 30 2 0 {name=l5 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 240 60 0 0 {name=l6 sig_type=std_logic lab=inn}
C {devices/lab_pin.sym} 280 90 2 0 {name=l7 sig_type=std_logic lab=e2}
C {devices/lab_pin.sym} 280 60 2 0 {name=l8 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 60 0 0 {name=Rt1a value=220 m=1}
C {devices/lab_pin.sym} 420 30 0 0 {name=l9 sig_type=std_logic lab=e1}
C {devices/lab_pin.sym} 420 90 0 0 {name=l10 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 60 0 0 {name=Rt1b value=220 m=1}
C {devices/lab_pin.sym} 580 30 0 0 {name=l11 sig_type=std_logic lab=e2}
C {devices/lab_pin.sym} 580 90 0 0 {name=l12 sig_type=std_logic lab=vss}
C {devices/res.sym} 740 60 0 0 {name=RLa value=60 m=1}
C {devices/lab_pin.sym} 740 30 0 0 {name=l13 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 90 0 0 {name=l14 sig_type=std_logic lab=outn}
C {devices/res.sym} 900 60 0 0 {name=RLb value=60 m=1}
C {devices/lab_pin.sym} 900 30 0 0 {name=l15 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 900 90 0 0 {name=l16 sig_type=std_logic lab=outp}
C {sg13g2_pr/cap_cmim.sym} 100 190 0 0 {name=Cca model=cap_cmim w=10u l=10u m=1 spiceprefix=X}
C {devices/lab_pin.sym} 100 160 0 0 {name=l17 sig_type=std_logic lab=inp}
C {devices/lab_pin.sym} 100 220 0 0 {name=l18 sig_type=std_logic lab=hpp}
C {sg13g2_pr/cap_cmim.sym} 260 190 0 0 {name=Ccb model=cap_cmim w=10u l=10u m=1 spiceprefix=X}
C {devices/lab_pin.sym} 260 160 0 0 {name=l19 sig_type=std_logic lab=inn}
C {devices/lab_pin.sym} 260 220 0 0 {name=l20 sig_type=std_logic lab=hpn}
C {devices/res.sym} 420 190 0 0 {name=Rca value=2000 m=1}
C {devices/lab_pin.sym} 420 160 0 0 {name=l21 sig_type=std_logic lab=hpp}
C {devices/lab_pin.sym} 420 220 0 0 {name=l22 sig_type=std_logic lab=vcm}
C {devices/res.sym} 580 190 0 0 {name=Rcb value=2000 m=1}
C {devices/lab_pin.sym} 580 160 0 0 {name=l23 sig_type=std_logic lab=hpn}
C {devices/lab_pin.sym} 580 220 0 0 {name=l24 sig_type=std_logic lab=vcm}
C {sg13g2_pr/npn13G2.sym} 100 320 0 0 {name=Qfa model=npn13G2 spiceprefix=X Nx=7}
C {devices/lab_pin.sym} 120 290 2 0 {name=l25 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 80 320 0 0 {name=l26 sig_type=std_logic lab=hpp}
C {devices/lab_pin.sym} 120 350 2 0 {name=l27 sig_type=std_logic lab=efa}
C {devices/lab_pin.sym} 120 320 2 0 {name=l28 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 320 0 0 {name=Qfb model=npn13G2 spiceprefix=X Nx=7}
C {devices/lab_pin.sym} 280 290 2 0 {name=l29 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 240 320 0 0 {name=l30 sig_type=std_logic lab=hpn}
C {devices/lab_pin.sym} 280 350 2 0 {name=l31 sig_type=std_logic lab=efb}
C {devices/lab_pin.sym} 280 320 2 0 {name=l32 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 320 0 0 {name=Rfa value=62.86 m=1}
C {devices/lab_pin.sym} 420 290 0 0 {name=l33 sig_type=std_logic lab=efa}
C {devices/lab_pin.sym} 420 350 0 0 {name=l34 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 320 0 0 {name=Rfb value=62.86 m=1}
C {devices/lab_pin.sym} 580 290 0 0 {name=l35 sig_type=std_logic lab=efb}
C {devices/lab_pin.sym} 580 350 0 0 {name=l36 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 100 450 0 0 {name=Qa0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 120 420 2 0 {name=l37 sig_type=std_logic lab=ca0}
C {devices/lab_pin.sym} 80 450 0 0 {name=l38 sig_type=std_logic lab=hpp}
C {devices/lab_pin.sym} 120 480 2 0 {name=l39 sig_type=std_logic lab=ea0}
C {devices/lab_pin.sym} 120 450 2 0 {name=l40 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 450 0 0 {name=Qb0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 280 420 2 0 {name=l41 sig_type=std_logic lab=cb0}
C {devices/lab_pin.sym} 240 450 0 0 {name=l42 sig_type=std_logic lab=hpn}
C {devices/lab_pin.sym} 280 480 2 0 {name=l43 sig_type=std_logic lab=eb0}
C {devices/lab_pin.sym} 280 450 2 0 {name=l44 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 450 0 0 {name=Ra0 value=440 m=1}
C {devices/lab_pin.sym} 420 420 0 0 {name=l45 sig_type=std_logic lab=ea0}
C {devices/lab_pin.sym} 420 480 0 0 {name=l46 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 450 0 0 {name=Rb0 value=440 m=1}
C {devices/lab_pin.sym} 580 420 0 0 {name=l47 sig_type=std_logic lab=eb0}
C {devices/lab_pin.sym} 580 480 0 0 {name=l48 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 740 450 0 0 {name=Spa0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 760 420 2 0 {name=l49 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 720 450 0 0 {name=l50 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 760 480 2 0 {name=l51 sig_type=std_logic lab=ca0}
C {devices/lab_pin.sym} 760 450 2 0 {name=l52 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 900 450 0 0 {name=Sna0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 920 420 2 0 {name=l53 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 880 450 0 0 {name=l54 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 920 480 2 0 {name=l55 sig_type=std_logic lab=ca0}
C {devices/lab_pin.sym} 920 450 2 0 {name=l56 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1060 450 0 0 {name=Spb0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 1080 420 2 0 {name=l57 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 1040 450 0 0 {name=l58 sig_type=std_logic lab=c0}
C {devices/lab_pin.sym} 1080 480 2 0 {name=l59 sig_type=std_logic lab=cb0}
C {devices/lab_pin.sym} 1080 450 2 0 {name=l60 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1220 450 0 0 {name=Snb0 model=npn13G2 spiceprefix=X Nx=1}
C {devices/lab_pin.sym} 1240 420 2 0 {name=l61 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 1200 450 0 0 {name=l62 sig_type=std_logic lab=c0b}
C {devices/lab_pin.sym} 1240 480 2 0 {name=l63 sig_type=std_logic lab=cb0}
C {devices/lab_pin.sym} 1240 450 2 0 {name=l64 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 100 580 0 0 {name=Qa1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 550 2 0 {name=l65 sig_type=std_logic lab=ca1}
C {devices/lab_pin.sym} 80 580 0 0 {name=l66 sig_type=std_logic lab=hpp}
C {devices/lab_pin.sym} 120 610 2 0 {name=l67 sig_type=std_logic lab=ea1}
C {devices/lab_pin.sym} 120 580 2 0 {name=l68 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 580 0 0 {name=Qb1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 550 2 0 {name=l69 sig_type=std_logic lab=cb1}
C {devices/lab_pin.sym} 240 580 0 0 {name=l70 sig_type=std_logic lab=hpn}
C {devices/lab_pin.sym} 280 610 2 0 {name=l71 sig_type=std_logic lab=eb1}
C {devices/lab_pin.sym} 280 580 2 0 {name=l72 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 580 0 0 {name=Ra1 value=220 m=1}
C {devices/lab_pin.sym} 420 550 0 0 {name=l73 sig_type=std_logic lab=ea1}
C {devices/lab_pin.sym} 420 610 0 0 {name=l74 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 580 0 0 {name=Rb1 value=220 m=1}
C {devices/lab_pin.sym} 580 550 0 0 {name=l75 sig_type=std_logic lab=eb1}
C {devices/lab_pin.sym} 580 610 0 0 {name=l76 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 740 580 0 0 {name=Spa1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 760 550 2 0 {name=l77 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 720 580 0 0 {name=l78 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 760 610 2 0 {name=l79 sig_type=std_logic lab=ca1}
C {devices/lab_pin.sym} 760 580 2 0 {name=l80 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 900 580 0 0 {name=Sna1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 920 550 2 0 {name=l81 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 880 580 0 0 {name=l82 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 920 610 2 0 {name=l83 sig_type=std_logic lab=ca1}
C {devices/lab_pin.sym} 920 580 2 0 {name=l84 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1060 580 0 0 {name=Spb1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 1080 550 2 0 {name=l85 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 1040 580 0 0 {name=l86 sig_type=std_logic lab=c1}
C {devices/lab_pin.sym} 1080 610 2 0 {name=l87 sig_type=std_logic lab=cb1}
C {devices/lab_pin.sym} 1080 580 2 0 {name=l88 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1220 580 0 0 {name=Snb1 model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 1240 550 2 0 {name=l89 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 1200 580 0 0 {name=l90 sig_type=std_logic lab=c1b}
C {devices/lab_pin.sym} 1240 610 2 0 {name=l91 sig_type=std_logic lab=cb1}
C {devices/lab_pin.sym} 1240 580 2 0 {name=l92 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 100 710 0 0 {name=Qa2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 120 680 2 0 {name=l93 sig_type=std_logic lab=ca2}
C {devices/lab_pin.sym} 80 710 0 0 {name=l94 sig_type=std_logic lab=hpp}
C {devices/lab_pin.sym} 120 740 2 0 {name=l95 sig_type=std_logic lab=ea2}
C {devices/lab_pin.sym} 120 710 2 0 {name=l96 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 710 0 0 {name=Qb2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 280 680 2 0 {name=l97 sig_type=std_logic lab=cb2}
C {devices/lab_pin.sym} 240 710 0 0 {name=l98 sig_type=std_logic lab=hpn}
C {devices/lab_pin.sym} 280 740 2 0 {name=l99 sig_type=std_logic lab=eb2}
C {devices/lab_pin.sym} 280 710 2 0 {name=l100 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 710 0 0 {name=Ra2 value=110 m=1}
C {devices/lab_pin.sym} 420 680 0 0 {name=l101 sig_type=std_logic lab=ea2}
C {devices/lab_pin.sym} 420 740 0 0 {name=l102 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 710 0 0 {name=Rb2 value=110 m=1}
C {devices/lab_pin.sym} 580 680 0 0 {name=l103 sig_type=std_logic lab=eb2}
C {devices/lab_pin.sym} 580 740 0 0 {name=l104 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 740 710 0 0 {name=Spa2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 760 680 2 0 {name=l105 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 720 710 0 0 {name=l106 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 760 740 2 0 {name=l107 sig_type=std_logic lab=ca2}
C {devices/lab_pin.sym} 760 710 2 0 {name=l108 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 900 710 0 0 {name=Sna2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 920 680 2 0 {name=l109 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 880 710 0 0 {name=l110 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 920 740 2 0 {name=l111 sig_type=std_logic lab=ca2}
C {devices/lab_pin.sym} 920 710 2 0 {name=l112 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1060 710 0 0 {name=Spb2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 1080 680 2 0 {name=l113 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 1040 710 0 0 {name=l114 sig_type=std_logic lab=c2}
C {devices/lab_pin.sym} 1080 740 2 0 {name=l115 sig_type=std_logic lab=cb2}
C {devices/lab_pin.sym} 1080 710 2 0 {name=l116 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 1220 710 0 0 {name=Snb2 model=npn13G2 spiceprefix=X Nx=4}
C {devices/lab_pin.sym} 1240 680 2 0 {name=l117 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 1200 710 0 0 {name=l118 sig_type=std_logic lab=c2b}
C {devices/lab_pin.sym} 1240 740 2 0 {name=l119 sig_type=std_logic lab=cb2}
C {devices/lab_pin.sym} 1240 710 2 0 {name=l120 sig_type=std_logic lab=vss}
