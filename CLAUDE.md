# sg13g2-serdes — agent instructions

Open-source canary block: a single-lane 10 Gb/s-class SerDes on IHP SG13G2,
a 130 nm SiGe BiCMOS open PDK, designed and verified by AI agents.
**Mixed-signal** — HBT current-mode logic at the high-speed edge, CMOS logic
behind it — so both flows apply.

- **PDK**: IHP SG13G2 (open PDK, IHP-GmbH/IHP-Open-PDK). Analog: xschem +
  ngspice. Digital: cocotb + Icarus, Yosys, OpenROAD. Layout, DRC, and LVS
  through klayout-tools (`klt`) in both cases. The sibling SG13G2 canaries
  (`sg13g2-vco`, `sg13g2-pll`, `sg13g2-lna`) have already brought up the
  device models and the starter DRC/LVS deck; start from their setup, and
  expect HBT extraction and LVS to be where the deck is thinnest.
- **The link, not the blocks, is the risk.** Each CML stage can be simulated
  on its own; a 10 Gb/s link cannot be proven by one transistor-level
  transient. A credible claim needs a chain: transistor-level PVT results for
  each stage → behavioural models fitted to those results → a statistical
  link simulation over the declared channel model → an extrapolated bathtub.
  Every model in that chain cites the transistor-level record it was fitted
  to; an eye or BER figure that does not trace back is not evidence. The CDR
  loop and the high-speed pads (capacitance, ESD, the core-to-pad seam at
  5 GHz) are where it is most likely to fail. Expect the tools to be weakest
  there and file accordingly.
- **Scope discipline.** This repo has no `consumes:` edge. Do not design a
  PLL or VCO here. Specify the clock this block needs — frequency, phase
  count, duty-cycle and jitter budget — and compare it against the sibling
  candidates by name (`sg13g2-vco`'s ratified LC band, `sg13g2-pll`'s band,
  the LC PLL canary opened alongside this one). If none meets the
  requirement, say so in the spec and file the requirement on the sibling;
  a mismatch nobody wrote down is the failure mode `2am/REUSE.md` exists to
  prevent.
- **Friction protocol (the canary's job)**: every time klayout-tools is
  awkward, missing a capability, or wrong for what you need, file an issue at
  `2AMLogic/klayout-tools` describing the tool gap generically — that tracker
  is scoped to the tool, so keep design-specific detail out of it and describe
  the gap, not the design.
- **Verification is the product**: no claim without a testbench. PVT corners
  on every recorded analog result; recorded results are append-only evidence.
  A simulated or extrapolated BER is never called measured.
- Spec changes go through `spec/` with a decision record; agents do not relax
  the ratified spec to make results pass.
- **10 Gb/s is the target.** 5 Gb/s is the fallback and 12.5 Gb/s a stretch.
  Do not let 12.5 Gb/s requirements drive architecture before 10 Gb/s closes.

<!-- BEGIN LOOM ORCHESTRATION -->
This repository uses [Loom](https://github.com/rjwalters/loom) for AI-powered development orchestration — see the Loom repository for the full guide (roles, labels, worktrees, configuration). When installed, Loom also writes a locally-substituted copy of that guide to `.loom/CLAUDE.md`.

Work is coordinated through `loom:` labels on issues and pull requests, and the same roles run either under `loom-daemon` or by hand in an attended session — daemon mode is optional. Create the labels once with `.loom/scripts/sync-labels.sh` (an install ships `.github/labels.yml` but does not create the labels on the forge). A pull request ready for review carries `loom:review-requested`; Judge reviews it and applies `loom:pr` (approved) or `loom:changes-requested`; Doctor fixes a `loom:changes-requested` pull request and returns it to `loom:review-requested`. Only a `loom:pr` pull request gets merged, and always via this repo's merge script (`.loom/scripts/merge-pr.sh`) — never a raw forge merge command such as `gh pr merge`. Full state machine: `.loom/docs/label-state-machine.md`.
<!-- END LOOM ORCHESTRATION -->

<!-- BEGIN REPO-SKILLS -->
This repository has [Repo Skills](https://github.com/rjwalters/repo) v0.24.3 installed —
general repository hygiene and environment commands invoked as `/repo:<command>`. Run
`/repo:help` for the command list, or see `.claude/skills/repo/SKILL.md` for the full
guide. Hygiene commands apply safe, reversible fixes by default and report each
change; run with `--ask` to review first, and `--prune` to allow irreversible
removals. Managed by `install.sh` — edit outside the markers only.
<!-- END REPO-SKILLS -->
