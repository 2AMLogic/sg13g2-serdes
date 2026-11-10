# mux2to1_cml clock-swing sweep record 20261110-232100-f7361f7-ckswing

**Sizing evidence, not a spec result and not a measurement.** Per-side clock swing swept at a fixed 0.6 V centre; no `spec/` row is graded here.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`
- `design/tx/netlists/mux2to1_cml.spice` sha256 `612cb14e2bb4526e87ed79c5799034d8993f7c936f58c00f38fc622c92a22adc`
- `tx_mosck_mux2to1_cml_sw100.sp` sha256 `a6f1e66dded70d6f8e2fe2e10d05df5226ef7d077ff8dc328d555ac71543af2f`, request sha256 `f7943d0a0475ee08982706e641d4ba65c68fbb0f957e28b3599df5d5307b4cec`
- `tx_mosck_mux2to1_cml_sw200.sp` sha256 `70f3416e09be656d00b92b59cf9b4ab6c34f0d04f1f0d9236180e97aa88387c4`, request sha256 `1017f82c9d1919dfc1db2fa77ed92a459f8dc647d2b0659d370cfae4ae467f66`
- `tx_mosck_mux2to1_cml_sw300.sp` sha256 `e0e7c4a82ab276652d4548ca149d12229c88c78f4241798af54954d5a69ca8ca`, request sha256 `3fc0758a9dcb4d0025bb0625048e7cdfe8215cde212ea9f601c711b24881c9ec`

## Run
- tx_mosck_mux2to1_cml_sw100 exit=4; tx_mosck_mux2to1_cml_sw200 exit=4; tx_mosck_mux2to1_cml_sw300 exit=4

## Output differential swing per corner (V, min of out_diff_min / max of out_diff_max)

- swing 0.1 V per side: **error**, 20/45 pass, 9 fail, 16 error, job `klt-sim-3ebc9d1113dc`
- swing 0.2 V per side: **error**, 23/45 pass, 11 fail, 11 error, job `klt-sim-d1f1f6380255`
- swing 0.3 V per side: **error**, 30/45 pass, 9 fail, 6 error, job `klt-sim-3bd40ab2c9b0`

### 0.1 V per side (0.2 V differential peak-to-peak)

| corner | status | out max (V) | out min (V) | peak-peak (V) |
|---|---|---|---|---|
| ff_bcs/1.080V/-40C | error | 0.01693 | -0.01712 | 0.03405 |
| ff_bcs/1.080V/125C | pass | 0.07866 | -0.07857 | 0.1572 |
| ff_bcs/1.080V/27C | pass | 0.03743 | -0.03738 | 0.07482 |
| ff_bcs/1.200V/-40C | pass | 0.05868 | -0.0587 | 0.1174 |
| ff_bcs/1.200V/125C | pass | 0.1414 | -0.1414 | 0.2828 |
| ff_bcs/1.200V/27C | pass | 0.09278 | -0.0928 | 0.1856 |
| ff_bcs/1.320V/-40C | fail | 0.1309 | -0.1309 | 0.2618 |
| ff_bcs/1.320V/125C | pass | 0.217 | -0.217 | 0.4339 |
| ff_bcs/1.320V/27C | fail | 0.1729 | -0.1729 | 0.3459 |
| fs_typ/1.080V/-40C | error | 0.003037 | -0.002548 | 0.005585 |
| fs_typ/1.080V/125C | pass | 0.03555 | -0.03581 | 0.07136 |
| fs_typ/1.080V/27C | error | 0.01083 | -0.01057 | 0.02139 |
| fs_typ/1.200V/-40C | error | 0.01986 | -0.02043 | 0.04029 |
| fs_typ/1.200V/125C | pass | 0.07919 | -0.07906 | 0.1583 |
| fs_typ/1.200V/27C | pass | 0.04011 | -0.04057 | 0.08068 |
| fs_typ/1.320V/-40C | fail | 0.06568 | -0.0657 | 0.1314 |
| fs_typ/1.320V/125C | pass | 0.1403 | -0.1403 | 0.2806 |
| fs_typ/1.320V/27C | fail | 0.09698 | -0.09699 | 0.194 |
| sf_typ/1.080V/-40C | error | 0.002398 | -0.002154 | 0.004552 |
| sf_typ/1.080V/125C | pass | 0.03604 | -0.03661 | 0.07264 |
| sf_typ/1.080V/27C | error | 0.009755 | -0.01001 | 0.01977 |
| sf_typ/1.200V/-40C | error | 0.01959 | -0.01998 | 0.03958 |
| sf_typ/1.200V/125C | pass | 0.08069 | -0.08077 | 0.1615 |
| sf_typ/1.200V/27C | pass | 0.04037 | -0.04054 | 0.08091 |
| sf_typ/1.320V/-40C | fail | 0.0661 | -0.06613 | 0.1322 |
| sf_typ/1.320V/125C | pass | 0.1424 | -0.1424 | 0.2848 |
| sf_typ/1.320V/27C | fail | 0.09788 | -0.09787 | 0.1957 |
| ss_wcs/1.080V/-40C | error | 9.198e-05 | -4.024e-05 | 0.0001322 |
| ss_wcs/1.080V/125C | error | 0.01192 | -0.01029 | 0.02221 |
| ss_wcs/1.080V/27C | error | 0.001149 | -0.001204 | 0.002353 |
| ss_wcs/1.200V/-40C | error | 0.002698 | -0.002363 | 0.005062 |
| ss_wcs/1.200V/125C | pass | 0.03365 | -0.03443 | 0.06808 |
| ss_wcs/1.200V/27C | error | 0.009639 | -0.01005 | 0.01969 |
| ss_wcs/1.320V/-40C | error | 0.02234 | -0.02282 | 0.04517 |
| ss_wcs/1.320V/125C | pass | 0.07535 | -0.07573 | 0.1511 |
| ss_wcs/1.320V/27C | fail | 0.04096 | -0.04146 | 0.08243 |
| tt_typ/1.080V/-40C | error | 0.002819 | -0.00244 | 0.005259 |
| tt_typ/1.080V/125C | pass | 0.03628 | -0.03672 | 0.073 |
| tt_typ/1.080V/27C | error | 0.01068 | -0.01055 | 0.02124 |
| tt_typ/1.200V/-40C | error | 0.01972 | -0.02023 | 0.03995 |
| tt_typ/1.200V/125C | pass | 0.08039 | -0.08029 | 0.1607 |
| tt_typ/1.200V/27C | pass | 0.04056 | -0.04075 | 0.08131 |
| tt_typ/1.320V/-40C | fail | 0.0652 | -0.06521 | 0.1304 |
| tt_typ/1.320V/125C | pass | 0.1417 | -0.1417 | 0.2834 |
| tt_typ/1.320V/27C | fail | 0.0972 | -0.0972 | 0.1944 |

### 0.2 V per side (0.4 V differential peak-to-peak)

| corner | status | out max (V) | out min (V) | peak-peak (V) |
|---|---|---|---|---|
| ff_bcs/1.080V/-40C | pass | 0.04595 | -0.04608 | 0.09203 |
| ff_bcs/1.080V/125C | pass | 0.1584 | -0.1584 | 0.3168 |
| ff_bcs/1.080V/27C | pass | 0.09019 | -0.09004 | 0.1802 |
| ff_bcs/1.200V/-40C | pass | 0.1451 | -0.1451 | 0.2903 |
| ff_bcs/1.200V/125C | pass | 0.2609 | -0.2608 | 0.5217 |
| ff_bcs/1.200V/27C | pass | 0.2021 | -0.2021 | 0.4042 |
| ff_bcs/1.320V/-40C | fail | 0.2654 | -0.2654 | 0.5308 |
| ff_bcs/1.320V/125C | pass | 0.3607 | -0.3606 | 0.7213 |
| ff_bcs/1.320V/27C | fail | 0.3159 | -0.3159 | 0.6318 |
| fs_typ/1.080V/-40C | error | 0.006644 | -0.005946 | 0.01259 |
| fs_typ/1.080V/125C | pass | 0.07819 | -0.0784 | 0.1566 |
| fs_typ/1.080V/27C | error | 0.02653 | -0.02689 | 0.05342 |
| fs_typ/1.200V/-40C | pass | 0.05728 | -0.05833 | 0.1156 |
| fs_typ/1.200V/125C | pass | 0.1747 | -0.1745 | 0.3492 |
| fs_typ/1.200V/27C | pass | 0.1037 | -0.1037 | 0.2074 |
| fs_typ/1.320V/-40C | fail | 0.1799 | -0.1799 | 0.3598 |
| fs_typ/1.320V/125C | pass | 0.2953 | -0.2953 | 0.5907 |
| fs_typ/1.320V/27C | fail | 0.2395 | -0.2394 | 0.4789 |
| sf_typ/1.080V/-40C | error | 0.006572 | -0.006199 | 0.01277 |
| sf_typ/1.080V/125C | pass | 0.08063 | -0.08119 | 0.1618 |
| sf_typ/1.080V/27C | error | 0.02713 | -0.02775 | 0.05488 |
| sf_typ/1.200V/-40C | pass | 0.05986 | -0.06092 | 0.1208 |
| sf_typ/1.200V/125C | pass | 0.1761 | -0.1761 | 0.3522 |
| sf_typ/1.200V/27C | pass | 0.1072 | -0.1073 | 0.2144 |
| sf_typ/1.320V/-40C | fail | 0.1821 | -0.1821 | 0.3641 |
| sf_typ/1.320V/125C | pass | 0.2893 | -0.2893 | 0.5786 |
| sf_typ/1.320V/27C | fail | 0.2387 | -0.2387 | 0.4775 |
| ss_wcs/1.080V/-40C | error | 3.218e-05 | -0.0001103 | 0.0001425 |
| ss_wcs/1.080V/125C | error | 0.02477 | -0.02328 | 0.04805 |
| ss_wcs/1.080V/27C | error | 0.002939 | -0.002573 | 0.005513 |
| ss_wcs/1.200V/-40C | error | 0.008574 | -0.007646 | 0.01622 |
| ss_wcs/1.200V/125C | pass | 0.07662 | -0.07804 | 0.1547 |
| ss_wcs/1.200V/27C | error | 0.02872 | -0.02941 | 0.05813 |
| ss_wcs/1.320V/-40C | fail | 0.07131 | -0.07274 | 0.144 |
| ss_wcs/1.320V/125C | fail | 0.1714 | -0.1718 | 0.3431 |
| ss_wcs/1.320V/27C | fail | 0.1125 | -0.1137 | 0.2262 |
| tt_typ/1.080V/-40C | error | 0.006653 | -0.006104 | 0.01276 |
| tt_typ/1.080V/125C | pass | 0.08012 | -0.08048 | 0.1606 |
| tt_typ/1.080V/27C | error | 0.02713 | -0.02762 | 0.05475 |
| tt_typ/1.200V/-40C | pass | 0.0578 | -0.05898 | 0.1168 |
| tt_typ/1.200V/125C | pass | 0.1762 | -0.1761 | 0.3524 |
| tt_typ/1.200V/27C | pass | 0.1053 | -0.1054 | 0.2107 |
| tt_typ/1.320V/-40C | fail | 0.179 | -0.179 | 0.358 |
| tt_typ/1.320V/125C | pass | 0.2933 | -0.2933 | 0.5866 |
| tt_typ/1.320V/27C | fail | 0.2386 | -0.2386 | 0.4772 |

### 0.3 V per side (0.6 V differential peak-to-peak)

| corner | status | out max (V) | out min (V) | peak-peak (V) |
|---|---|---|---|---|
| ff_bcs/1.080V/-40C | pass | 0.08463 | -0.08448 | 0.1691 |
| ff_bcs/1.080V/125C | pass | 0.2115 | -0.2114 | 0.423 |
| ff_bcs/1.080V/27C | pass | 0.1435 | -0.1435 | 0.287 |
| ff_bcs/1.200V/-40C | pass | 0.2022 | -0.2021 | 0.4044 |
| ff_bcs/1.200V/125C | pass | 0.3104 | -0.3103 | 0.6207 |
| ff_bcs/1.200V/27C | pass | 0.2539 | -0.2538 | 0.5077 |
| ff_bcs/1.320V/-40C | fail | 0.301 | -0.3009 | 0.6018 |
| ff_bcs/1.320V/125C | pass | 0.4069 | -0.4068 | 0.8136 |
| ff_bcs/1.320V/27C | pass | 0.353 | -0.3529 | 0.706 |
| fs_typ/1.080V/-40C | error | 0.01449 | -0.01437 | 0.02886 |
| fs_typ/1.080V/125C | pass | 0.1353 | -0.1351 | 0.2704 |
| fs_typ/1.080V/27C | pass | 0.05428 | -0.05498 | 0.1093 |
| fs_typ/1.200V/-40C | pass | 0.1182 | -0.1181 | 0.2362 |
| fs_typ/1.200V/125C | pass | 0.267 | -0.2669 | 0.5338 |
| fs_typ/1.200V/27C | pass | 0.19 | -0.1898 | 0.3797 |
| fs_typ/1.320V/-40C | fail | 0.2781 | -0.278 | 0.5561 |
| fs_typ/1.320V/125C | pass | 0.3857 | -0.3856 | 0.7713 |
| fs_typ/1.320V/27C | fail | 0.3348 | -0.3347 | 0.6695 |
| sf_typ/1.080V/-40C | error | 0.01621 | -0.01645 | 0.03266 |
| sf_typ/1.080V/125C | pass | 0.1382 | -0.1382 | 0.2765 |
| sf_typ/1.080V/27C | pass | 0.05777 | -0.05856 | 0.1163 |
| sf_typ/1.200V/-40C | pass | 0.1233 | -0.1235 | 0.2467 |
| sf_typ/1.200V/125C | pass | 0.2601 | -0.26 | 0.5202 |
| sf_typ/1.200V/27C | pass | 0.1921 | -0.1919 | 0.384 |
| sf_typ/1.320V/-40C | fail | 0.2728 | -0.2728 | 0.5456 |
| sf_typ/1.320V/125C | pass | 0.3686 | -0.3685 | 0.7371 |
| sf_typ/1.320V/27C | fail | 0.3239 | -0.3239 | 0.6478 |
| ss_wcs/1.080V/-40C | error | 0.0002201 | -0.0002471 | 0.0004672 |
| ss_wcs/1.080V/125C | pass | 0.04394 | -0.04347 | 0.08742 |
| ss_wcs/1.080V/27C | error | 0.006991 | -0.005692 | 0.01268 |
| ss_wcs/1.200V/-40C | error | 0.02181 | -0.02134 | 0.04315 |
| ss_wcs/1.200V/125C | pass | 0.1405 | -0.1417 | 0.2822 |
| ss_wcs/1.200V/27C | pass | 0.06278 | -0.06422 | 0.127 |
| ss_wcs/1.320V/-40C | fail | 0.1536 | -0.1552 | 0.3087 |
| ss_wcs/1.320V/125C | pass | 0.2884 | -0.2883 | 0.5767 |
| ss_wcs/1.320V/27C | fail | 0.2211 | -0.2211 | 0.4422 |
| tt_typ/1.080V/-40C | error | 0.01509 | -0.01517 | 0.03026 |
| tt_typ/1.080V/125C | pass | 0.1378 | -0.1377 | 0.2754 |
| tt_typ/1.080V/27C | pass | 0.05618 | -0.05694 | 0.1131 |
| tt_typ/1.200V/-40C | pass | 0.1193 | -0.1194 | 0.2387 |
| tt_typ/1.200V/125C | pass | 0.2648 | -0.2647 | 0.5294 |
| tt_typ/1.200V/27C | pass | 0.191 | -0.1908 | 0.3818 |
| tt_typ/1.320V/-40C | fail | 0.2746 | -0.2745 | 0.5491 |
| tt_typ/1.320V/125C | pass | 0.3781 | -0.3781 | 0.7562 |
| tt_typ/1.320V/27C | fail | 0.3296 | -0.3295 | 0.6591 |
