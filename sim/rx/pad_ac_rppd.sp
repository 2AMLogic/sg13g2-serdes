* RX termination rppd corner bench (issue #240, R9 gate G1): the two ideal
* 50 ohm legs of design/rx/rx_term_pad are replaced by PDK rppd instances
* (w=2u, l=0.7715u, m=2 -> 49.998 ohm per side at rsh = 260); everything else
* is pad_ac as-is: PLACEHOLDER pad capacitance, ideal 4 ohm metal series
* stand-ins, ideal CTLE-internal resistors, code-0 CTLE hanging on the pad.
* NOT a return-loss result: R9 SDD11 is graded on extracted layout (#24/#28).
* Tolerance figures trace to spec/sources/rppd-tolerance-window.md (PDK
* process spec Rev. 1.2 p.11 vs cornerRES.lib; discrepancy reported, not
* reconciled). Sizing evidence from a simulation, never a measurement.
.include ../../design/rx/netlists/ctle.spice
XRtp padp vcm 0 rppd w=2u l=0.7715u m=2 b=0
XRtn padn vcm 0 rppd w=2u l=0.7715u m=2 b=0
Cpad_p padp 0 50f m=1
Cpad_n padn 0 50f m=1
XDesd_pu vdd padp 0 diodevdd_2kv m=1
XDesd_pd vdd padp 0 diodevss_2kv m=1
XDesd_nu vdd padn 0 diodevdd_2kv m=1
XDesd_nd vdd padn 0 diodevss_2kv m=1
Rsp padp inp 4 m=1
Rsn padn inn 4 m=1
Vdd vdd 0 1.2
Bvcm vcm 0 V=0.7917*v(vdd)
Vip padp vcm dc 0 ac 0.5
Vin padn vcm dc 0 ac -0.5
Xc inp inn vcm vdd 0 kl klb kl klb kl klb op on ctle
Bkl kl 0 V=v(vdd)-0.25
Bklb klb 0 V=v(vdd)
Clp op 0 80f
Cln on 0 80f
Hip iz 0 Vip 1
