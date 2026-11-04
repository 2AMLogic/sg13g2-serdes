# Smoke record 20261102-165452-773bc87

Toolchain bring-up only (issue #3). Devices are placeholders, not design values.

## Pins
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0, tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- OpenVAF-Reloaded v24.0.1mob (sim/tools/build-osdi.sh)
- klt: `c572046be644e0407f693f2410f3abb799d68a3a`

## Runs

### hbt_gummel
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261102-165452-773bc87/hbt_gummel.report.json hbt_gummel.request.json`
- hbt_gummel exit=0
- status: **pass** (3/3 corners pass, 0 error)
- engine host: worker, ngspice 46 ['** ngspice-46 : Circuit level simulation program'], backend job `klt-sim-cd717b59f575`, runner klt 0.8.0

| corner | status | runtime_s | notes |
|---|---|---|---|
| hbt_typ/novdd/27C | pass | 0.116 | ic_at_0p8v=0.000139916; ib_at_0p8v=-1.75409e-07 |
| hbt_bcs/novdd/27C | pass | 0.116 | ic_at_0p8v=0.000178477; ib_at_0p8v=-1.20952e-07 |
| hbt_wcs/novdd/27C | pass | 0.115 | ic_at_0p8v=0.000104188; ib_at_0p8v=-2.31044e-07 |
- model sections exercised: hbt_bcs, hbt_typ, hbt_wcs

### mos_inv_dc
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261102-165452-773bc87/mos_inv_dc.report.json mos_inv_dc.request.json`
- mos_inv_dc exit=0
- status: **pass** (5/5 corners pass, 0 error)
- engine host: worker, ngspice 46 ['** ngspice-46 : Circuit level simulation program'], backend job `klt-sim-940145f16792`, runner klt 0.8.0

| corner | status | runtime_s | notes |
|---|---|---|---|
| tt/novdd/27C | pass | 0.269 | voh=1.2; vol=7.72861e-08; vm=0.622562 |
| ff/novdd/27C | pass | 0.266 | voh=1.2; vol=6.72594e-07; vm=0.625593 |
| ss/novdd/27C | pass | 0.267 | voh=1.2; vol=6.9846e-09; vm=0.616373 |
| fs/novdd/27C | pass | 0.317 | voh=1.2; vol=3.38543e-08; vm=0.587724 |
| sf/novdd/27C | pass | 0.367 | voh=1.2; vol=2.30489e-07; vm=0.655947 |
- model sections exercised: mos_ff, mos_fs, mos_sf, mos_ss, mos_tt

### mixed_tran
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261102-165452-773bc87/mixed_tran.report.json mixed_tran.request.json`
- mixed_tran exit=0
- status: **pass** (3/3 corners pass, 0 error)
- engine host: worker, ngspice 46 ['** ngspice-46 : Circuit level simulation program'], backend job `klt-sim-83614ad85578`, runner klt 0.8.0

| corner | status | runtime_s | notes |
|---|---|---|---|
| tt_typ/novdd/27C | pass | 5.236 | ef_max=0.482083; ef_min=-0.00450839 |
| ff_bcs/novdd/27C | pass | 5.188 | ef_max=0.472901; ef_min=-0.003198 |
| ss_wcs/novdd/27C | pass | 5.185 | ef_max=0.488271; ef_min=-0.00632159 |
- model sections exercised: hbt_bcs, hbt_typ, hbt_wcs, mos_ff, mos_ss, mos_tt

## HBT corner sections found in cornerHBT.lib
- hbt_bcs, hbt_bcs_mismatch, hbt_typ, hbt_typ_mismatch, hbt_typ_stat, hbt_wcs, hbt_wcs_mismatch
- smoke grid uses the deterministic ones: hbt_typ, hbt_bcs, hbt_wcs (the _mismatch/_stat sections are Monte Carlo variants, out of scope)
