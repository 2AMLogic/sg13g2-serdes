# TX MOS-cell sizing record 20261106-054913-a506fea-mos

**Sizing evidence, not a spec result and not a measurement.** Simulated, first-cut sizes, ideal-source drive. No `spec/` row is graded here.

## Pins and inputs
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0 (sim/pdk.json), tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc`
- klt: `c572046be644e0407f693f2410f3abb799d68a3a`
- `tx_mos_mux2to1_cml.sp` sha256 `d2fb5ffc8337849ed1fb2d95228b30c09ac5878006eb8035aa1e36d9ffe37ba0`, `tx_mos_mux2to1_cml.request.json` sha256 `0ab6e683d314680f36bc057b5d41bdeaa7d8160e54744320e7f35ec6ad93e3db`
- netlist `design/tx/netlists/mux2to1_cml.spice` sha256 `612cb14e2bb4526e87ed79c5799034d8993f7c936f58c00f38fc622c92a22adc`
- `tx_mos_tx_lvl_cml2cmos.sp` sha256 `1b14cddbe75dbbad1f01d3be030568a80c89899fd23df5ddd61371ef4a525674`, `tx_mos_tx_lvl_cml2cmos.request.json` sha256 `f40130de0e53707e462a392d2d010bc72f87d443c7cdcc8c5bfa5892e9fc6872`
- netlist `design/tx/netlists/tx_lvl_cml2cmos.spice` sha256 `fa1f86408c106ca6fa3f6069004398d97a9a129a86049ff28519c34466f1b5d9`
- `tx_mos_ffe_en.sp` sha256 `aff84b6e7f59fb900b9e523f8df3be6a2b2b5683cac8050255c8ebe7ab9aac97`, `tx_mos_ffe_en.request.json` sha256 `ff82b67df8752f956a7a7b0b8b6c60b41868638080b17504cf4264e770f4bf25`
- netlist `design/tx/netlists/ffe_en.spice` sha256 `1d3f8b9d5b58779edb3aa9776a635327dc42f69739bf2ae0d920ffecff4f1094`
- bias cell netlists also inlined: `bias`, `predriver` (mux bench), `bias` (ffe_en bench)

## Run
- tx_mos_ffe_en exit=4; tx_mos_mux2to1_cml exit=4; tx_mos_tx_lvl_cml2cmos exit=4
- mux2to1_cml: status **error** (0/45 corners pass, 0 fail, 45 error), backend job `klt-sim-20fa2aae69e2`
- tx_lvl_cml2cmos: status **error** (0/45 corners pass, 0 fail, 45 error), backend job `klt-sim-14847858d4ab`
- ffe_en: status **error** (0/45 corners pass, 0 fail, 45 error), backend job `klt-sim-f58bb02c6b1e`

## Failing or erroring corners (kept, not dropped)

- mux2to1_cml/tt_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.080V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.080V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.200V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.200V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.320V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/tt_typ/1.320V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.080V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.080V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.080V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.200V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.200V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.200V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.320V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.320V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ff_bcs/1.320V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.080V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.080V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.080V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.200V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.200V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.200V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.320V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.320V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/ss_wcs/1.320V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.080V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.080V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.200V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.200V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.320V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/fs_typ/1.320V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.080V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.080V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.200V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.200V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.320V/27C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- mux2to1_cml/sf_typ/1.320V/125C: error batch_job_failed batch job klt-sim-20fa2aae69e2 finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.080V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.080V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.200V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.200V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.320V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/tt_typ/1.320V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.080V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.080V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.080V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.200V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.200V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.200V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.320V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.320V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ff_bcs/1.320V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.080V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.080V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.080V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.200V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.200V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.200V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.320V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.320V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/ss_wcs/1.320V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.080V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.080V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.200V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.200V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.320V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/fs_typ/1.320V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.080V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.080V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.200V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.200V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.320V/27C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- tx_lvl_cml2cmos/sf_typ/1.320V/125C: error batch_job_failed batch job klt-sim-14847858d4ab finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.080V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.080V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.200V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.200V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.320V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/tt_typ/1.320V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.080V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.080V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.080V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.200V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.200V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.200V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.320V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.320V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ff_bcs/1.320V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.080V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.080V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.080V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.200V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.200V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.200V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.320V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.320V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/ss_wcs/1.320V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.080V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.080V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.200V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.200V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.320V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/fs_typ/1.320V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.080V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.080V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.080V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.200V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.200V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.200V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.320V/-40C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.320V/27C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli
- ffe_en/sf_typ/1.320V/125C: error batch_job_failed batch job klt-sim-f58bb02c6b1e finished 'failed' (job command exited 87): the job's klt reported: the fleet runner runs klt 0.9.0 but the submitting client is 0.8.0 -- the request was not run (update the runner image or use a compatible cli

## mux2to1_cml (5 GHz clock, A=1/B=0, 10 Gb/s 1010 output)

| corner | out max (V) | out min (V) | cm (V) | rise (ps) | fall (ps) | Idd (mA) | sq_a hi/lo (V) |
|---|---|---|---|---|---|---|---|
| ff_bcs/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ff_bcs/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| fs_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| sf_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| ss_wcs/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |
| tt_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a |

Rise/fall are the time between the fixed +-30 mV differential crossings, NOT a conforming 20-80 % figure (ngspice cannot reference an earlier `.meas` as a threshold). 'n/a' = no crossing in the window (swing under 30 mV or no edge).

### Node stress (R3: collector <= 1.32 V, reverse Vbe <= 1.0 V)

| check | worst value (V) | limit (V) | corner |
|---|---|---|---|

- nodes beyond the R3 limits in this grid: **0**

Informational Vce max per mux HBT (open-base BVCEO is 1.4 V):


## tx_lvl_cml2cmos (2.5 GHz input, 20 fF load)

| corner | out hi (V) | out lo (V) | duty (%) | tpd LH (ps) | tpd HL (ps) | Idd (mA) |
|---|---|---|---|---|---|---|
| ff_bcs/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a |

Duty = time above vdd/2 over the period (`t_high_s` / `t_period_s`). Delay is from the differential input zero crossing to the output vdd/2 crossing. 'n/a' = no crossing.

## ffe_en (vbp0..2 minus vbn at each enable code; slices enabled = 0..3)

| corner | code | vbn (V) | vbp0-vbn (V) | vbp1-vbn (V) | vbp2-vbn (V) |
|---|---|---|---|---|---|
| ff_bcs/1.080V/-40C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/-40C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/-40C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/-40C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/125C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/125C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/125C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/125C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/27C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/27C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/27C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.080V/27C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/-40C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/-40C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/-40C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/-40C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/125C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/125C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/125C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/125C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/27C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/27C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/27C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.200V/27C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/-40C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/-40C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/-40C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/-40C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/125C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/125C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/125C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/125C | 3 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/27C | 0 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/27C | 1 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/27C | 2 | n/a | n/a | n/a | n/a |
| ff_bcs/1.320V/27C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/-40C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/-40C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/-40C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/-40C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/125C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/125C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/125C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/125C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/27C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/27C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/27C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.080V/27C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/-40C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/-40C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/-40C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/-40C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/125C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/125C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/125C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/125C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/27C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/27C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/27C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.200V/27C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/-40C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/-40C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/-40C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/-40C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/125C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/125C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/125C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/125C | 3 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/27C | 0 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/27C | 1 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/27C | 2 | n/a | n/a | n/a | n/a |
| fs_typ/1.320V/27C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/-40C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/-40C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/-40C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/-40C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/125C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/125C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/125C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/125C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/27C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/27C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/27C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.080V/27C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/-40C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/-40C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/-40C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/-40C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/125C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/125C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/125C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/125C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/27C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/27C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/27C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.200V/27C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/-40C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/-40C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/-40C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/-40C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/125C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/125C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/125C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/125C | 3 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/27C | 0 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/27C | 1 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/27C | 2 | n/a | n/a | n/a | n/a |
| sf_typ/1.320V/27C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/-40C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/-40C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/-40C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/-40C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/125C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/125C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/125C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/125C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/27C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/27C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/27C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.080V/27C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/-40C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/-40C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/-40C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/-40C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/125C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/125C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/125C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/125C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/27C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/27C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/27C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.200V/27C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/-40C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/-40C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/-40C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/-40C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/125C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/125C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/125C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/125C | 3 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/27C | 0 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/27C | 1 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/27C | 2 | n/a | n/a | n/a | n/a |
| ss_wcs/1.320V/27C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/-40C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/-40C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/-40C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/-40C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/125C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/125C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/125C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/125C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/27C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/27C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/27C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.080V/27C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/-40C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/-40C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/-40C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/-40C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/125C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/125C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/125C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/125C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/27C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/27C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/27C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.200V/27C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/-40C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/-40C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/-40C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/-40C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/125C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/125C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/125C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/125C | 3 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/27C | 0 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/27C | 1 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/27C | 2 | n/a | n/a | n/a | n/a |
| tt_typ/1.320V/27C | 3 | n/a | n/a | n/a | n/a |

An enabled slice has vbp = vbn (difference near 0); a disabled one is pulled low through the 1 kohm series resistor. vbp is unloaded.

## Corners and what is simulated

- Process pairing (MOS / HBT / CAP / RES sections ganged): tt/typ, ff/bcs, ss/wcs, and fs and sf both with the typical HBT/CAP/RES (no HBT skew exists for them), x supply 1.08/1.2/1.32 V x -40/27/125 C = 45 corners per cell. Mismatch/Monte Carlo is not run.
- MOS is PSP103 and the PDK `rsil`/`rppd` are the real `r3_cmc` models, loaded via `osdi_preload` as in `sim/smoke/`. No behavioural resistor is used in these benches (the six HBT-bench decks still use the stand-in).
- Inputs are ideal sources: a 0.4 V-swing 5 GHz clock (an assumption, not a spec value) and 300 mV vdd-referenced CML levels. Loads are lumped (predriver input, 20 fF). Resistor current-density limits are not checked.
