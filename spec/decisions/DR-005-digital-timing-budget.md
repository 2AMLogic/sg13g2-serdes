# DR-005: Digital partition misses the 1.6 ns word-clock budget

- **Status**: proposed
- **Date**: 2026-10-27
- **Decided by**: builder (issue #32); ratification needs a human or Champion

Records are append-only: a ratified record is never rewritten; a new record
says what it supersedes.

## Context

DR-001 decision 3 puts everything at or below 625 MHz in CMOS, a 1.6 ns word
clock. Issue #32 asked for gate-level static timing of the digital partition
(PR #30 had only ABC's ~3.0 ns wire-less estimate).

Measured by `scripts/sta-paths.sh` on the committed netlist
(`rtl/synth/serdes_digital_top_synth.v`, sha256 303ba30a...): OpenSTA 26Q3 via the
pinned `klt sta`, SG13G2 `sg13g2_stdcell` `typ_1p20V_25C`, ideal clock, no wire
load, no placement. Evidence: `rtl/synth/sta/`. This is a pre-layout estimate;
layout parasitics and clock skew will only add to it. One corner only (the
issue's scope), so no PVT claim.

| Endpoint module | Worst setup slack | Path |
|---|---|---|
| `serdes_prbs_chk` | -2.09 ns | 3.57 ns: `serdes_ctrl` flop -> XOR/mux chain, 22 cells -> counter/lock flop |
| `serdes_cdr_pd` | -2.03 ns | 3.51 ns, also launched from a `serdes_ctrl` flop |
| `serdes_eye_mon` | -0.95 ns | 2.43 ns: 10-deep AND4 chain (counter compare) |
| `serdes_cdr_filter` | -0.51 ns | 1.99 ns: 15-cell carry chain, flop to flop |
| `serdes_loopback`, `serdes_ctrl` | -0.02 ns | |
| `serdes_prbs_gen` | +0.04 ns (met) | |

Whole partition: fmax 270.7 MHz, 157 violating setup endpoints, hold clean
(+0.24 ns). Of the two worst paths, both start at `serdes_ctrl` configuration
flops (register-file bits; the netlist does not name which) that may be quasi-static; whether they
may be timed as multicycle is a design statement nobody has made, and no
constraint was added to hide them here.

## Options considered

1. **Restructure the RTL to meet 1.6 ns.** Pipeline the PRBS-31 checker
   compare and counter update, register the configuration fan-out and PD
   decode, replace the eye-monitor compare with a down-counter, and
   carry-save or pipeline the loop-filter accumulator. Keeps DR-001, costs
   latency and area, and the CDR loop gets extra delay that DR-001/loop
   analysis must re-check (loop latency lowers phase margin). Needed amount:
   roughly 2.1 ns off the worst path, i.e. ~7-8 logic levels instead of ~22.
2. **Declare configuration registers quasi-static (multicycle/false paths)**
   and restructure only what remains (eye monitor, loop filter, checker data
   path). Needs a documented register-write protocol (the host never changes
   mode while the checker runs) and an SDC the tools honour.
3. **Narrow the budget:** 32:1 / 312.5 MHz word clock (3.2 ns), already listed
   in DR-001 as "fine for timing" with a wider datapath. A spec change.
4. **Leave as is.** Not viable: the partition cannot be claimed to run the
   16:1 / 625 MHz rate.

## Decision

Proposed: pursue option 2 then 1 (keep 16:1 / 625 MHz) in a follow-up RTL
issue; fall back to option 3 only if that fails. **This record does not change
the ratified spec**; the target stays 1.6 ns until a human ratifies a superseding
record. Until then 625 MHz is *not demonstrated* for the digital partition.

## Consequences

- No RTL changed in this record, so `rtl/synth/` is unchanged and
  `scripts/check-synth-fresh.sh` passes.
- Follow-up issue #36: restructure per options 1-2 and re-run `scripts/sta-paths.sh`.
- Any claim about the digital block at 625 MHz must cite `rtl/synth/sta/`.
- Tool gap: `klt synthesize`'s integrated `sta` cannot analyse a hierarchical
  netlist and needs a Rust extension built from source; filed upstream as 2AMLogic/klayout-tools#4224.
