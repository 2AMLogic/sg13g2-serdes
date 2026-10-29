# Work Log

Chronological record of merged PRs and closed issues. Maintained by the Guide role.

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
