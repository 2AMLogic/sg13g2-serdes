* Termination + pad first-look bench (issue #22). PLACEHOLDER pad capacitance
* (Cpad in rx_term_pad), ideal resistors, ESD from the PDK diode models, the CTLE
* (code 0) hanging on the pad. NOT a return-loss result: R9 SDD11 is graded on
* extracted layout in #24/#28. Only |Zdiff| at low frequency and at 5 GHz.
.include ../../design/rx/netlists/rx_term_pad.spice
.include ../../design/rx/netlists/ctle.spice
Vdd vdd 0 1.2
Bvcm vcm 0 V=0.7917*v(vdd)
Vip padp vcm dc 0 ac 0.5
Vin padn vcm dc 0 ac -0.5
Xpad padp padn vcm vdd 0 inp inn rx_term_pad
Xc inp inn vcm vdd 0 kl klb kl klb kl klb op on ctle
Bkl kl 0 V=v(vdd)-0.25
Bklb klb 0 V=v(vdd)
Clp op 0 80f
Cln on 0 80f
