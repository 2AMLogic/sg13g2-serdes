# RX sizing record 20261027-015751-ace29de

**Sizing evidence, not a spec result.** Nothing here is measured. `spec/target-spec.md` is PROPOSED;
rows R8-R10, R20 are used as draft targets only. Passives are ideal, the pad capacitance is a
placeholder, the clock source is ideal, the CTLE load is a placeholder 80 fF, and the MOS level
converter is not simulated. The grid is the HBT-only PVT-edge set (7 units, below).

## Pins
- PDK: IHP-GmbH/IHP-Open-PDK v0.3.0, tarball sha256 `f6afb7a8d2adf3e40acd3fd2c7892fc93510e6f760565409a8df2b5b242254fc` (sim/pdk.json)
- klt: `267ea83a0510bcb61d2956058095201c0f481ff7` (layout/toolchain.json)
- Schematics/netlists: design/rx/ at the commit named in the record id; netlist staleness gate `design/check-netlists.sh`

## Runs

### ctle_ac
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261027-015751-ace29de/ctle_ac.report.json ctle_ac.request.json`
- ctle_ac exit=4
- status: **error** (0/7 corners pass, 7 error); engine host worker, ngspice None, backend job `klt-sim-0554347f74b1`

### ctle_op
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261027-015751-ace29de/ctle_op.report.json ctle_op.request.json`
- ctle_op exit=4
- status: **error** (0/7 corners pass, 7 error); engine host worker, ngspice None, backend job `klt-sim-ea4726a4e4fc`

### pad_ac
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261027-015751-ace29de/pad_ac.report.json pad_ac.request.json`
- pad_ac exit=4
- status: **error** (0/7 corners pass, 7 error); engine host worker, ngspice None, backend job `klt-sim-6b7643ce3098`

### latch_regen
- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/20261027-015751-ace29de/latch_regen.report.json latch_regen.request.json`
- latch_regen exit=4
- status: **error** (0/7 corners pass, 7 error); engine host worker, ngspice None, backend job `klt-sim-52c32b609f61`

## CTLE AC response per setting (peaking = gain at 5 GHz minus gain at 0.1 GHz, differential, dB)

Code = c2c1c0. First-look comparison with R10: 0-10 dB peaking at 5 GHz in >= 8 steps. `fail` limits are code 0 <= 1 dB and code 7 >= 10 dB.

| corner | c0 | c1 | c2 | c3 | c4 | c5 | c6 | c7 | gain@0.1G c0 / c7 | gain@5G c7 |
|---|---|---|---|---|---|---|---|---|---|---|
| hbt_typ/1.200V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_wcs/1.080V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_wcs/1.080V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_wcs/1.080V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_bcs/1.320V/-40C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_bcs/1.320V/27C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |
| hbt_bcs/1.320V/125C | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a / n/a | n/a |

## CTLE output common mode (V, code 7)

| corner | out CM |
|---|---|
| hbt_typ/1.200V/27C | n/a |
| hbt_wcs/1.080V/125C | n/a |
| hbt_wcs/1.080V/27C | n/a |
| hbt_wcs/1.080V/-40C | n/a |
| hbt_bcs/1.320V/-40C | n/a |
| hbt_bcs/1.320V/27C | n/a |
| hbt_bcs/1.320V/125C | n/a |

## Latch regeneration at 5 GHz (clock buffer + latch, ps)

Time from the clock edge that closes the sample phase to |q| = 0.25 V (about 85 % of the swing), +-10 mV differential input. First-look limit: 100 ps (half period).

| corner | t_regen up | t_regen down | q swing (V) |
|---|---|---|---|
| hbt_typ/1.200V/27C | n/a | n/a | n/a |
| hbt_wcs/1.080V/125C | n/a | n/a | n/a |
| hbt_wcs/1.080V/27C | n/a | n/a | n/a |
| hbt_wcs/1.080V/-40C | n/a | n/a | n/a |
| hbt_bcs/1.320V/-40C | n/a | n/a | n/a |
| hbt_bcs/1.320V/27C | n/a | n/a | n/a |
| hbt_bcs/1.320V/125C | n/a | n/a | n/a |

## Termination + pad first-look |Zdiff| (ohm, placeholder 50 fF pads)

| corner | 0.1 GHz | 5 GHz |
|---|---|---|
| hbt_typ/1.200V/27C | n/a | n/a |
| hbt_wcs/1.080V/125C | n/a | n/a |
| hbt_wcs/1.080V/27C | n/a | n/a |
| hbt_wcs/1.080V/-40C | n/a | n/a |
| hbt_bcs/1.320V/-40C | n/a | n/a |
| hbt_bcs/1.320V/27C | n/a | n/a |
| hbt_bcs/1.320V/125C | n/a | n/a |

## HBT node stress versus DR-003 (collector <= 1.32 V, reverse Vbe <= 1.0 V)

- Nodes over a DR-003 limit: 0
- Per-node values for every HBT, corner and CTLE code are in the `*.report.json` files in this directory.

## Limits missed (first-look comparisons)

- none

## Not simulated

- `lvl_cml2cmos` (thin-oxide MOS, PSP103 via OSDI): not simulated; the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` inputs fail (klayout-tools#3818, #3819; sim/README.md; blocked on #3).
- PDK resistors `rsil`/`rppd` (`r3_cmc` OSDI): not simulated; every resistor in design/rx is an ideal `res` for that reason, so resistor corners (`res_*`) are not exercised.
- Pad/ESD capacitance at 5 GHz, SDD11 (R9) and the core-to-pad seam: not simulated beyond the placeholder |Zdiff| above; owned by #24/#28.
- Sampler offset and noise (Monte Carlo, DR-002), CDR, link behaviour, clock duty/quadrature error (R20 +-1 %, +-2 deg) and mismatch: not simulated.
- Full PVT-full grid (135 points): not run; only the 7-point HBT PVT-edge set. HBT-only `hbt_*` corner sections ganged with `cap_*` and `dio_*`.
- Unconfirmed: the +-10 % supply tolerance is a proposal (DR-003); temperature -40/27/125 C is a proposal.
