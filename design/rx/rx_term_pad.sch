v {xschem version=3.4.6 file_version=1.2
* rx_term_pad: 100 ohm differential termination, pad capacitance placeholder and
* the smallest PDK ESD clamp pair on each pad (DR-001, spec R9/R18/R19).
* Resistors are ideal (PDK rsil/rppd are OSDI models, not simulable today).
* Termination is 2 x 50 ohm to the vcm pin (bias supplied from outside this cell).
* Cpad_* are PLACEHOLDER capacitances (the PDK bondpad model is empty): layout
* and extraction (#24) replace them. Nothing here is a measured value.
}
G {}
K {}
V {}
S {}
E {}
C {devices/iopin.sym} -120 -200 0 0 {name=p1 lab=padp}
C {devices/iopin.sym} -120 -180 0 0 {name=p2 lab=padn}
C {devices/iopin.sym} -120 -160 0 0 {name=p3 lab=vcm}
C {devices/iopin.sym} -120 -140 0 0 {name=p4 lab=vdd}
C {devices/iopin.sym} -120 -120 0 0 {name=p5 lab=vss}
C {devices/iopin.sym} -120 -100 0 0 {name=p6 lab=inp}
C {devices/iopin.sym} -120 -80 0 0 {name=p7 lab=inn}
C {devices/res.sym} 100 60 0 0 {name=Rtp value=50 m=1}
C {devices/lab_pin.sym} 100 30 0 0 {name=l1 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 100 90 0 0 {name=l2 sig_type=std_logic lab=vcm}
C {devices/res.sym} 260 60 0 0 {name=Rtn value=50 m=1}
C {devices/lab_pin.sym} 260 30 0 0 {name=l3 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 260 90 0 0 {name=l4 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 420 60 0 0 {name=Cpad_p m=1 value=50f}
C {devices/lab_pin.sym} 420 30 0 0 {name=l5 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 420 90 0 0 {name=l6 sig_type=std_logic lab=vss}
C {devices/capa.sym} 580 60 0 0 {name=Cpad_n m=1 value=50f}
C {devices/lab_pin.sym} 580 30 0 0 {name=l7 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 580 90 0 0 {name=l8 sig_type=std_logic lab=vss}
C {sg13g2_pr/diodevdd_2kv.sym} 100 190 0 0 {name=Desd_pu model=diodevdd_2kv m=1 spiceprefix=X}
C {devices/lab_pin.sym} 100 160 0 0 {name=l9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 100 220 0 0 {name=l10 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 70 190 0 0 {name=l11 sig_type=std_logic lab=vss}
C {sg13g2_pr/diodevss_2kv.sym} 260 190 0 0 {name=Desd_pd model=diodevss_2kv m=1 spiceprefix=X}
C {devices/lab_pin.sym} 230 190 0 0 {name=l12 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 260 160 0 0 {name=l13 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 260 220 0 0 {name=l14 sig_type=std_logic lab=vss}
C {sg13g2_pr/diodevdd_2kv.sym} 420 190 0 0 {name=Desd_nu model=diodevdd_2kv m=1 spiceprefix=X}
C {devices/lab_pin.sym} 420 160 0 0 {name=l15 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 420 220 0 0 {name=l16 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 390 190 0 0 {name=l17 sig_type=std_logic lab=vss}
C {sg13g2_pr/diodevss_2kv.sym} 580 190 0 0 {name=Desd_nd model=diodevss_2kv m=1 spiceprefix=X}
C {devices/lab_pin.sym} 550 190 0 0 {name=l18 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 580 160 0 0 {name=l19 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 580 220 0 0 {name=l20 sig_type=std_logic lab=vss}
C {devices/res.sym} 100 320 0 0 {name=Rsp value=4 m=1}
C {devices/lab_pin.sym} 100 290 0 0 {name=l21 sig_type=std_logic lab=padp}
C {devices/lab_pin.sym} 100 350 0 0 {name=l22 sig_type=std_logic lab=inp}
C {devices/res.sym} 260 320 0 0 {name=Rsn value=4 m=1}
C {devices/lab_pin.sym} 260 290 0 0 {name=l23 sig_type=std_logic lab=padn}
C {devices/lab_pin.sym} 260 350 0 0 {name=l24 sig_type=std_logic lab=inn}
