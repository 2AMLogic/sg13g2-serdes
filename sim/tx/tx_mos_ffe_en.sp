* TX ffe_en sizing bench (issue #80). SIZING EVIDENCE, not a spec result.
* Enable codes step through 000, 001, 011, 111 (en0 first), 10 ns each; vbn comes from the
* real bias cell. vbp0..2 are unloaded (tail-base current ignored).
* Circuit body only: klt sim supplies .lib / .control / .end.
Vdd vdd 0 dc 1.2
.subckt bias vdd vss vbn
*.iopin vdd
*.iopin vss
*.iopin vbn
XRref vdd vbn vss rsil w=4u l=114.3u m=1 b=0
XQref vbn vbn er vss npn13G2 Nx=1
XRer er vss vss rsil w=4u l=36.57u m=1 b=0
XCvbn vbn vss cap_cmim w=7u l=7u m=1
.ends

.subckt ffe_en vdd vss vbn en0 en1 en2 vbp0 vbp1 vbp2
*.iopin vdd
*.iopin vss
*.iopin vbn
*.iopin en0
*.iopin en1
*.iopin en2
*.iopin vbp0
*.iopin vbp1
*.iopin vbp2
XMPi0 enb0 en0 vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1
XMNi0 enb0 en0 vss vss sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
XRb0 vbn vbp0 vss rsil w=2u l=285.7u m=1 b=0
XMNd0 vbp0 enb0 vss vss sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XMPi1 enb1 en1 vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1
XMNi1 enb1 en1 vss vss sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
XRb1 vbn vbp1 vss rsil w=2u l=285.7u m=1 b=0
XMNd1 vbp1 enb1 vss vss sg13_lv_nmos w=2u l=0.13u ng=1 m=1
XMPi2 enb2 en2 vdd vdd sg13_lv_pmos w=1u l=0.13u ng=1 m=1
XMNi2 enb2 en2 vss vss sg13_lv_nmos w=0.5u l=0.13u ng=1 m=1
XRb2 vbn vbp2 vss rsil w=2u l=285.7u m=1 b=0
XMNd2 vbp2 enb2 vss vss sg13_lv_nmos w=2u l=0.13u ng=1 m=1
.ends

Ven0u en0u 0 pwl(0 0 1e-08 0 1.002e-08 1 4e-08 1)
Ben0 en0 0 V='v(en0u)*v(vdd)'
Ven1u en1u 0 pwl(0 0 2e-08 0 2.002e-08 1 4e-08 1)
Ben1 en1 0 V='v(en1u)*v(vdd)'
Ven2u en2u 0 pwl(0 0 3e-08 0 3.002e-08 1 4e-08 1)
Ben2 en2 0 V='v(en2u)*v(vdd)'
Xbias vdd 0 vbn bias
Xffe vdd 0 vbn en0 en1 en2 vbp0 vbp1 vbp2 ffe_en
.ic v(vbn)=0.9
