# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide role.

### 2026-11-12

- **Issue #24** (closed): T1 item 2 (layout, analog): GDS for the CML TX/RX cells, clock path and high-speed pads
- **Issue #105** (closed): rtl: apply DR-009 CDR loop gain (KP=8, KI=0) and regenerate synth/P&R records

### 2026-11-11

- **PR #122**: refactor(layout): share netlist parser, klt runner and um() across analog generators
- **Issue #119** (closed): Consolidate duplicated netlist parser, um() and klt runner across the three analog layout generators
- **PR #120**: feat(layout): analog top assembly of TX/RX core and pad cells with item 2 attestation
- **PR #118**: fix: run RX layout regen with the repo-local .venv python
- **PR #116**: feat(layout): pad_esd and rx_term_pad pad cells from PDK bondpad/ESD cells
- **PR #115**: feat(layout): generate RX core analog cells with a re-runnable klt generator
- **PR #114**: feat(layout): generate TX core analog cells with port-named pins
- **PR #109**: fix(bench): remove duplicated phrase in top-bench R11 limitations string
- **PR #108**: fix(sim): count nt votes in noise-free CDR loop analysis; DR-010 supersedes DR-007 numbers
- **PR #107**: feat(sim): attribute CDR dither closure and propose KP=8 KI=0 loop fix (DR-009)
- **PR #104**: feat(sim): add R6 return-loss and R20 clock-quality analog benches
- **Issue #117** (closed): layout/analog/rx: regen.sh needs klayout.db under plain python3 -I; not provided by setup-env
- **Issue #113** (closed): T1 item 2 (layout, analog): pad/ESD cells and analog top assembly with item-2 attestation
- **Issue #112** (closed): T1 item 2 (layout, analog): RX core cell layouts (CTLE, CML latch, clock buffer quad, level converter)
- **Issue #111** (closed): x
- **Issue #110** (closed): T1 item 2 (layout, analog): TX core cell layouts (bias, ffe_en, mux, predriver, driver_ffe, level converter)
- **Issue #106** (closed): scripts/cdr-loop-analysis.py counts one vote per word when noise-free (DR-007 noise-free columns wrong)
- **Issue #102** (closed): Follow-on from PR #100: 1e-12 eye closes once CDR dither is included (R12/R15)
- **Issue #101** (closed): Fix garbled limitations text for the digital top bench in sim/bench/benches.json
- **Issue #92** (closed): T1 item 9 follow-up: analog benches for R6 (TX return loss) and R20 (receiving-buffer clock quality)
- **PR #100**: feat(sim): add behavioural link benches for R8, R11, R12, R13, R15
- **Issue #93** (closed): T1 item 9 follow-up: behavioural/statistical benches for R8, R11, R12, R13 and R15

### 2026-11-10

- **PR #97**: feat(layout): digital-partition place-and-route flow and routed GDS record
- **PR #96**: docs(sim/tx): state why the 0.4 V mux clock swing is unvalidated and what closes it
- **PR #95**: sim: ship testbench registry, run-bench.sh cold start and item-9 attestation
- **PR #91**: sim: cap TX MOS request timeout_s at 75 s and record 135-unit re-run
- **Issue #80** (closed): sim/tx: add batch-fleet sizing benches for the MOS cells mux2to1_cml, ffe_en, tx_lvl_cml2cmos
- **Issue #28** (closed): T1 item 9 (testbenches shipped): one bench per simulation-graded spec row, with cold-start docs and --attest 9
- **Issue #25** (closed): T1 item 2 (layout, digital): routed GDS of the CMOS partition from a committed klt place-and-route flow
- **PR #89**: build: bump klayout-tools pin to 0.9.0 and record TX MOS-cell fleet run
- **Issue #23** (closed): T1 item 1 (design sources, digital): serializer/deserializer, PRBS, CDR loop filter RTL plus sg13g2 netlist

### 2026-11-07

- **PR #85**: Merge pull request: chore: Bump Repo Skills 0.25.1 -> 0.25.10

### 2026-11-06

- **PR #83**: refactor(sim): share record renderer boilerplate in sim/tools/record_common.py
- **PR #81**: feat(sim/tx): add batch-fleet sizing benches for the TX MOS cells
- **Issue #82** (closed): Consolidate duplicated boilerplate across the four sim make_record*.py renderers

### 2026-11-04

- **PR #75**: docs(spec): refresh clock fit table and reconcile serializer stage boundaries

### 2026-11-02

- **PR #76**: sim: record passing batch smoke grid on klt 0.8.0
- **Issue #3** (closed): PDK and simulator bring-up: pin SG13G2, build the OSDI models, smoke-simulate MOS and HBT models

### 2026-11-01

- **PR #71**: refactor(design): share xschem pin-offset table between TX and RX generators
- **Issue #69** (closed): Consolidate duplicated xschem emitters in tx/rx gen_schematics.py
- **PR #68**: feat(signoff): attest T1 item 1 for analog and digital partitions (partial increment of #23)
- **PR #35**: feat: add TX CML path schematics, netlists, PVT-edge sizing record and R3 finding
- **Issue #21** (closed): T1 item 1 (design sources, analog): TX CML final mux, pre-driver, FFE line driver and pad/ESD schematics
- **PR #64**: docs(spec): add DR-007 CDR loop delay analysis
- **PR #63**: feat(rtl): pipeline the digital partition to meet the 1.6 ns word clock pre-layout
- **Issue #62** (closed): Write the CDR loop analysis and check the 7-clock digital loop delay against it
- **Issue #36** (closed): Restructure digital partition RTL to close 625 MHz timing (DR-005)
- **PR #60**: Bump Repo Skills 0.24.7 -> 0.25.1
- **PR #37**: feat: record gate-level STA of the digital partition and route the 625 MHz miss
- **Issue #32** (closed): Digital partition: demonstrate or re-budget 625 MHz timing (no gate-level STA yet)

### 2026-10-31

- **PR #38**: fix(ci): wire package.json checks to the real synth-freshness and cocotb gates
- **Issue #31** (closed): Replace always-green package.json check stubs with the repo's real checks

### 2026-10-29

- **PR #54**: ci: fail check-ci when klt pins in klt-pin.env and toolchain.json differ
- **Issue #50** (closed): Dedupe klt version pin: scripts/klt-pin.env duplicates layout/toolchain.json

### 2026-10-28

- **PR #51**: feat: attest T1 item 10 repo hygiene via klt signoff --attest
- **Issue #49** (closed): T1 item 10 (repo hygiene): klt signoff --attest 10 envelope cited for both partitions

### 2026-10-27

- **PR #45**: docs: add EE-key and market-key ratification directories
- **PR #43**: build: bump klayout-tools pin to 0.8.0 (PyPI) and verify by version
- **Issue #42** (closed): Bump klayout-tools pin 0.7.0, 267ea83a0510 → 0.8.0
- **PR #6**: ci: add check-ci gate and graded klt signoff manifest
- **Issue #4** (closed): Repo hygiene and CI (T1 item 10): real CI checks, a graded klt signoff manifest, README spec-issue fix
- **PR #34**: feat(rx): record the HBT PVT sizing grid for the RX path
- **PR #30**: feat: add CMOS digital-partition RTL, benches and committed gate-level netlist
- **Issue #22** (closed): T1 item 1 (design sources, analog): RX termination, CTLE, four CML sampling latches and 5 GHz clock path

### 2026-10-22

- **Issue #14** (closed): Remove unused sim harness import from reuse.lock.json and setup-env.sh

### 2026-10-21

- **PR #15**: Bump Repo Skills 0.24.3 -> 0.24.7

### 2026-10-18

- **PR #12**: chore(config): remove unread toolchain.json keys, derive PDK_ROOT from sim/pdk.json
- **PR #10**: refactor(sim): read OpenVAF pin from build-osdi.sh, drop duplicate pdk.json block
- **Issue #11** (closed): Remove unread keys from toolchain.json files: floors that setup-env.sh never checks
- **Issue #9** (closed): Remove duplicated OSDI pin block from sim/pdk.json: second source of truth for evidence records

### 2026-10-17

- **PR #8**: feat(sim): pin SG13G2 PDK/OSDI toolchain, add setup script and HBT/MOS smoke grid
- **PR #7**: docs(spec): propose SerDes target spec, clock requirement, channel model and decision records
- **PR #1**: chore(loom): Install Loom 0.19.1180
