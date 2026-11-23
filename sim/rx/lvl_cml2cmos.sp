* lvl_cml2cmos sizing bench, driven by the latch it loads in rx_top (issue #241,
* evidence gate G3). SIZING EVIDENCE, not a spec result.
* Stimulus and rate: the latch_regen bench below (ideal 5 GHz four-phase clock,
* +-10 mV data), so qp/qn carries the 1010 stream of a 5 Gb/s per-wire sampler
* output (200 ps per bit) at the latch's own swing and common mode. One
* lvl_cml2cmos sits on qp/qn as Xlvl_d0 does in design/rx/rx_top.spice;
* Xlvl_d180, Xlvl_e90 and Xlvl_e270 are the same cell on equivalent latch outputs.
* Load on d0: 20f to ground (assumption: the CMOS deserializer behind it does not
* exist yet). The converter supply goes through the 0 V source Vddc so its current
* is read alone. Threshold nodes: vdd/2 (on), 90 % (n90) and 10 % (n10) of vdd.
* Latch + clock-buffer sizing bench (issue #22). Sizing evidence, not a spec result.
* Ideal 5 GHz clock source (the SG13G2 clock candidates do not meet R20, see
* spec/clock-requirement.md): common mode 0.8333 vdd, +-150 mV per phase, ideal
* quadrature and 50 % duty. Data: +-10 mV differential toggling every 200 ps
* inside the hold phase, common mode 0.8167 vdd (the CTLE output common mode).
.include ../../design/rx/netlists/latch_cml.spice
.include ../../design/rx/netlists/clk_buf_quad.spice
Vdd vdd 0 1.2
Bck0 ck0 0 V=0.8333*v(vdd)+0.15*sin(2*3.14159265*5e9*time+0*3.14159265/180)
Bck180 ck180 0 V=0.8333*v(vdd)+0.15*sin(2*3.14159265*5e9*time+180*3.14159265/180)
Bck90 ck90 0 V=0.8333*v(vdd)+0.15*sin(2*3.14159265*5e9*time+90*3.14159265/180)
Bck270 ck270 0 V=0.8333*v(vdd)+0.15*sin(2*3.14159265*5e9*time+270*3.14159265/180)
Xclk ck0 ck180 ck90 ck270 vdd 0 b0 b180 b90 b270 clk_buf_quad
Cb0 b0 0 20f
Cb1 b180 0 20f
Cb2 b90 0 20f
Cb3 b270 0 20f
Bdcm dcm 0 V=0.8167*v(vdd)
Vdp dp dcm pulse(-0.01 0.01 250p 20p 20p 180p 400p)
Vdn dn dcm pulse(0.01 -0.01 250p 20p 20p 180p 400p)
Xl dp dn b0 b180 vdd 0 qp qn latch_cml
Bck ck 0 V=v(b0)-v(b180)
Bq q 0 V=v(qp)-v(qn)
.include ../../design/rx/netlists/lvl_cml2cmos.spice
Vddc vdd cdd dc 0
Xlvl qp qn cdd 0 d0 lvl_cml2cmos
Cd0 d0 0 20f
Bon on 0 V=v(d0)-0.5*v(vdd)
Bn90 n90 0 V=v(d0)-0.9*v(vdd)
Bn10 n10 0 V=v(d0)-0.1*v(vdd)
