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
Bclk_xclk_qi1a_vbe_node clk_xclk_qi1a_vbe_node 0 V=v(xclk.ti1)-v(ck0)
Bclk_xclk_qi1b_vbe_node clk_xclk_qi1b_vbe_node 0 V=v(xclk.ti1)-v(ck180)
Bclk_xclk_qi2a_vbe_node clk_xclk_qi2a_vbe_node 0 V=v(xclk.ti2)-v(xclk.min)
Bclk_xclk_qi2b_vbe_node clk_xclk_qi2b_vbe_node 0 V=v(xclk.ti2)-v(xclk.mip)
Bclk_xclk_qq1a_vbe_node clk_xclk_qq1a_vbe_node 0 V=v(xclk.tq1)-v(ck90)
Bclk_xclk_qq1b_vbe_node clk_xclk_qq1b_vbe_node 0 V=v(xclk.tq1)-v(ck270)
Bclk_xclk_qq2a_vbe_node clk_xclk_qq2a_vbe_node 0 V=v(xclk.tq2)-v(xclk.mqn)
Bclk_xclk_qq2b_vbe_node clk_xclk_qq2b_vbe_node 0 V=v(xclk.tq2)-v(xclk.mqp)
Blatch_xl_qs1_vbe_node latch_xl_qs1_vbe_node 0 V=v(xl.es)-v(dp)
Blatch_xl_qs2_vbe_node latch_xl_qs2_vbe_node 0 V=v(xl.es)-v(dn)
Blatch_xl_qh1_vbe_node latch_xl_qh1_vbe_node 0 V=v(xl.eh)-v(qp)
Blatch_xl_qh2_vbe_node latch_xl_qh2_vbe_node 0 V=v(xl.eh)-v(qn)
Blatch_xl_qts_vbe_node latch_xl_qts_vbe_node 0 V=v(xl.ets)-v(b0)
Blatch_xl_qth_vbe_node latch_xl_qth_vbe_node 0 V=v(xl.eth)-v(b180)
