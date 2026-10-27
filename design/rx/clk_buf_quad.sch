v {xschem version=3.4.6 file_version=1.2
* clk_buf_quad: receiving CML buffers for the four clock phases (interface:
* spec/clock-requirement.md, R20: 5 GHz, 0/90/180/270 deg, duty +-1 %,
* quadrature +-2 deg). Two chains, each two stages: ck0/ck180 -> b0/b180 and
* ck90/ck270 -> b90/b270. The clock SOURCE is not designed here; no quadrature
* correction is attempted, the cell passes the source's phase error through.
* Output common mode is set low (about 0.75 V) to drive the latch tail bases.
* Sizing choice, not a result.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=ck0}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=ck180}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=ck90}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=ck270}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=vdd}
C {devices/iopin.sym} -120 -100 0 0 {name=p6 lab=vss}
C {devices/iopin.sym} -120 -80 0 0 {name=p7 lab=b0}
C {devices/iopin.sym} -120 -60 0 0 {name=p8 lab=b180}
C {devices/iopin.sym} -120 -40 0 0 {name=p9 lab=b90}
C {devices/iopin.sym} -120 -20 0 0 {name=p10 lab=b270}
C {sg13g2_pr/npn13G2.sym} 100 60 0 0 {name=Qi1a model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 30 2 0 {name=l1 sig_type=std_logic lab=min}
C {devices/lab_pin.sym} 80 60 0 0 {name=l2 sig_type=std_logic lab=ck0}
C {devices/lab_pin.sym} 120 90 2 0 {name=l3 sig_type=std_logic lab=ti1}
C {devices/lab_pin.sym} 120 60 2 0 {name=l4 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 60 0 0 {name=Qi1b model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 30 2 0 {name=l5 sig_type=std_logic lab=mip}
C {devices/lab_pin.sym} 240 60 0 0 {name=l6 sig_type=std_logic lab=ck180}
C {devices/lab_pin.sym} 280 90 2 0 {name=l7 sig_type=std_logic lab=ti1}
C {devices/lab_pin.sym} 280 60 2 0 {name=l8 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 60 0 0 {name=Rti1 value=85 m=1}
C {devices/lab_pin.sym} 420 30 0 0 {name=l9 sig_type=std_logic lab=ti1}
C {devices/lab_pin.sym} 420 90 0 0 {name=l10 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 60 0 0 {name=RLi1a value=100 m=1}
C {devices/lab_pin.sym} 580 30 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 580 90 0 0 {name=l12 sig_type=std_logic lab=min}
C {devices/res.sym} 740 60 0 0 {name=RLi1b value=100 m=1}
C {devices/lab_pin.sym} 740 30 0 0 {name=l13 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 90 0 0 {name=l14 sig_type=std_logic lab=mip}
C {sg13g2_pr/npn13G2.sym} 100 190 0 0 {name=Qi2a model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 160 2 0 {name=l15 sig_type=std_logic lab=b180}
C {devices/lab_pin.sym} 80 190 0 0 {name=l16 sig_type=std_logic lab=min}
C {devices/lab_pin.sym} 120 220 2 0 {name=l17 sig_type=std_logic lab=ti2}
C {devices/lab_pin.sym} 120 190 2 0 {name=l18 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 190 0 0 {name=Qi2b model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 160 2 0 {name=l19 sig_type=std_logic lab=b0}
C {devices/lab_pin.sym} 240 190 0 0 {name=l20 sig_type=std_logic lab=mip}
C {devices/lab_pin.sym} 280 220 2 0 {name=l21 sig_type=std_logic lab=ti2}
C {devices/lab_pin.sym} 280 190 2 0 {name=l22 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 190 0 0 {name=Rti2 value=85 m=1}
C {devices/lab_pin.sym} 420 160 0 0 {name=l23 sig_type=std_logic lab=ti2}
C {devices/lab_pin.sym} 420 220 0 0 {name=l24 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 190 0 0 {name=RLi2a value=225 m=1}
C {devices/lab_pin.sym} 580 160 0 0 {name=l25 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 580 220 0 0 {name=l26 sig_type=std_logic lab=b180}
C {devices/res.sym} 740 190 0 0 {name=RLi2b value=225 m=1}
C {devices/lab_pin.sym} 740 160 0 0 {name=l27 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 220 0 0 {name=l28 sig_type=std_logic lab=b0}
C {sg13g2_pr/npn13G2.sym} 100 320 0 0 {name=Qq1a model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 290 2 0 {name=l29 sig_type=std_logic lab=mqn}
C {devices/lab_pin.sym} 80 320 0 0 {name=l30 sig_type=std_logic lab=ck90}
C {devices/lab_pin.sym} 120 350 2 0 {name=l31 sig_type=std_logic lab=tq1}
C {devices/lab_pin.sym} 120 320 2 0 {name=l32 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 320 0 0 {name=Qq1b model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 290 2 0 {name=l33 sig_type=std_logic lab=mqp}
C {devices/lab_pin.sym} 240 320 0 0 {name=l34 sig_type=std_logic lab=ck270}
C {devices/lab_pin.sym} 280 350 2 0 {name=l35 sig_type=std_logic lab=tq1}
C {devices/lab_pin.sym} 280 320 2 0 {name=l36 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 320 0 0 {name=Rtq1 value=85 m=1}
C {devices/lab_pin.sym} 420 290 0 0 {name=l37 sig_type=std_logic lab=tq1}
C {devices/lab_pin.sym} 420 350 0 0 {name=l38 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 320 0 0 {name=RLq1a value=100 m=1}
C {devices/lab_pin.sym} 580 290 0 0 {name=l39 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 580 350 0 0 {name=l40 sig_type=std_logic lab=mqn}
C {devices/res.sym} 740 320 0 0 {name=RLq1b value=100 m=1}
C {devices/lab_pin.sym} 740 290 0 0 {name=l41 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 350 0 0 {name=l42 sig_type=std_logic lab=mqp}
C {sg13g2_pr/npn13G2.sym} 100 450 0 0 {name=Qq2a model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 120 420 2 0 {name=l43 sig_type=std_logic lab=b270}
C {devices/lab_pin.sym} 80 450 0 0 {name=l44 sig_type=std_logic lab=mqn}
C {devices/lab_pin.sym} 120 480 2 0 {name=l45 sig_type=std_logic lab=tq2}
C {devices/lab_pin.sym} 120 450 2 0 {name=l46 sig_type=std_logic lab=vss}
C {sg13g2_pr/npn13G2.sym} 260 450 0 0 {name=Qq2b model=npn13G2 spiceprefix=X Nx=2}
C {devices/lab_pin.sym} 280 420 2 0 {name=l47 sig_type=std_logic lab=b90}
C {devices/lab_pin.sym} 240 450 0 0 {name=l48 sig_type=std_logic lab=mqp}
C {devices/lab_pin.sym} 280 480 2 0 {name=l49 sig_type=std_logic lab=tq2}
C {devices/lab_pin.sym} 280 450 2 0 {name=l50 sig_type=std_logic lab=vss}
C {devices/res.sym} 420 450 0 0 {name=Rtq2 value=85 m=1}
C {devices/lab_pin.sym} 420 420 0 0 {name=l51 sig_type=std_logic lab=tq2}
C {devices/lab_pin.sym} 420 480 0 0 {name=l52 sig_type=std_logic lab=vss}
C {devices/res.sym} 580 450 0 0 {name=RLq2a value=225 m=1}
C {devices/lab_pin.sym} 580 420 0 0 {name=l53 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 580 480 0 0 {name=l54 sig_type=std_logic lab=b270}
C {devices/res.sym} 740 450 0 0 {name=RLq2b value=225 m=1}
C {devices/lab_pin.sym} 740 420 0 0 {name=l55 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 740 480 0 0 {name=l56 sig_type=std_logic lab=b90}
