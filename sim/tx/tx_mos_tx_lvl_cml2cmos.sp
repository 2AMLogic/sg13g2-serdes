* TX tx_lvl_cml2cmos sizing bench (issue #80). SIZING EVIDENCE, not a spec result.
* Input: ideal complementary 2.5 GHz (first divided clock), vdd-referenced CML levels,
* 300 mV single-ended (high = vdd, low = vdd-0.3). Load: 20 fF on the CMOS output.
* Circuit body only: klt sim supplies .lib / .control / .end.
Vdd vdd 0 dc 1.2
.subckt tx_lvl_cml2cmos vdd vss inp inn out
*.iopin vdd
*.iopin vss
*.iopin inp
*.iopin inn
*.iopin out
XMN1 d1 inp s vss sg13_lv_nmos w=8u l=0.13u ng=2 m=1
XMN2 o1 inn s vss sg13_lv_nmos w=8u l=0.13u ng=2 m=1
XMP1 d1 d1 vdd vdd sg13_lv_pmos w=8u l=0.13u ng=2 m=1
XMP2 o1 d1 vdd vdd sg13_lv_pmos w=8u l=0.13u ng=2 m=1
XMNt s vbm vss vss sg13_lv_nmos w=8u l=0.13u ng=2 m=1
XMNb vbm vbm vss vss sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XRbm vdd vbm vss rppd w=0.5u l=19.23u m=1 b=0
XMP3 out o1 vdd vdd sg13_lv_pmos w=4u l=0.13u ng=1 m=1
XMN3 out o1 vss vss sg13_lv_nmos w=2u l=0.13u ng=1 m=1
.ends

Vq q 0 pulse(0 1 0 20p 20p 1.8e-10 4e-10)
Binp inp 0 V='v(vdd)-0.3*(1-v(q))'
Binn inn 0 V='v(vdd)-0.3*v(q)'
Xlvl vdd 0 inp inn out tx_lvl_cml2cmos
Cout out 0 20f
Bdin din 0 V='v(inp)-v(inn)'
Bon on 0 V='v(out)-0.5*v(vdd)'
