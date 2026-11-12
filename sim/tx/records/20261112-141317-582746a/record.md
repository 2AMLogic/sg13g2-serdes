# TX sizing record 20261112-141317-582746a

**Sizing evidence, not a spec result and not a measurement.** Simulated, first-cut sizes, ideal-source drive, extracted pad-metal C + PDK ESD diodes (issue #142).

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- `tx_sizing_ffe0_typ.sp` sha256 `5ae1aad2f06f3942a0e282e1b200197d4524ee4573f78a135fc78271bf584e98`, `tx_sizing_ffe0_typ.request.json` sha256 `c8cf3984b3befd270d0b3a0f81a33f9e72492614cffb77987bb865a91c785996`
- `tx_sizing_ffe0_bcs.sp` sha256 `24ab21a8501d582d3f8b3522f0f8fbddc09bbbbbbe0883556fda5acca57c47eb`, `tx_sizing_ffe0_bcs.request.json` sha256 `b297897e45457b146f44bddbefa6b2fcdbcfe6c2e23d098f8a44a3309eea3004`
- `tx_sizing_ffe0_wcs.sp` sha256 `4fc95343fdde0dfa3f04523518c60581840650432180fa837e1cff14994ad354`, `tx_sizing_ffe0_wcs.request.json` sha256 `5a321dade89a26787563d15edc6c15aa962a61f619cc6f704f6059b14eae8d12`
- `tx_sizing_ffe1_typ.sp` sha256 `2ac49c91981aa4bf251a3bd07e4210cc0f0784e7ffb761705ef2222f07f318d0`, `tx_sizing_ffe1_typ.request.json` sha256 `10cde4577135351da08a70738caf40413862da4364beb90bb147bbfb58dc5c0a`
- `tx_sizing_ffe1_bcs.sp` sha256 `1b7a5dd50cf2635f120115e25aca31ca8d6bd694b5d0be073d6e60d8078264e8`, `tx_sizing_ffe1_bcs.request.json` sha256 `e8044fa56d2a9d39f303965805c12fbede74b706f5b257b7afeff7e8d403802f`
- `tx_sizing_ffe1_wcs.sp` sha256 `bdcccccec56c6b62936dc7d3fb97eda28ae151c14e2a9827a6cf8c3a5cb1b2b5`, `tx_sizing_ffe1_wcs.request.json` sha256 `941403b88cb2f0ec1ccd9817f18e588a0c39386fcf8e7cccf212bbe8f01bff6a`
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
- ffe0_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-51a96f66dcd4`
- ffe0_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-026cba344e9e`
- ffe0_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-da69f174aeeb`
- ffe1_typ: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-e25cbc6c5439`
- ffe1_bcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-b0ffe35dfc4b`
- ffe1_wcs: status **fail** (6/9 corners pass, 3 fail, 0 error), backend job `klt-sim-f136cc72bc6d`

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
| vc_max_pre_main_outp | 1.3491 **VIOLATION** | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_pre_main_outn | 1.3492 **VIOLATION** | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_pre_main_tail | 0.5196 | 1.32 | ffe0_bcs/bcs/1.320V/125C |
| vc_max_pre_post_outp | 1.3282 **VIOLATION** | 1.32 | ffe0_wcs/wcs/1.320V/27C |
| vc_max_pre_post_outn | 1.3283 **VIOLATION** | 1.32 | ffe0_wcs/wcs/1.320V/27C |
| vc_max_pre_post_tail | 0.5196 | 1.32 | ffe1_bcs/bcs/1.320V/125C |
| vc_max_bias_vbn | 1.0618 | 1.32 | ffe0_wcs/wcs/1.320V/-40C |
| vbe_rev_max_drv_main_p | -0.3797 | 1.0 | ffe1_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_main_n | -0.3808 | 1.0 | ffe1_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_tail_main | -0.7762 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_p | -0.4759 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_n | -0.4790 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_main_tail | -0.7785 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_p | -0.4715 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_n | -0.4759 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_pre_post_tail | -0.7762 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_bias_ref | -0.7718 | 1.0 | ffe0_bcs/bcs/1.080V/125C |
| vbe_rev_max_drv_post0_p | 0.2161 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post0_n | 0.1966 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post0_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |
| vbe_rev_max_drv_post1_p | 0.2161 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post1_n | 0.1966 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post1_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |
| vbe_rev_max_drv_post2_p | 0.2161 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post2_n | 0.1966 | 1.0 | ffe0_bcs/bcs/1.320V/125C |
| vbe_rev_max_drv_post2_tail | 0.0000 | 1.0 | ffe0_wcs/wcs/1.080V/125C |

- nodes beyond the R3 limits in this grid: **4**

## Informational headroom (not R3 limits)

| measure | worst value | corner |
|---|---|---|
| vce_min_drv_tail_main | 0.1089 V | ffe1_wcs/wcs/1.080V/-40C |
| vce_min_pre_main_tail | 0.0487 V | ffe0_wcs/wcs/1.080V/-40C |
| vcb_min_drv_pair_p | -0.5161 V | ffe1_bcs/bcs/1.320V/125C |
| vcb_min_drv_pair_n | -0.5213 V | ffe1_bcs/bcs/1.320V/125C |
| vce_max_drv_pair_p | 0.9327 V | ffe0_wcs/wcs/1.320V/-40C |
| vce_max_drv_pair_n | 0.9334 V | ffe0_typ/typ/1.320V/-40C |
| vce_max_pre_main_pair_p | 1.0539 V | ffe1_wcs/wcs/1.320V/-40C |
| vce_max_pre_main_pair_n | 1.0539 V | ffe1_wcs/wcs/1.320V/-40C |
| vce_max_pre_post_pair_p | 1.0515 V | ffe0_wcs/wcs/1.320V/-40C |
| vce_max_pre_post_pair_n | 1.0518 V | ffe0_wcs/wcs/1.320V/-40C |

## First look at R4 and R7 (sizing evidence, not a spec result)

| corner | r4 steady hi (V) | r4 steady lo (V) | r4 peak max/min (V) | r7 rise (ps) | r7 fall (ps) | Idd (mA) |
|---|---|---|---|---|---|---|
| ffe0_bcs/bcs/1.080V/-40C | 0.1232 | -0.1238 | 0.1272 / -0.128 | 5.599 | 5.552 | 13.56 |
| ffe0_bcs/bcs/1.080V/125C | 0.1821 | -0.1827 | 0.188 / -0.2383 | 3.833 | 3.801 | 15.29 |
| ffe0_bcs/bcs/1.080V/27C | 0.1497 | -0.1505 | 0.1548 / -0.1556 | 4.385 | 4.335 | 14.41 |
| ffe0_bcs/bcs/1.200V/-40C | 0.2065 | -0.2066 | 0.2124 / -0.213 | 2.568 | 2.559 | 22.47 |
| ffe0_bcs/bcs/1.200V/125C | 0.2511 | -0.2513 | 0.2583 / -0.2587 | 2.506 | 2.513 | 20.92 |
| ffe0_bcs/bcs/1.200V/27C | 0.2274 | -0.2275 | 0.2346 / -0.2354 | 2.453 | 2.449 | 21.67 |
| ffe0_bcs/bcs/1.320V/-40C | 0.2907 | -0.2908 | 0.299 / -0.2997 | 1.639 | 1.636 | 31.64 |
| ffe0_bcs/bcs/1.320V/125C | 0.3201 | -0.3201 | 0.3274 / -0.3277 | 1.877 | 1.878 | 26.63 |
| ffe0_bcs/bcs/1.320V/27C | 0.3051 | -0.3051 | 0.3149 / -0.3156 | 1.742 | 1.734 | 29.05 |
| ffe0_typ/typ/1.080V/-40C | 0.1133 | -0.1138 | 0.1162 / -0.1168 | 6.756 | 6.752 | 11.44 |
| ffe0_typ/typ/1.080V/125C | 0.165 | -0.1656 | 0.1699 / -0.2139 | 4.775 | 4.731 | 12.94 |
| ffe0_typ/typ/1.080V/27C | 0.137 | -0.1377 | 0.1409 / -0.1415 | 5.396 | 5.322 | 12.19 |
| ffe0_typ/typ/1.200V/-40C | 0.1905 | -0.1906 | 0.1953 / -0.1957 | 3.127 | 3.092 | 18.99 |
| ffe0_typ/typ/1.200V/125C | 0.2275 | -0.2276 | 0.2339 / -0.2342 | 3.146 | 3.102 | 17.7 |
| ffe0_typ/typ/1.200V/27C | 0.2084 | -0.2085 | 0.2143 / -0.2149 | 2.987 | 3.004 | 18.35 |
| ffe0_typ/typ/1.320V/-40C | 0.2683 | -0.2683 | 0.2753 / -0.2759 | 2.029 | 2.031 | 26.75 |
| ffe0_typ/typ/1.320V/125C | 0.2896 | -0.2896 | 0.297 / -0.2974 | 2.312 | 2.309 | 22.5 |
| ffe0_typ/typ/1.320V/27C | 0.2795 | -0.2794 | 0.2879 / -0.2883 | 2.092 | 2.082 | 24.59 |
| ffe0_wcs/wcs/1.080V/-40C | 0.1033 | -0.1037 | 0.1054 / -0.1059 | 8.165 | 8.104 | 9.742 |
| ffe0_wcs/wcs/1.080V/125C | 0.1476 | -0.1481 | 0.1517 / -0.1897 | 5.957 | 5.907 | 10.98 |
| ffe0_wcs/wcs/1.080V/27C | 0.1242 | -0.1247 | 0.127 / -0.1275 | 6.608 | 6.519 | 10.38 |
| ffe0_wcs/wcs/1.200V/-40C | 0.1753 | -0.1754 | 0.1792 / -0.1796 | 3.749 | 3.734 | 16.27 |
| ffe0_wcs/wcs/1.200V/125C | 0.2041 | -0.2042 | 0.2097 / -0.21 | 3.936 | 3.87 | 15.05 |
| ffe0_wcs/wcs/1.200V/27C | 0.1899 | -0.19 | 0.1948 / -0.1953 | 3.664 | 3.627 | 15.69 |
| ffe0_wcs/wcs/1.320V/-40C | 0.2475 | -0.2475 | 0.2536 / -0.254 | 2.415 | 2.415 | 22.97 |
| ffe0_wcs/wcs/1.320V/125C | 0.2598 | -0.2598 | 0.267 / -0.2673 | 2.892 | 2.868 | 19.14 |
| ffe0_wcs/wcs/1.320V/27C | 0.2549 | -0.2549 | 0.2622 / -0.2627 | 2.531 | 2.506 | 21.06 |
| ffe1_bcs/bcs/1.080V/-40C | 0.07848 | -0.07887 | 0.1735 / -0.1742 | 3.659 | 3.752 | 15.87 |
| ffe1_bcs/bcs/1.080V/125C | 0.1167 | -0.117 | 0.2558 / -0.2561 | 2.539 | 2.491 | 17.87 |
| ffe1_bcs/bcs/1.080V/27C | 0.09567 | -0.09616 | 0.2109 / -0.2116 | 2.952 | 2.917 | 16.84 |
| ffe1_bcs/bcs/1.200V/-40C | 0.1318 | -0.132 | 0.2891 / -0.2898 | 1.781 | 1.764 | 26.28 |
| ffe1_bcs/bcs/1.200V/125C | 0.1613 | -0.1614 | 0.3486 / -0.3488 | 1.715 | 1.703 | 24.42 |
| ffe1_bcs/bcs/1.200V/27C | 0.1458 | -0.1459 | 0.319 / -0.3199 | 1.61 | 1.674 | 25.31 |
| ffe1_bcs/bcs/1.320V/-40C | 0.1861 | -0.1863 | 0.4063 / -0.4072 | 1.215 | 1.213 | 36.96 |
| ffe1_bcs/bcs/1.320V/125C | 0.2057 | -0.2057 | 0.4432 / -0.4415 | 1.203 | 1.251 | 31.04 |
| ffe1_bcs/bcs/1.320V/27C | 0.1961 | -0.1962 | 0.4237 / -0.4242 | 1.126 | 1.125 | 33.91 |
| ffe1_typ/typ/1.080V/-40C | 0.07217 | -0.07249 | 0.1585 / -0.1589 | 4.484 | 4.446 | 13.39 |
| ffe1_typ/typ/1.080V/125C | 0.1058 | -0.1061 | 0.231 / -0.2313 | 3.124 | 3.128 | 15.12 |
| ffe1_typ/typ/1.080V/27C | 0.08762 | -0.08803 | 0.1919 / -0.1924 | 3.454 | 3.526 | 14.25 |
| ffe1_typ/typ/1.200V/-40C | 0.1217 | -0.1218 | 0.2658 / -0.2663 | 2.049 | 2.066 | 22.21 |
| ffe1_typ/typ/1.200V/125C | 0.1462 | -0.1463 | 0.3165 / -0.3167 | 2.041 | 2.021 | 20.66 |
| ffe1_typ/typ/1.200V/27C | 0.1337 | -0.1338 | 0.2913 / -0.292 | 2.012 | 1.975 | 21.43 |
| ffe1_typ/typ/1.320V/-40C | 0.1718 | -0.172 | 0.3742 / -0.3748 | 1.311 | 1.301 | 31.25 |
| ffe1_typ/typ/1.320V/125C | 0.1863 | -0.1863 | 0.3988 / -0.3976 | 1.533 | 1.523 | 26.24 |
| ffe1_typ/typ/1.320V/27C | 0.1797 | -0.1798 | 0.3896 / -0.3902 | 1.441 | 1.425 | 28.71 |
| ffe1_wcs/wcs/1.080V/-40C | 0.06589 | -0.06614 | 0.1437 / -0.1441 | 5.492 | 5.479 | 11.4 |
| ffe1_wcs/wcs/1.080V/125C | 0.09468 | -0.09494 | 0.2061 / -0.2064 | 3.852 | 3.803 | 12.83 |
| ffe1_wcs/wcs/1.080V/27C | 0.07942 | -0.07978 | 0.1729 / -0.1734 | 4.306 | 4.25 | 12.13 |
| ffe1_wcs/wcs/1.200V/-40C | 0.112 | -0.1121 | 0.2439 / -0.2443 | 2.441 | 2.424 | 19.02 |
| ffe1_wcs/wcs/1.200V/125C | 0.1312 | -0.1313 | 0.2843 / -0.2845 | 2.536 | 2.534 | 17.56 |
| ffe1_wcs/wcs/1.200V/27C | 0.1218 | -0.1219 | 0.2647 / -0.2652 | 2.424 | 2.419 | 18.33 |
| ffe1_wcs/wcs/1.320V/-40C | 0.1585 | -0.1586 | 0.3446 / -0.3451 | 1.642 | 1.635 | 26.83 |
| ffe1_wcs/wcs/1.320V/125C | 0.1674 | -0.1673 | 0.3543 / -0.3544 | 1.899 | 1.876 | 22.32 |
| ffe1_wcs/wcs/1.320V/27C | 0.1639 | -0.164 | 0.3556 / -0.3561 | 1.633 | 1.652 | 24.58 |

Differential output `v(padp)-v(padn)` into 100 ohm differential, 4 ohm series + extracted 70.66 fF pad-metal C + PDK ESD clamp diodes per leg (issue #142; was 4 ohm + 100 fF). R7 is NOT a conforming 20-80 % measurement: the thresholds are fixed absolute levels (+-0.06 V FFE off, +-0.04 V FFE on), chosen below the smallest steady half-swing so every corner crosses them, so the time is that of the central part of the edge and understates 20-80 % at large swing. The inputs are ideal 20 ps ramps. 'n/a' = no crossing.

## Not simulated

- `mux2to1_cml`, `ffe_en`, `lvl_cml2cmos`: contain PSP103 MOS, which needs OSDI; the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` fail (sim/README.md known gaps, klayout-tools#3818/#3819; owner #3). Their R3 status is unknown beyond the argument in design/README.md.
- `pad_esd` cell: not inlined; each output sees a 4 ohm series stand-in, the extracted 70.66 fF pad-metal C (layout/analog/pads/records/2026-11-12-fc8a7fa, quasi-static, no bondwire/package) and the PDK clamp diodes. PDK dantenna/dpantenna equivalence to the diodevdd_2kv clamp is not established (LVS #27, DR-013); only the TX padp leg is covered. R6 is in sim/bench/.
- PDK `rsil` is an OSDI (`r3_cmc`) model, so the deck uses a behavioural resistor from the PDK symbol's own value formula, with the corner's sheet-resistance scale (6.02/7.0/7.98 ohm/sq) and tc1 = 3.1e-3. Resistor current-density limits are not checked.
- Corners: HBT, capacitor and resistor corners move together (typ/typ/typ, bcs/bcs/bcs, wcs/wcs/wcs), x supply 1.08/1.2/1.32 V x -40/27/125 C x FFE off / all three post slices on. Mismatch/Monte Carlo is not run.
- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not the mux output.
- Supply and bias: Rref is a placeholder resistor reference, so tail current tracks the supply; the bias block is not a supply-independent reference.
