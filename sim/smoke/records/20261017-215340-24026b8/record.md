# Smoke record 20261017-215340-24026b8

Toolchain bring-up only (issue #3). Devices are placeholders, not design values.

## Pins
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0, tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- OpenVAF-Reloaded v24.0.1mob (sim/tools/build-osdi.sh)
- klt: `267ea83a0510bcb61d2956058095201c0f481ff7`

## Runs

### hbt_gummel
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261017-215340-24026b8/hbt_gummel.report.json hbt_gummel.request.json`
- hbt_gummel exit=0
- status: **pass** (3/3 corners pass, 0 error)
- engine host: worker, ngspice 46 ['** ngspice-46 : Circuit level simulation program'], backend job `klt-sim-358db04e702f`, runner klt 0.7.0

| corner | status | runtime_s | notes |
|---|---|---|---|
| hbt_typ/novdd/27C | pass | 0.115 | ic_at_0p8v=0.000139916; ib_at_0p8v=-1.75409e-07 |
| hbt_bcs/novdd/27C | pass | 0.117 | ic_at_0p8v=0.000178477; ib_at_0p8v=-1.20952e-07 |
| hbt_wcs/novdd/27C | pass | 0.116 | ic_at_0p8v=0.000104188; ib_at_0p8v=-2.31044e-07 |
- model sections exercised: hbt_bcs, hbt_typ, hbt_wcs

### mos_inv_dc
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261017-215340-24026b8/mos_inv_dc.report.json mos_inv_dc.request.json`
- mos_inv_dc exit=4
- status: **error** (0/5 corners pass, 5 error)
- engine host: worker, ngspice None [], backend job `klt-sim-931eea654dac`, runner klt None

| corner | status | runtime_s | notes |
|---|---|---|---|
| tt/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-931eea654dac finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| ff/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-931eea654dac finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| ss/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-931eea654dac finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| fs/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-931eea654dac finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| sf/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-931eea654dac finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
- model sections exercised: mos_ff, mos_fs, mos_sf, mos_ss, mos_tt

### mixed_tran
- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/20261017-215340-24026b8/mixed_tran.report.json mixed_tran.request.json`
- mixed_tran exit=4
- status: **error** (0/3 corners pass, 3 error)
- engine host: worker, ngspice None [], backend job `klt-sim-66b1ab3f6f73`, runner klt None

| corner | status | runtime_s | notes |
|---|---|---|---|
| tt_typ/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-66b1ab3f6f73 finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| ff_bcs/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-66b1ab3f6f73 finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
| ss_wcs/novdd/27C | error | 0.0 | batch_job_failed: batch job klt-sim-66b1ab3f6f73 finished 'failed' without a usable report: job command exited 2 [output recovery: collected outputs hold no rep |
- model sections exercised: hbt_bcs, hbt_typ, hbt_wcs, mos_ff, mos_ss, mos_tt

## HBT corner sections found in cornerHBT.lib
- hbt_bcs, hbt_bcs_mismatch, hbt_typ, hbt_typ_mismatch, hbt_typ_stat, hbt_wcs, hbt_wcs_mismatch
- smoke grid uses the deterministic ones: hbt_typ, hbt_bcs, hbt_wcs (the _mismatch/_stat sections are Monte Carlo variants, out of scope)
