# DR-001: Line rate, rate architecture, HBT/CMOS split, serialization ratio

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-17
- **Decided by**: Builder agent, issue #2
- **Fixes rows**: target-spec R1, R2

## Context

`CLAUDE.md` fixes 10 Gb/s as the target, 5 Gb/s the fallback, 12.5 Gb/s a
stretch that must not drive architecture. The only clock sources in the
catalog are LC-based at 4.5–5.5 GHz (`sg13g2-vco` @ `6e6e830`, ratified as
targets; see [clock-requirement.md](../clock-requirement.md)); the ring PLL
`sg13g2-pll` @ `880d797` reaches 445–1562 MHz.

## Options considered

| Option | Clock at 10 Gb/s | Verdict |
|---|---|---|
| Full-rate | 10 GHz | Needs a clock twice the VCO band's top end (5.5 GHz); no sibling can supply it. Rejected. |
| **Half-rate** | **5 GHz** | Inside the VCO band; rising and falling edges each carry one bit. Chosen. |
| Quarter-rate | 2.5 GHz | Below the VCO band; needs a divider tree and 8 phases. Kept as the RX *stretch* only if half-rate samplers fail, as the README draft already lists. |

Serialization ratio / word width (CMOS side of the boundary):

| Ratio | Parallel clock at 10 Gb/s | Verdict |
|---|---|---|
| 8:1 | 1.25 GHz | Too fast for the CMOS standard cells; rejected. |
| **16:1** | **625 MHz** (5 GHz / 8) | Chosen: comfortably CMOS, a 4-stage 2:1 tree whose last two stages are CML. |
| 32:1 | 312.5 MHz | Fine for timing but a larger mux/demux tree and wider PRBS datapath for no benefit. |

## Decision

1. **Line rate**: 10 Gb/s target. The 5 Gb/s fallback runs **full-rate on the
   same 5 GHz clock** (not half-rate at 2.5 GHz, which is outside the VCO
   band). The 12.5 Gb/s stretch would need 6.25 GHz half-rate, outside the
   band; it is recorded as a clock gap only and shapes nothing.
2. **Half-rate on both sides.** TX: 5 GHz differential clock (2 phases) into
   the final 2:1 CML mux. RX: 4 phases (0/90/180/270°) at 5 GHz; two samplers
   take data on 0°/180°, two take edges on 90°/270° (Alexander bang-bang).
3. **HBT CML**: the last 2:1 serializer stage, the line driver and its
   pre-driver, the RX input buffer/CTLE, the four sampling latches and the
   5 GHz clock buffers/quadrature path. **CMOS**: everything below 625 MHz
   (the serializer tree down to 16:1, deserializer, PRBS generator/checker,
   CDR digital filter, control, loopback muxes). The CML-to-CMOS boundary sits
   at the first divided clock; level-conversion stage is a design item.
4. **Parallel word**: 16 bits at 625 MHz in each direction, raw bits only.
5. **Lanes**: one.

## Consequences

- The clock requirement (5 GHz, 4 phases, tight duty/quadrature error) is
  what makes the clock interface the risk; see clock-requirement.md.
- HBT supply and breakdown limits constrain the CML rail: DR-003.
- Changing any item needs a superseding record. No agent relaxes this to
  make results pass.
