# Comparison for issue #266: RX collector ceiling

Baseline: `20261123-102613-14d2158`; revised: `20261123-202156-f5860fa-vce`. Simulated sizing evidence, not measured.

## Worst collector-to-ground (R3 limit 1.32 V) and reverse Vbe (limit 1.0 V), 27 corners

| bench | quantity | baseline | revised |
|---|---|---|---|
| latch_regen | max vc_max | 1.3901 V (latch_xl_qs1_vc_max, hbt_bcs/1.320V/125C) | 1.3180 V (clk_xclk_qq1b_vc_max, hbt_bcs/1.320V/-40C) |
| latch_regen | max vbe_rev_max | -0.1783 V (latch_xl_qh1_vbe_rev_max, hbt_bcs/1.320V/125C) | -0.2624 V (latch_xl_qh1_vbe_rev_max, hbt_bcs/1.320V/125C) |
| ctle_op | max vc_max | 1.0447 V (ctle_c0_xd0_q1_vc_max, hbt_wcs/1.080V/-40C) | 1.0447 V (ctle_c0_xd0_q1_vc_max, hbt_wcs/1.080V/-40C) |
| ctle_op | max vbe_rev_max | -0.4720 V (ctle_c0_xd0_spa2_vbe_rev_max, hbt_bcs/1.080V/125C) | -0.4720 V (ctle_c0_xd0_spa2_vbe_rev_max, hbt_bcs/1.080V/125C) |
| ctle_tran | max vc_max | 1.3145 V (ctle_hi_c7_xdh7_q1_vc_max, hbt_wcs/1.320V/-40C) | 1.3145 V (ctle_hi_c7_xdh7_q1_vc_max, hbt_wcs/1.320V/-40C) |
| ctle_tran | max vbe_rev_max | -0.3335 V (ctle_hi_c0_xdh0_spa2_vbe_rev_max, hbt_wcs/1.080V/125C) | -0.3335 V (ctle_hi_c0_xdh0_spa2_vbe_rev_max, hbt_wcs/1.080V/125C) |
| ctle_tran | max vce_max | 1.3089 V (ctle_hi_c7_xdh7_qfa_vce_max, hbt_wcs/1.320V/-40C) | 1.3089 V (ctle_hi_c7_xdh7_qfa_vce_max, hbt_wcs/1.320V/-40C) |

Per-node worst `vc_max` in the revised latch_regen record (V):

- `clk_xclk_qq1b_vc_max` 1.3180 (hbt_bcs/1.320V/-40C)
- `clk_xclk_qi1b_vc_max` 1.3170 (hbt_bcs/1.320V/-40C)
- `clk_xclk_qi1a_vc_max` 1.3150 (hbt_bcs/1.320V/-40C)
- `clk_xclk_qq1a_vc_max` 1.3144 (hbt_wcs/1.320V/-40C)
- `clk_xclk_qq2a_vc_max` 1.3059 (hbt_bcs/1.320V/-40C)
- `clk_xclk_qq2b_vc_max` 1.3057 (hbt_bcs/1.320V/-40C)
- `latch_xl_qs1_vc_max` 1.3007 (hbt_wcs/1.320V/-40C)
- `latch_xl_qh1_vc_max` 1.3007 (hbt_wcs/1.320V/-40C)
- `latch_xl_qs2_vc_max` 1.2764 (hbt_wcs/1.320V/-40C)
- `latch_xl_qh2_vc_max` 1.2764 (hbt_wcs/1.320V/-40C)

## Latch regeneration time (ps), baseline -> revised; floor level 0.10 V, decision level 0.25 V

| corner | up_lo | dn_lo | up@0.25 | dn@0.25 | q max V |
|---|---|---|---|---|---|
| hbt_typ/1.080V/-40C | 10.6 -> 13.6 | 10.2 -> 13.2 | NR -> NR | NR -> NR | 0.176 -> 0.156 |
| hbt_typ/1.080V/27C | 8.6 -> 11.1 | 8.0 -> 10.5 | NR -> NR | NR -> NR | 0.222 -> 0.197 |
| hbt_typ/1.080V/125C | 8.1 -> 10.8 | 7.3 -> 9.8 | 71.4 -> 94.3 | 66.2 -> 93.9 | 0.286 -> 0.254 |
| hbt_typ/1.200V/-40C | 5.0 -> 6.0 | 4.7 -> 5.6 | 85.8 -> 93.5 | 84.5 -> 93.4 | 0.320 -> 0.284 |
| hbt_typ/1.200V/27C | 4.7 -> 5.8 | 4.2 -> 5.4 | 19.3 -> 44.7 | 18.5 -> 40.5 | 0.365 -> 0.324 |
| hbt_typ/1.200V/125C | 4.9 -> 6.3 | 4.4 -> 5.7 | 13.7 -> 17.0 | 13.1 -> 16.2 | 0.414 -> 0.368 |
| hbt_typ/1.320V/-40C | 3.6 -> 4.4 | 3.2 -> 4.0 | 13.4 -> 20.8 | 11.6 -> 20.3 | 0.458 -> 0.408 |
| hbt_typ/1.320V/27C | 3.6 -> 4.5 | 3.1 -> 4.0 | 11.4 -> 14.9 | 10.4 -> 14.5 | 0.500 -> 0.442 |
| hbt_typ/1.320V/125C | 3.8 -> 4.9 | 3.4 -> 4.4 | 10.1 -> 11.7 | 9.6 -> 11.2 | 0.514 -> 0.471 |
| hbt_bcs/1.080V/-40C | 6.9 -> 8.5 | 6.6 -> 8.3 | NR -> NR | NR -> NR | 0.206 -> 0.181 |
| hbt_bcs/1.080V/27C | 5.3 -> 6.9 | 5.0 -> 6.5 | 92.5 -> NR | 92.3 -> NR | 0.261 -> 0.229 |
| hbt_bcs/1.080V/125C | 4.6 -> 6.5 | 4.1 -> 5.9 | 18.3 -> 53.6 | 17.5 -> 48.6 | 0.336 -> 0.296 |
| hbt_bcs/1.200V/-40C | 3.3 -> 4.1 | 3.1 -> 3.8 | 22.0 -> 86.8 | 18.4 -> 86.4 | 0.370 -> 0.324 |
| hbt_bcs/1.200V/27C | 2.7 -> 3.7 | 2.4 -> 3.3 | 13.5 -> 18.1 | 12.2 -> 17.8 | 0.423 -> 0.369 |
| hbt_bcs/1.200V/125C | 2.7 -> 4.0 | 2.4 -> 3.6 | 10.1 -> 12.3 | 9.5 -> 11.9 | 0.477 -> 0.425 |
| hbt_bcs/1.320V/-40C | 2.0 -> 2.8 | 1.7 -> 2.2 | 8.4 -> 17.0 | 7.3 -> 15.7 | 0.527 -> 0.459 |
| hbt_bcs/1.320V/27C | 1.8 -> 2.8 | 1.5 -> 2.3 | 7.7 -> 11.9 | 7.0 -> 11.4 | 0.558 -> 0.504 |
| hbt_bcs/1.320V/125C | 2.0 -> 3.2 | 1.8 -> 2.8 | 7.3 -> 8.8 | 6.9 -> 8.5 | 0.569 -> 0.525 |
| hbt_wcs/1.080V/-40C | 17.5 -> 25.2 | 16.8 -> 24.4 | NR -> NR | NR -> NR | 0.148 -> 0.132 |
| hbt_wcs/1.080V/27C | 14.1 -> 18.4 | 13.1 -> 17.4 | NR -> NR | NR -> NR | 0.187 -> 0.167 |
| hbt_wcs/1.080V/125C | 14.1 -> 18.2 | 12.6 -> 16.4 | NR -> NR | NR -> NR | 0.240 -> 0.213 |
| hbt_wcs/1.200V/-40C | 6.9 -> 8.2 | 6.4 -> 7.7 | 93.9 -> NR | 93.7 -> NR | 0.278 -> 0.249 |
| hbt_wcs/1.200V/27C | 7.0 -> 8.4 | 6.3 -> 7.7 | 67.7 -> 91.8 | 50.1 -> 91.6 | 0.313 -> 0.280 |
| hbt_wcs/1.200V/125C | 7.6 -> 9.6 | 6.8 -> 8.6 | 19.8 -> 27.7 | 18.6 -> 26.0 | 0.352 -> 0.316 |
| hbt_wcs/1.320V/-40C | 5.1 -> 6.1 | 4.7 -> 5.6 | 20.7 -> 26.2 | 18.4 -> 25.3 | 0.401 -> 0.360 |
| hbt_wcs/1.320V/27C | 5.2 -> 6.3 | 4.7 -> 5.7 | 15.3 -> 18.1 | 14.3 -> 17.5 | 0.433 -> 0.387 |
| hbt_wcs/1.320V/125C | 5.5 -> 6.9 | 5.0 -> 6.3 | 13.3 -> 15.6 | 12.4 -> 14.7 | 0.454 -> 0.412 |

Corners missing the 0.25 V decision level (up edge): baseline 6, revised 8 (NR = not reached).
Corners missing the 100 ps floor-level limit in the revised run: none.

## R20 clock quality (clk_buf_quad, identical ideal source and 20 fF loads), baseline -> revised

Measurements: `r20_high_a_s`, `r20_high_b_s`, `r20_period_a_s`, `r20_period_b_s`, `r20_quad_270_s`, `r20_quad_90_s`, `r20_slew_rise_a_s`, `r20_slew_rise_b_s`, `r20_swing_a_v`, `r20_swing_b_v`

| corner | duty A % | duty B % | swing A pp V | swing B pp V |
|---|---|---|---|---|
| hbt_typ/1.080V/-40C | 50.01 -> 50.01 | 48.86 -> 48.87 | r20_swing_a_v: 0.805 -> 0.805 | r20_swing_b_v: 0.804 -> 0.804 |
| hbt_typ/1.080V/27C | 50.01 -> 50.01 | 49.00 -> 49.01 | r20_swing_a_v: 1.000 -> 1.000 | r20_swing_b_v: 0.997 -> 0.997 |
| hbt_typ/1.080V/125C | 50.01 -> 50.01 | 49.08 -> 49.09 | r20_swing_a_v: 1.226 -> 1.216 | r20_swing_b_v: 1.225 -> 1.215 |
| hbt_typ/1.200V/-40C | 50.01 -> 50.01 | 48.96 -> 48.97 | r20_swing_a_v: 1.294 -> 1.293 | r20_swing_b_v: 1.289 -> 1.288 |
| hbt_typ/1.200V/27C | 50.01 -> 50.01 | 48.98 -> 48.98 | r20_swing_a_v: 1.408 -> 1.395 | r20_swing_b_v: 1.406 -> 1.394 |
| hbt_typ/1.200V/125C | 50.00 -> 50.00 | 48.97 -> 48.97 | r20_swing_a_v: 1.446 -> 1.426 | r20_swing_b_v: 1.446 -> 1.427 |
| hbt_typ/1.320V/-40C | 50.01 -> 50.01 | 48.77 -> 48.78 | r20_swing_a_v: 1.606 -> 1.587 | r20_swing_b_v: 1.606 -> 1.588 |
| hbt_typ/1.320V/27C | 50.00 -> 50.00 | 48.79 -> 48.78 | r20_swing_a_v: 1.622 -> 1.599 | r20_swing_b_v: 1.623 -> 1.600 |
| hbt_typ/1.320V/125C | 50.00 -> 50.00 | 48.78 -> 48.79 | r20_swing_a_v: 1.602 -> 1.578 | r20_swing_b_v: 1.603 -> 1.579 |
| hbt_bcs/1.080V/-40C | 50.01 -> 50.01 | 48.89 -> 48.90 | r20_swing_a_v: 0.860 -> 0.860 | r20_swing_b_v: 0.858 -> 0.858 |
| hbt_bcs/1.080V/27C | 50.01 -> 50.01 | 49.03 -> 49.04 | r20_swing_a_v: 1.065 -> 1.064 | r20_swing_b_v: 1.061 -> 1.061 |
| hbt_bcs/1.080V/125C | 50.01 -> 50.01 | 49.11 -> 49.11 | r20_swing_a_v: 1.278 -> 1.266 | r20_swing_b_v: 1.277 -> 1.265 |
| hbt_bcs/1.200V/-40C | 50.01 -> 50.01 | 48.98 -> 48.99 | r20_swing_a_v: 1.366 -> 1.363 | r20_swing_b_v: 1.360 -> 1.357 |
| hbt_bcs/1.200V/27C | 50.01 -> 50.01 | 48.99 -> 48.99 | r20_swing_a_v: 1.459 -> 1.444 | r20_swing_b_v: 1.457 -> 1.443 |
| hbt_bcs/1.200V/125C | 50.00 -> 50.00 | 48.99 -> 48.99 | r20_swing_a_v: 1.494 -> 1.473 | r20_swing_b_v: 1.494 -> 1.473 |
| hbt_bcs/1.320V/-40C | 50.01 -> 50.01 | 48.77 -> 48.76 | r20_swing_a_v: 1.659 -> 1.638 | r20_swing_b_v: 1.659 -> 1.638 |
| hbt_bcs/1.320V/27C | 50.01 -> 50.01 | 48.76 -> 48.82 | r20_swing_a_v: 1.674 -> 1.650 | r20_swing_b_v: 1.675 -> 1.650 |
| hbt_bcs/1.320V/125C | 50.01 -> 50.01 | 48.85 -> 48.84 | r20_swing_a_v: 1.655 -> 1.629 | r20_swing_b_v: 1.655 -> 1.630 |
| hbt_wcs/1.080V/-40C | 50.01 -> 50.01 | 48.85 -> 48.86 | r20_swing_a_v: 0.747 -> 0.746 | r20_swing_b_v: 0.746 -> 0.746 |
| hbt_wcs/1.080V/27C | 50.01 -> 50.01 | 48.99 -> 49.00 | r20_swing_a_v: 0.929 -> 0.929 | r20_swing_b_v: 0.927 -> 0.927 |
| hbt_wcs/1.080V/125C | 50.01 -> 50.01 | 49.06 -> 49.07 | r20_swing_a_v: 1.165 -> 1.157 | r20_swing_b_v: 1.164 -> 1.156 |
| hbt_wcs/1.200V/-40C | 50.01 -> 50.01 | 48.95 -> 48.96 | r20_swing_a_v: 1.220 -> 1.219 | r20_swing_b_v: 1.215 -> 1.215 |
| hbt_wcs/1.200V/27C | 50.01 -> 50.01 | 48.97 -> 48.98 | r20_swing_a_v: 1.353 -> 1.343 | r20_swing_b_v: 1.351 -> 1.341 |
| hbt_wcs/1.200V/125C | 50.00 -> 50.01 | 48.96 -> 48.96 | r20_swing_a_v: 1.398 -> 1.380 | r20_swing_b_v: 1.398 -> 1.381 |
| hbt_wcs/1.320V/-40C | 50.01 -> 50.00 | 48.79 -> 48.79 | r20_swing_a_v: 1.554 -> 1.537 | r20_swing_b_v: 1.554 -> 1.537 |
| hbt_wcs/1.320V/27C | 50.00 -> 50.00 | 48.81 -> 48.80 | r20_swing_a_v: 1.571 -> 1.550 | r20_swing_b_v: 1.572 -> 1.551 |
| hbt_wcs/1.320V/125C | 50.00 -> 50.00 | 48.79 -> 48.80 | r20_swing_a_v: 1.551 -> 1.528 | r20_swing_b_v: 1.552 -> 1.529 |
