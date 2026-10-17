# sg13g2-serdes

A single-lane 10 Gb/s-class serializer/deserializer on
[IHP SG13G2](https://github.com/IHP-GmbH/IHP-Open-PDK), a 130 nm SiGe BiCMOS
open PDK — CMOS for the parallel and control logic, SiGe HBT current-mode
logic for the high-speed edge — designed by AI agents driving
[klayout-tools](https://github.com/2AMLogic/klayout-tools), xschem + ngspice
on the analog side and Yosys/OpenROAD on the digital side.

**Status: just opened, specification phase.** Nothing is designed yet.

**Built agent-native.** Every specification, decision record, testbench, and
line of documentation here is produced by AI agents working from a ratified
spec and an append-only evidence trail — not human-authored work that agents
merely assisted with. Verification is the product: every claim traces to a
recorded result under PVT corners. Where the agents hit friction with the
open-source tooling — most often
[klayout-tools](https://github.com/2AMLogic/klayout-tools) — that friction is
filed as a public issue against the tool itself, so the fix benefits everyone
using SG13G2, not just this repo.

## Why this block, on this node

A multi-gigabit SerDes is one of the most common blocks in a modern chip
and, to our knowledge, one with no open-source design that has published
measured silicon results on any open PDK. It is also a hard one to do in
130 nm CMOS: at 10 Gb/s a half-rate architecture needs 5 GHz clocks and
latches that resolve in a fraction of a 100 ps unit interval.

SG13G2 changes that arithmetic. Its SiGe HBTs are high-speed devices
alongside ordinary CMOS, so the last serializer stage, the line driver, the
receiver's front end and the decision latches can be bipolar current-mode
logic while everything slower stays CMOS. The block is a test of the PDK's
distinguishing devices in a role that CMOS at this node struggles to fill.

## Scope

- **In scope**: TX serializer and CML line driver with feed-forward
  equalization; RX termination, continuous-time linear equalizer, sampling
  latches, clock-and-data recovery and deserializer; on-chip PRBS generator
  and checker; loopback modes; the high-speed pad cells and their ESD.
- **From siblings**: the reference/high-speed clock synthesis. This repo has
  no `consumes:` edge yet; it specifies the clock it needs (frequency,
  phases, jitter budget) and the spec issue names the sibling candidates.
  Do not design a PLL or VCO here.
- **Not in scope**: line coding (8b/10b, 64b/66b) and any protocol layer —
  the block moves raw bits and proves them with PRBS.

## Target specification (PROPOSED — operator to ratify, see issue #2)

The target specification is in [`spec/`](spec/README.md): the
[parameter table](spec/target-spec.md) (10 Gb/s target, 5 Gb/s fallback,
12.5 Gb/s stretch, each with verification and PVT corners), the
[clock requirement](spec/clock-requirement.md), the
[channel model](spec/channel/README.md) and the
[decision records](spec/decisions/). It is a proposal until the operator
ratifies it by merge.

Every error-rate figure in this repo is simulated or extrapolated until
silicon exists, and says so.

Maturity ladder: spec ratified → TX and RX building blocks simulated across
PVT → link simulated end to end over the channel model → pads DRC-clean →
assembled and LVS-clean → post-layout re-verification → shuttle seat →
measured silicon. **Current position: pre-spec.**

## Repo layout

```
spec/          ratified spec + decision records
rtl/           PRBS, serializer/deserializer control, CDR logic
verification/  cocotb testbenches
design/        analog schematics (CML stages, driver, CTLE, latches)
sim/           testbenches + PVT corner results (ngspice), link-level eye studies
layout/        GDS + DRC/LVS reports, including the pad cells
measurements/  silicon characterization (empty until tape-out)
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
