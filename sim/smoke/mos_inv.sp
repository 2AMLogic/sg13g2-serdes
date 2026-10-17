* SMOKE (toolchain bring-up, issue #3): SG13G2 LV CMOS inverter, DC transfer.
* Device sizes are PLACEHOLDERS to prove the PSP103 OSDI models load at each
* MOS corner. They are NOT design choices and carry no spec value.
* Circuit body only: klt sim supplies .lib / .control / .end.
Vdd vdd 0 dc 1.2
Vin in 0 dc 0
XMP out in vdd vdd sg13_lv_pmos w=1.0u l=0.13u ng=1 m=1
XMN out in 0 0 sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
