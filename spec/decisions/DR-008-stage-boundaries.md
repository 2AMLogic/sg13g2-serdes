# DR-008: Serializer/deserializer stage boundaries and the 625 MHz assumption

- **Status**: proposed (nothing here is ratified; ratification needs the engineering and market review in `ratification/`)
- **Date**: 2026-11-02
- **Decided by**: Builder agent, issue #2 (operator ruling 2026-10-19)
- **Clarifies**: DR-001 decision 3 and target-spec R2. Does not edit them; if accepted, this record supersedes the wording of those two items.

## Context

DR-001 says the serializer is "a 4-stage 2:1 tree whose last two stages are
CML", while decision 3 and R2 say "HBT CML for the last 2:1 mux ... CMOS
everything below 625 MHz". These disagree about the 2.5 GHz stage and are
silent about the 1.25 GHz stage. Level conversion is called "a design item".
DR-001 also rejects an 8:1 ratio because 1.25 GHz is "too fast for the CMOS
standard cells", which would equally exclude a CMOS 1.25 GHz stage.

## The stages (arithmetic on DR-001's 16:1 half-rate tree)

| Stage (TX; RX mirrors) | Output rate per wire | Clock it needs (DDR) | DR-001 / R2 assignment | Status |
|---|---|---|---|---|
| S4: 2:1 to the line | 10 Gb/s | 5 GHz | HBT CML (both texts agree) | consistent |
| S3: 4:2 | 5 Gb/s | 2.5 GHz | DR-001 prose: CML; R2: unassigned | **conflict** |
| S2: 8:4 | 2.5 Gb/s | 1.25 GHz | unassigned | **gap** |
| S1: 16:8 | 1.25 Gb/s | 625 MHz | unassigned (RTL port comment implies CML) | **gap** |
| Word (converter output) | 625 Mb/s per bit, 16 wires | 625 MHz | CMOS | assumption |
| Clock divider chain 5 → 2.5 → 1.25 → 0.625 GHz | n/a | n/a | unassigned | **gap** |

## Options

- **B1 (proposed default)**: CML for S4, S3, S2 and S1 (the whole 2:1 tree)
  and the divider chain all the way down to 625 MHz; the CML-to-CMOS level
  conversion (RX) and CMOS-to-CML conversion (TX) sit at the 16 x 625 Mb/s
  word boundary, matching `rtl/serdes_digital_top.v` (`tx_word`, "to the CML
  serialiser, 625 MHz"). Makes no CMOS claim above 625 MHz in clock frequency
  or data rate. Cost: one more CML stage (S1) and a CML divide-by-2 from
  1.25 to 0.625 GHz than the DR-001 prose implies; more CML power, not
  estimated (R16 has no device-level estimate), and a larger HBT clock tree.
- **B2**: CML for S4 and S3 only; S2 in CMOS at 1.25 GHz. Saves CML power but
  rests on a CMOS 1.25 GHz stage that DR-001 itself called too fast for the
  standard cells and that nothing in the repo supports. Not proposed.
- **B3**: 32:1 / 312.5 MHz word (DR-001 option), relaxing the CMOS budget at
  the cost of a wider datapath. The fallback if B1's 625 MHz fails.

## Proposed decision (all Proposed)

1. Adopt B1. R2's text becomes: HBT CML for S4, S3, S2, S1 and the
   5/2.5/1.25/0.625 GHz clock path; CMOS from the 625 MHz word boundary down.
   The level converters therefore carry the 16-bit 625 Mb/s-per-wire word.
2. **The 625 MHz CMOS claim is a proposed feasibility assumption.** The only
   timing evidence is DR-005/DR-006: OpenSTA, pre-layout, ideal clock, no wire
   load, **one corner** (`typ_1p20V_25C`), worst setup slack +0.014 ns at
   1.6 ns after a restructuring that raised the CDR loop delay from 2 to 7
   clocks. It does not cover layout parasitics, skew, other PVT corners or
   the level converter. Those records' wording is not proof of feasibility.
3. **Level conversion is unresolved**: the CML-to-CMOS converter (RX) and
   CMOS-to-CML converter (TX) at 1.2 V are not sized, simulated or specified
   (swing, input common mode, delay variation over PVT, supply isolation
   between the CML and digital rails). The seam is the stated risk in
   `CLAUDE.md`; it gets its own gate in `spec/validation-plan.md` (G2).
4. B3 stays the recorded fallback; choosing it needs a superseding record, not
   an edit to the proposal.

## Unresolved feasibility, stated

The CML-to-CMOS clock edge at 625 MHz (the last CML divide-by-2 output driving
the CMOS word clock) is part of the converter work in item 3 and is likewise
unsimulated.

Whether HBT CML at 5 GHz with `npn13G2` and a 1.2 V ±10 % rail has the
headroom for a stacked S4 mux plus tail source is **unsimulated** (depends on
#3, DR-003). The 2.5, 1.25 and 0.625 GHz CML latches have the same dependency.
