# DR-005: TX stages with resistor loads to the rail cannot meet "no collector node > 1.32 V" at +10 % supply

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-27
- **Decided by**: Builder agent, issue #21

DR-NNN is the next unused number at merge time and is the permanent ID.

## Context

DR-003 / target-spec R3 forbid any HBT collector node above 1.32 V, which is also
the +10 % CML rail (1.2 V x 1.1). The first-cut TX pre-drivers load each collector with
a resistor to the rail, so the off-side collector rests at the rail and can only
go up from there. The PVT-edge sizing record
[`sim/tx/records/20261027-024044-2e55774/record.md`](../../sim/tx/records/20261027-024044-2e55774/record.md)
(simulated, sizing evidence, not a measurement) shows the four pre-driver output
nodes (`vc_max_pre_main_outp/outn`, `vc_max_pre_post_outp/outn`) above 1.32 V in
**all 18 corners at vdd = 1.32 V** (every process and temperature), by 8 mV to 30 mV
(worst 1.3503 V, ffe1_bcs/bcs/1.320 V/125 C). Every node of the line driver, the
tails and the bias stays below the limit (worst driver output 1.2961 V), and no
reverse Vbe is above 0.22 V against the 1.0 V limit. The same record shows the
collector-emitter voltage across those pre-driver pairs at most 1.054 V against the
1.4 V open-base BVCEO. The mux, FFE enable and level converter are MOS-dependent and
not simulated, so they are not covered by this finding.

## Options considered

1. **Lower the load reference.** Return the pre-driver loads to a node a few tens of
   mV below the rail (for example a diode-connected HBT or a small series resistor
   from the rail). Keeps R3 as written; costs headroom the stack barely has
   (tail Vce already 0.05 to 0.11 V at the low-supply corners) and swing.
2. **Clamp the pre-driver outputs** to the rail with a diode. Adds capacitance on a
   5 GHz node and conducts only above the rail, so it caps the overshoot at one
   diode drop, not at 1.32 V.
3. **Restate the limit on the device stress** (collector-emitter voltage against
   BVCEO) instead of node-to-ground. Measured Vce is well inside 1.4 V, but this
   relaxes R3, and agents do not relax the ratified spec to make results pass.
4. **`npn13G2V` on the pre-driver.** DR-003's fallback; fT 90 to 120 GHz is a poor
   fit for the stage after the final mux.

## Decision

Proposed: option 1 for the pre-drivers only, to be sized and re-simulated in a
follow-up (the loads return to the rail through a series resistor, or to a
diode-dropped node, chosen by re-running the same grid). R3 stays as written; option 3
is recorded as the alternative the operator may choose, and nothing here relaxes it.

## Consequences

- The T1 item 1 TX sources in this PR are committed with the violation recorded, not
  hidden; the sizing record is the evidence and is not edited after the fact.
- The pre-driver load change shifts the driver input common mode and swing; the grid
  must be re-run and a new record appended.
- The finding applies to any later stage with a rail-referenced resistive load and
  an off-side collector at the rail (RX buffers, the clock path).
