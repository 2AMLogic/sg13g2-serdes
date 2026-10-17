* SMOKE (toolchain bring-up, issue #3): transient with BOTH model families in one
* deck -- a PSP103 (OSDI) CMOS inverter driving a VBIC (built-in) HBT emitter
* follower. Topology and sizes are PLACEHOLDERS to prove transient analysis runs
* with both families loaded. They are NOT design choices and carry no spec value.
* Circuit body only: klt sim supplies .lib / .control / .end.
Vdd vdd 0 dc 1.2
Vin in 0 pulse(0 1.2 0.5n 50p 50p 1n 2n)
XMP out in vdd vdd sg13_lv_pmos w=1.0u l=0.13u ng=1 m=1
XMN out in 0 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
XQ vdd out ef 0 npn13G2
Rload ef 0 5k
Cload ef 0 20f
