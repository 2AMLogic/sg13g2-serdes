v {xschem version=3.4.6 file_version=1.2
* lvl_cml2cmos: latch-to-CMOS conversion. NMOS differential pair with PMOS
* mirror load, then two inverters. Thin-oxide MOS only (spec R3). The PDK MOS
* models need OSDI, which the batch fleet cannot stage today (see sim/README.md),
* so this cell is NOT simulated in this change.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=ip}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=in}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=vdd}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=vss}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=op}
C {sg13g2_pr/sg13_lv_nmos.sym} 100 60 0 0 {name=Mn1 l=0.13u w=4u ng=1 m=1 model=sg13_lv_nmos spiceprefix=X}
C {devices/lab_pin.sym} 120 30 2 0 {name=l1 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 80 60 0 0 {name=l2 sig_type=std_logic lab=ip}
C {devices/lab_pin.sym} 120 90 2 0 {name=l3 sig_type=std_logic lab=tl}
C {devices/lab_pin.sym} 120 60 2 0 {name=l4 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_lv_nmos.sym} 260 60 0 0 {name=Mn2 l=0.13u w=4u ng=1 m=1 model=sg13_lv_nmos spiceprefix=X}
C {devices/lab_pin.sym} 280 30 2 0 {name=l5 sig_type=std_logic lab=y}
C {devices/lab_pin.sym} 240 60 0 0 {name=l6 sig_type=std_logic lab=in}
C {devices/lab_pin.sym} 280 90 2 0 {name=l7 sig_type=std_logic lab=tl}
C {devices/lab_pin.sym} 280 60 2 0 {name=l8 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_lv_nmos.sym} 420 60 0 0 {name=Mnt l=0.5u w=2u ng=1 m=1 model=sg13_lv_nmos spiceprefix=X}
C {devices/lab_pin.sym} 440 30 2 0 {name=l9 sig_type=std_logic lab=tl}
C {devices/lab_pin.sym} 400 60 0 0 {name=l10 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 440 90 2 0 {name=l11 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 440 60 2 0 {name=l12 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_lv_pmos.sym} 100 190 0 0 {name=Mp1 l=0.13u w=4u ng=1 m=1 model=sg13_lv_pmos spiceprefix=X}
C {devices/lab_pin.sym} 120 220 2 0 {name=l13 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 80 190 0 0 {name=l14 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 120 160 2 0 {name=l15 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 120 190 2 0 {name=l16 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_lv_pmos.sym} 260 190 0 0 {name=Mp2 l=0.13u w=4u ng=1 m=1 model=sg13_lv_pmos spiceprefix=X}
C {devices/lab_pin.sym} 280 220 2 0 {name=l17 sig_type=std_logic lab=y}
C {devices/lab_pin.sym} 240 190 0 0 {name=l18 sig_type=std_logic lab=x}
C {devices/lab_pin.sym} 280 160 2 0 {name=l19 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 280 190 2 0 {name=l20 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_lv_pmos.sym} 100 320 0 0 {name=Mpi1 l=0.13u w=2u ng=1 m=1 model=sg13_lv_pmos spiceprefix=X}
C {devices/lab_pin.sym} 120 350 2 0 {name=l21 sig_type=std_logic lab=z}
C {devices/lab_pin.sym} 80 320 0 0 {name=l22 sig_type=std_logic lab=y}
C {devices/lab_pin.sym} 120 290 2 0 {name=l23 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 120 320 2 0 {name=l24 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_lv_nmos.sym} 260 320 0 0 {name=Mni1 l=0.13u w=1u ng=1 m=1 model=sg13_lv_nmos spiceprefix=X}
C {devices/lab_pin.sym} 280 290 2 0 {name=l25 sig_type=std_logic lab=z}
C {devices/lab_pin.sym} 240 320 0 0 {name=l26 sig_type=std_logic lab=y}
C {devices/lab_pin.sym} 280 350 2 0 {name=l27 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 280 320 2 0 {name=l28 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 320 0 0 {name=Mpi2 l=0.13u w=4u ng=1 m=1 model=sg13_lv_pmos spiceprefix=X}
C {devices/lab_pin.sym} 440 350 2 0 {name=l29 sig_type=std_logic lab=op}
C {devices/lab_pin.sym} 400 320 0 0 {name=l30 sig_type=std_logic lab=z}
C {devices/lab_pin.sym} 440 290 2 0 {name=l31 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 440 320 2 0 {name=l32 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_lv_nmos.sym} 580 320 0 0 {name=Mni2 l=0.13u w=2u ng=1 m=1 model=sg13_lv_nmos spiceprefix=X}
C {devices/lab_pin.sym} 600 290 2 0 {name=l33 sig_type=std_logic lab=op}
C {devices/lab_pin.sym} 560 320 0 0 {name=l34 sig_type=std_logic lab=z}
C {devices/lab_pin.sym} 600 350 2 0 {name=l35 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 600 320 2 0 {name=l36 sig_type=std_logic lab=vss}
