# TX sizing record 20261027-024044-2e55774

**Sizing evidence, not a spec result and not a measurement.** Simulated, first-cut sizes, ideal-source drive, lumped pad stand-in.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `267ea83a0510bcb61d2956058095201c0f481ff7`
- `tx_sizing_ffe0_typ.sp` sha256 `b5c728024558ed8a605e46201dec47ac02c304dc47db46790262c6960a1a995a`, `tx_sizing_ffe0_typ.request.json` sha256 `521e36e3d39fd85c7a212977b395b3a48127ed1d6d32737c2dfafae9cedb7697`
- `tx_sizing_ffe0_bcs.sp` sha256 `17f18112746a2466cd28f518bd6db31052e5ae1c28d7fb321caeb391236c33ba`, `tx_sizing_ffe0_bcs.request.json` sha256 `31a3e924e93372730ab259db6b9fe4bdab624ec6a91788c954daa250a8994fe7`
- `tx_sizing_ffe0_wcs.sp` sha256 `eff1bd0e5ef2a57cd7d35b0054adf08f73776f4b7520ebba8db2c1e4919a2149`, `tx_sizing_ffe0_wcs.request.json` sha256 `f4e2f6d7c8b724c9b6fd4031d67d6a649e66f7b38fc801d64c16aa25fe154068`
- `tx_sizing_ffe1_typ.sp` sha256 `b1487773779cf00a4e9346ab806540dcbf83a00faa422a46ef475ccf7bdadd6d`, `tx_sizing_ffe1_typ.request.json` sha256 `960671b24e6037bddf79673910671804e54b92098edc277d055e193bc214141f`
- `tx_sizing_ffe1_bcs.sp` sha256 `cf6a71009d6bce8a448bab2cd3074207d0b9bcaed21624b6d0a6805cddb4a897`, `tx_sizing_ffe1_bcs.request.json` sha256 `0e2742c15fec9a8df131015531a8587fd4ffd51fc904f596bfecd577dac4abba`
- `tx_sizing_ffe1_wcs.sp` sha256 `564ce1d1297048ad86678f8f98b4781483c477050fed1d17de5803f27881c0c2`, `tx_sizing_ffe1_wcs.request.json` sha256 `9110bc8cb492633052175703ae9e570089642a55b1193d37cef8684190e475a8`
- netlist `design/tx/netlists/bias.spice` sha256 `65855605637769fa33445dfe22c55dedce04b7577ac83a211286d0336e3a47e0`
- netlist `design/tx/netlists/predriver.spice` sha256 `0108584d4e4bbe0272aecca85ad475ad71d4db36d445283a6c98549d3efe1f6d`
- netlist `design/tx/netlists/driver_ffe.spice` sha256 `874e0b5eea8d1201873fccbe623c9c2185cb569b2225813c7bcd25992b7064e8`

## Run
- tx_sizing_ffe0_bcs exit=3
tx_sizing_ffe0_typ exit=3
tx_sizing_ffe0_wcs exit=3
tx_sizing_ffe1_bcs exit=3
tx_sizing_ffe1_typ exit=3
tx_sizing_ffe1_wcs exit=3
- ffe0_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-a9133df6866c`
- ffe0_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-6a92dedba3b7`
- ffe0_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-14a1f1385f0c`
- ffe1_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-56dc351e0930`
- ffe1_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-5a46ab0c11e4`
- ffe1_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-d1a3e3cc1d2c`

## R3 check (DR-003): collector <= 1.32 V, reverse Vbe <= 1.0 V

Worst case over all corners per HBT node.

| check | worst value (V) | limit (V) | corner |
|---|---|---|---|
| vc_max_drv_out_p | 1.2566 | 1.32 | ffe0_wcs/wcs/1.320V/-40C |
| vc_max_drv_out_n | 1.2961 | 1.32 | ffe0_bcs/bcs/1.320V/-40C |
| vc_max_drv_tail_main | 0.5175 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_drv_tail_post0 | 1.1248 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_drv_tail_post1 | 1.1248 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_drv_tail_post2 | 1.1248 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_pre_main_outp | 1.3500 **VIOLATION** | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_pre_main_outn | 1.3503 **VIOLATION** | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_pre_main_tail | 0.5196 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_pre_post_outp | 1.3282 **VIOLATION** | 1.32 | ffe0_wcs/wcs/1.320V/27C |
| vc_max_pre_post_outn | 1.3283 **VIOLATION** | 1.32 | ffe0_wcs/wcs/1.320V/27C |
| vc_max_pre_post_tail | 0.5196 | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_bias_vbn | 1.0619 | 1.32 | ffe0_wcs/wcs/1.320V/-40C |
| vbe_rev_max_drv_main_p | -0.3798 | 1.0 | ffe1_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_main_n | -0.3809 | 1.0 | ffe1_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_tail_main | -0.7762 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_p | -0.4759 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_n | -0.4790 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_tail | -0.7785 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_p | -0.4715 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_n | -0.4759 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_tail | -0.7762 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_bias_ref | -0.7718 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_drv_post0_p | 0.2162 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post0_n | 0.1958 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post0_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |
| vbe_rev_max_drv_post1_p | 0.2162 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post1_n | 0.1958 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post1_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |
| vbe_rev_max_drv_post2_p | 0.2162 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post2_n | 0.1958 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post2_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |

- nodes beyond the R3 limits in this grid: **4**

## Informational headroom (not R3 limits)

| measure | worst value | corner |
|---|---|---|
| vce_min_drv_tail_main | 0.1086 V | ffe1_wcs/wcs/1.080V/-40C |
| vce_min_pre_main_tail | 0.0487 V | ffe0_wcs/wcs/1.080V/-40C |
| vcb_min_drv_pair_p | -0.5153 V | ffe1_bcs/bcs/1.320V/125C |
| vcb_min_drv_pair_n | -0.5205 V | ffe1_bcs/bcs/1.320V/125C |
| vce_max_drv_pair_p | 0.9335 V | ffe0_wcs/wcs/1.320V/-40C |
| vce_max_drv_pair_n | 0.9341 V | ffe0_typ/typ/1.320V/-40C |
| vce_max_pre_main_pair_p | 1.0540 V | ffe1_wcs/wcs/1.320V/-40C |
| vce_max_pre_main_pair_n | 1.0542 V | ffe1_wcs/wcs/1.320V/-40C |
| vce_max_pre_post_pair_p | 1.0515 V | ffe0_wcs/wcs/1.320V/-40C |
| vce_max_pre_post_pair_n | 1.0518 V | ffe0_wcs/wcs/1.320V/-40C |

## First look at R4 and R7 (sizing evidence, not a spec result)

| corner | r4 steady hi (V) | r4 steady lo (V) | r4 peak max/min (V) | r7 rise (ps) | r7 fall (ps) | Idd (mA) |
|---|---|---|---|---|---|---|
| ffe0_bcs/bcs/1.080V/-40C | 0.1232 | -0.1238 | 0.1276 / -0.1284 | 5.259 | 5.164 | 13.56 |
| ffe0_bcs/bcs/1.080V/125C | 0.1821 | -0.1827 | 0.1891 / -0.2383 | 3.495 | 3.491 | 15.29 |
| ffe0_bcs/bcs/1.080V/27C | 0.1497 | -0.1505 | 0.1557 / -0.1566 | 4.043 | 3.984 | 14.41 |
| ffe0_bcs/bcs/1.200V/-40C | 0.2065 | -0.2066 | 0.213 / -0.2137 | 2.359 | 2.336 | 22.47 |
| ffe0_bcs/bcs/1.200V/125C | 0.2511 | -0.2513 | 0.26 / -0.2604 | 2.297 | 2.297 | 20.92 |
| ffe0_bcs/bcs/1.200V/27C | 0.2274 | -0.2275 | 0.2363 / -0.237 | 2.272 | 2.243 | 21.67 |
| ffe0_bcs/bcs/1.320V/-40C | 0.2907 | -0.2908 | 0.3 / -0.3006 | 1.531 | 1.544 | 31.64 |
| ffe0_bcs/bcs/1.320V/125C | 0.3201 | -0.3201 | 0.3291 / -0.3293 | 1.711 | 1.686 | 26.63 |
| ffe0_bcs/bcs/1.320V/27C | 0.3051 | -0.3051 | 0.3172 / -0.3179 | 1.603 | 1.569 | 29.05 |
| ffe0_typ/typ/1.080V/-40C | 0.1133 | -0.1138 | 0.1165 / -0.1172 | 6.396 | 6.364 | 11.44 |
| ffe0_typ/typ/1.080V/125C | 0.165 | -0.1656 | 0.1707 / -0.2139 | 4.384 | 4.281 | 12.94 |
| ffe0_typ/typ/1.080V/27C | 0.137 | -0.1377 | 0.1415 / -0.1422 | 4.997 | 4.899 | 12.19 |
| ffe0_typ/typ/1.200V/-40C | 0.1905 | -0.1906 | 0.1958 / -0.1964 | 2.848 | 2.844 | 18.99 |
| ffe0_typ/typ/1.200V/125C | 0.2275 | -0.2276 | 0.2351 / -0.2354 | 2.859 | 2.82 | 17.7 |
| ffe0_typ/typ/1.200V/27C | 0.2084 | -0.2085 | 0.2155 / -0.2162 | 2.788 | 2.768 | 18.35 |
| ffe0_typ/typ/1.320V/-40C | 0.2683 | -0.2683 | 0.2763 / -0.2768 | 1.896 | 1.89 | 26.75 |
| ffe0_typ/typ/1.320V/125C | 0.2896 | -0.2896 | 0.2984 / -0.2987 | 2.111 | 2.097 | 22.5 |
| ffe0_typ/typ/1.320V/27C | 0.2795 | -0.2794 | 0.2898 / -0.2903 | 1.907 | 1.891 | 24.59 |
| ffe0_wcs/wcs/1.080V/-40C | 0.1033 | -0.1037 | 0.1057 / -0.1061 | 7.739 | 7.767 | 9.742 |
| ffe0_wcs/wcs/1.080V/125C | 0.1476 | -0.1481 | 0.1522 / -0.1897 | 5.517 | 5.455 | 10.98 |
| ffe0_wcs/wcs/1.080V/27C | 0.1242 | -0.1247 | 0.1274 / -0.128 | 6.159 | 6.136 | 10.38 |
| ffe0_wcs/wcs/1.200V/-40C | 0.1753 | -0.1754 | 0.1797 / -0.1801 | 3.498 | 3.495 | 16.27 |
| ffe0_wcs/wcs/1.200V/125C | 0.2041 | -0.2042 | 0.2106 / -0.2109 | 3.57 | 3.556 | 15.05 |
| ffe0_wcs/wcs/1.200V/27C | 0.1899 | -0.19 | 0.1958 / -0.1963 | 3.37 | 3.319 | 15.69 |
| ffe0_wcs/wcs/1.320V/-40C | 0.2475 | -0.2475 | 0.2545 / -0.2548 | 2.252 | 2.25 | 22.97 |
| ffe0_wcs/wcs/1.320V/125C | 0.2598 | -0.2598 | 0.2681 / -0.2684 | 2.665 | 2.659 | 19.14 |
| ffe0_wcs/wcs/1.320V/27C | 0.2549 | -0.2549 | 0.2637 / -0.2642 | 2.317 | 2.29 | 21.06 |
| ffe1_bcs/bcs/1.080V/-40C | 0.07848 | -0.07887 | 0.1741 / -0.1747 | 3.577 | 3.649 | 15.87 |
| ffe1_bcs/bcs/1.080V/125C | 0.1167 | -0.117 | 0.2571 / -0.2574 | 2.369 | 2.331 | 17.87 |
| ffe1_bcs/bcs/1.080V/27C | 0.09567 | -0.09616 | 0.2121 / -0.2128 | 2.803 | 2.758 | 16.84 |
| ffe1_bcs/bcs/1.200V/-40C | 0.1318 | -0.132 | 0.2899 / -0.2906 | 1.696 | 1.67 | 26.28 |
| ffe1_bcs/bcs/1.200V/125C | 0.1613 | -0.1614 | 0.3499 / -0.3501 | 1.617 | 1.586 | 24.42 |
| ffe1_bcs/bcs/1.200V/27C | 0.1458 | -0.1459 | 0.321 / -0.3219 | 1.564 | 1.609 | 25.31 |
| ffe1_bcs/bcs/1.320V/-40C | 0.1861 | -0.1863 | 0.4074 / -0.4083 | 1.171 | 1.16 | 36.96 |
| ffe1_bcs/bcs/1.320V/125C | 0.2057 | -0.2057 | 0.4445 / -0.4427 | 1.162 | 1.188 | 31.04 |
| ffe1_bcs/bcs/1.320V/27C | 0.1961 | -0.1962 | 0.4253 / -0.4259 | 1.042 | 1.109 | 33.91 |
| ffe1_typ/typ/1.080V/-40C | 0.07217 | -0.07249 | 0.1588 / -0.1594 | 4.283 | 4.255 | 13.39 |
| ffe1_typ/typ/1.080V/125C | 0.1058 | -0.1061 | 0.2319 / -0.2322 | 2.965 | 2.94 | 15.12 |
| ffe1_typ/typ/1.080V/27C | 0.08762 | -0.08803 | 0.1927 / -0.1932 | 3.34 | 3.379 | 14.25 |
| ffe1_typ/typ/1.200V/-40C | 0.1217 | -0.1218 | 0.2665 / -0.267 | 1.979 | 1.99 | 22.21 |
| ffe1_typ/typ/1.200V/125C | 0.1462 | -0.1463 | 0.3176 / -0.3179 | 1.89 | 1.929 | 20.66 |
| ffe1_typ/typ/1.200V/27C | 0.1337 | -0.1338 | 0.2928 / -0.2935 | 1.891 | 1.841 | 21.43 |
| ffe1_typ/typ/1.320V/-40C | 0.1718 | -0.172 | 0.3752 / -0.3758 | 1.235 | 1.273 | 31.25 |
| ffe1_typ/typ/1.320V/125C | 0.1863 | -0.1863 | 0.3999 / -0.3986 | 1.434 | 1.411 | 26.24 |
| ffe1_typ/typ/1.320V/27C | 0.1797 | -0.1798 | 0.3913 / -0.392 | 1.366 | 1.333 | 28.71 |
| ffe1_wcs/wcs/1.080V/-40C | 0.06589 | -0.06614 | 0.144 / -0.1444 | 5.273 | 5.246 | 11.4 |
| ffe1_wcs/wcs/1.080V/125C | 0.09468 | -0.09494 | 0.2067 / -0.2069 | 3.609 | 3.609 | 12.83 |
| ffe1_wcs/wcs/1.080V/27C | 0.07942 | -0.07978 | 0.1735 / -0.1739 | 4.076 | 4.005 | 12.13 |
| ffe1_wcs/wcs/1.200V/-40C | 0.112 | -0.1121 | 0.2445 / -0.2449 | 2.307 | 2.287 | 19.02 |
| ffe1_wcs/wcs/1.200V/125C | 0.1312 | -0.1313 | 0.2851 / -0.2854 | 2.396 | 2.379 | 17.56 |
| ffe1_wcs/wcs/1.200V/27C | 0.1218 | -0.1219 | 0.2659 / -0.2664 | 2.306 | 2.292 | 18.33 |
| ffe1_wcs/wcs/1.320V/-40C | 0.1585 | -0.1586 | 0.3455 / -0.346 | 1.56 | 1.548 | 26.83 |
| ffe1_wcs/wcs/1.320V/125C | 0.1674 | -0.1673 | 0.3549 / -0.3548 | 1.768 | 1.76 | 22.32 |
| ffe1_wcs/wcs/1.320V/27C | 0.1639 | -0.164 | 0.3571 / -0.3577 | 1.567 | 1.595 | 24.58 |

Differential output `v(padp)-v(padn)` into 100 ohm differential, 4 ohm + 100 fF per leg. R7 is NOT a conforming 20-80 % measurement: the thresholds are fixed absolute levels (+-0.06 V FFE off, +-0.04 V FFE on), chosen below the smallest steady half-swing so every corner crosses them, so the time is that of the central part of the edge and understates 20-80 % at large swing. The inputs are ideal 20 ps ramps. 'n/a' = no crossing.

## Not simulated

- `mux2to1_cml`, `ffe_en`, `lvl_cml2cmos`: contain PSP103 MOS, which needs OSDI; the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` fail (sim/README.md known gaps, klayout-tools#3818/#3819; owner #3). Their R3 status is unknown beyond the argument in design/README.md.
- `pad_esd`: the PDK ESD diode models are not loaded in this deck; a lumped stand-in loads each output. R18, R19 and R6 are not assessed (#24).
- PDK `rsil` is an OSDI (`r3_cmc`) model, so the deck uses a behavioural resistor from the PDK symbol's own value formula, with the corner's sheet-resistance scale (6.02/7.0/7.98 ohm/sq) and tc1 = 3.1e-3. Resistor current-density limits are not checked.
- Corners: HBT, capacitor and resistor corners move together (typ/typ/typ, bcs/bcs/bcs, wcs/wcs/wcs), x supply 1.08/1.2/1.32 V x -40/27/125 C x FFE off / all three post slices on. Mismatch/Monte Carlo is not run.
- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not the mux output.
- Supply and bias: Rref is a placeholder resistor reference, so tail current tracks the supply; the bias block is not a supply-independent reference.
