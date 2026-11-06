* TX mux2to1_cml sizing bench (issue #80). SIZING EVIDENCE, not a spec result.
* Cells inlined from design/tx/netlists/ with the PDK's own MOS / rsil / rppd / cap_cmim.
* Clock: ideal complementary 5 GHz source, 0.4 V swing (AC-coupled into the squarers; an
* assumption, not a spec value). Data: A held 1, B held 0 (vdd-referenced CML, 300 mV), so
* the output alternates every half clock = a 1010 stream at 10 Gb/s.
* Load: predriver main input (as in the HBT bench) + 20 fF per predriver output.
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

.subckt predriver vdd vss inp inn vbn outp outn
*.iopin vdd
*.iopin vss
*.iopin inp
*.iopin inn
*.iopin vbn
*.iopin outp
*.iopin outn
XQ1 outn inp e vss npn13G2 Nx=4
XQ2 outp inn e vss npn13G2 Nx=4
XQt e vbn et vss npn13G2 Nx=4
XRe et vss vss rsil w=8u l=18.29u m=1 b=0
XRL1 vdd outp vss rsil w=8u l=68.57u m=1 b=0
XRL2 vdd outn vss rsil w=8u l=68.57u m=1 b=0
.ends

.subckt mux2to1_cml vdd vss ckp ckn dap dan dbp dbn outp outn
*.iopin vdd
*.iopin vss
*.iopin ckp
*.iopin ckn
*.iopin dap
*.iopin dan
*.iopin dbp
*.iopin dbn
*.iopin outp
*.iopin outn
XCca ckp nca cap_cmim w=7u l=7u m=1
XRfa mida nca vss rppd w=0.5u l=38.46u m=1 b=0
XMP1a mida nca vdd vdd sg13_lv_pmos w=8u l=0.13u ng=2 m=1
XMN1a mida nca vss vss sg13_lv_nmos w=4u l=0.13u ng=2 m=1
XMP2a sqa mida vdd vdd sg13_lv_pmos w=16u l=0.13u ng=4 m=1
XMN2a sqa mida vss vss sg13_lv_nmos w=8u l=0.13u ng=2 m=1
XCcb ckn ncb cap_cmim w=7u l=7u m=1
XRfb midb ncb vss rppd w=0.5u l=38.46u m=1 b=0
XMP1b midb ncb vdd vdd sg13_lv_pmos w=8u l=0.13u ng=2 m=1
XMN1b midb ncb vss vss sg13_lv_nmos w=4u l=0.13u ng=2 m=1
XMP2b sqb midb vdd vdd sg13_lv_pmos w=16u l=0.13u ng=4 m=1
XMN2b sqb midb vss vss sg13_lv_nmos w=8u l=0.13u ng=2 m=1
XQa1 outn dap ea vss npn13G2 Nx=2
XQa2 outp dan ea vss npn13G2 Nx=2
XMTa ea sqa sa vss sg13_lv_nmos w=20u l=0.13u ng=4 m=1
XRsa sa vss vss rsil w=8u l=68.57u m=1 b=0
XQb1 outn dbp eb vss npn13G2 Nx=2
XQb2 outp dbn eb vss npn13G2 Nx=2
XMTb eb sqb sb vss sg13_lv_nmos w=20u l=0.13u ng=4 m=1
XRsb sb vss vss rsil w=8u l=68.57u m=1 b=0
XRLp vdd outp vss rsil w=8u l=114.3u m=1 b=0
XRLn vdd outn vss rsil w=8u l=114.3u m=1 b=0
.ends

Vckp ckp 0 pulse(0.4 0.8 0 20p 20p 80p 2e-10)
Vckn ckn 0 pulse(0.8 0.4 0 20p 20p 80p 2e-10)
Bdap dap 0 V='v(vdd)'
Bdan dan 0 V='v(vdd)-0.3'
Bdbp dbp 0 V='v(vdd)-0.3'
Bdbn dbn 0 V='v(vdd)'
Xbias vdd 0 vbn bias
Xmux vdd 0 ckp ckn dap dan dbp dbn mp mn mux2to1_cml
Xprem vdd 0 mp mn vbn pp pn predriver
Cpp pp 0 20f
Cpn pn 0 20f
Bvd vd 0 V='v(mp)-v(mn)'
.ic v(vbn)=0.9 v(xmux.nca)=0.55 v(xmux.mida)=0.55 v(xmux.ncb)=0.55 v(xmux.midb)=0.55
