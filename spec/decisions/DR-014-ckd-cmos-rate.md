# DR-014: Rate of the TX divided clock `ckdp/ckdn` and consumer of `ckd_cmos`

- **Status**: proposed — **conditional on DR-008 B1**, which is itself proposed; if DR-008 is
  ratified differently (B2/B3, or a moved boundary), this record is superseded by a new one,
  not edited. Ratification needs a human or Champion.
- **Date**: 2026-11-23
- **Decided by**: builder (issue #252)
- **Clarifies**: DR-001 decision 3 ("The CML-to-CMOS boundary sits at the first divided
  clock") and DR-008 B1 item 1. Does not edit either record and does not relax any ratified
  spec text.

## Context

DR-001 decision 3 puts the CML-to-CMOS boundary "at the first divided clock". Under DR-001's
own 16:1 tree that clock is 2.5 GHz, and `design/tx/` was built against that wording:
`tx_top` instantiates `Xlvl` (`tx_lvl_cml2cmos`) on `ckdp/ckdn` producing `ckd_cmos`, and the
only converter evidence drives it at 2.5 GHz — `sim/tx/make_tb.py` `LV_T = 400 ps` and the
records `sim/tx/records/20261110-221849-506b37e-mos/` and
`sim/tx/records/20261110-224611-4092fc2-mos/` (45 corners each).

`design/README.md` instead called `ckdp/ckdn` "the CML 625 MHz-domain clock", matching DR-008
B1 item 1 (proposed): the whole 2:1 tree and the divider chain stay CML down to 625 MHz, and
both level converters sit at the 16 x 625 Mb/s word boundary, so no CMOS is clocked above
625 MHz. `rtl/serdes_digital_top.v` agrees on the consumer side ("`clk` is the divided
625 MHz word clock from the analog side").

So one clock had two written rates (bench 2.5 GHz, docs 625 MHz) and `ckd_cmos` had no
consumer anywhere in the tree (`git grep ckd_cmos` hits only `design/tx/`). Neither rate
could be traced to the other.

`spec/clock-domains.md` (deliverable of #241) was not on `main` when this was written; if it
lands and names a different boundary, this record defers to it via a superseding record.

## Options considered

- **625 MHz, the word boundary (DR-008 B1 item 1)** — chosen, see Decision. The documented
  proposed direction; consistent with `design/README.md`, `rtl/serdes_digital_top.v` and the
  DR-008 B1 split (CMOS at or below the 625 MHz word clock).
- **2.5 GHz, the literal "first divided clock" (DR-001 decision 3)** — rejected: it
  contradicts DR-008 B1 item 1 and `design/README.md`, and it needs a CMOS consumer clocked
  at 2.5 GHz, which the B1 split excludes and which DR-001 itself rules out for standard
  cells already at 1.25 GHz ("too fast for the CMOS standard cells"), a fortiori at 2.5 GHz.

## Decision

All proposed, conditional on DR-008 B1:

1. `ckdp/ckdn` is the **625 MHz word-boundary divided CML clock**: the last CML divide-by-2
   output of the 5 -> 2.5 -> 1.25 -> 0.625 GHz chain, i.e. DR-008's "CML-to-CMOS clock edge
   at 625 MHz ... driving the CMOS word clock". DR-001 decision 3's "first divided clock"
   wording is not the rate of this clock.
2. **Consumer of `ckd_cmos`**: the CMOS word interface of the serializer — the digital
   partition's `clk` input and the word-rate serializer stages it clocks. **No consumer
   exists today**: `rtl/` outputs a 16-bit parallel word and contains no CMOS serializer, so
   `ckd_cmos` is unloaded past the `tx_top` port. Building that consumer is future work
   (out of scope here, as is any serializer RTL).
3. **`Xlvl` stays in `tx_top`**: it is the TX's own clock-domain crossing (CML divider to
   CMOS word clock) that DR-008 B1 places at the word boundary. With no consumer yet it is
   the interface pin the future serializer will need; removing it would leave the digital
   partition with no word-clock source.
4. **Evidence at the intended rate**: the converter bench (`sim/tx/make_tb.py` `LV_T`) now
   runs at 625 MHz (1.6 ns period, was 400 ps), and the full 45-corner MOS set was re-run:
   record `sim/tx/records/20261123-035024-5214c04-mos/` (`tx_lvl_cml2cmos` 45/45 corners
   pass). The 2.5 GHz records `20261110-221849-506b37e-mos/` and
   `20261110-224611-4092fc2-mos/` are left untouched and are read as **margin data points
   (4x the intended input rate)**, not as evidence at 625 MHz. They carry no `Erratum`:
   each describes its own bench accurately; the defect corrected here is the rate
   *assignment* (which clock the bench and docs were naming), and it is corrected by this
   record plus the README updates, not by rewriting evidence.
5. If DR-008 ratification moves the boundary (B2/B3 or otherwise), the bench and record at
   the new rate follow the same rule: new append-only record, superseding (not editing)
   this one.

## Consequences

- `sim/tx/make_tb.py` sets `LV_T = 1.6 ns` (625 MHz) with this record cited in the deck
  header; `tx_mos_tx_lvl_cml2cmos.sp` and the request regenerate from it
  (`tx_mos_tx_lvl_cml2cmos.request.json` is unchanged — same corners, measurements and
  window; only the input period moved).
- `design/README.md` (cell table and the divided-clock bullet) and `sim/tx/README.md`
  (bench table and run status) name 625 MHz and cite this record.
- Converter margins at 625 MHz over 45 corners (record `20261123-035024-5214c04-mos`):
  output high 1.087..1.349 V, output low -0.036..-0.015 V (rail-to-rail at every corner),
  propagation delay 60..216 ps (differential-input zero crossing to output vdd/2), supply
  0.20..0.49 mA. Sizing evidence only; no spec row is graded. Reading against the
  validation plan's G2 trigger (delay spread vs the 1.6 ns word period): 60..216 ps is
  about 14 % of the period, far from the "more than half" B3 trigger — but this is
  sizing evidence at an ideal source, not a G2 pass claim (supply isolation, swing into a
  real load and skew are not benched here).
- Known measurement artifact, unchanged from the 2.5 GHz records: the duty column is a
  single-period trig/targ edge-pairing result and is phase-luck (34..38 % at 2.5 GHz,
  about -53 % at 625 MHz; ngspice searches `trig` and `targ` independently from their own
  `td`). Do not read duty from these records. The tpd, out_hi/out_lo and Idd columns are
  not affected. Fixing the duty measurement is a separate bench-methodology change, not
  made here (the published 2.5 GHz record used the same measurement).
- Remaining historical wording: `design/tx/gen_schematics.py` still describes the cell as
  "CML-to-CMOS level conversion at the first divided clock (DR-001 decision 3)". It is
  committed schematic-generator text; regenerating schematics and netlists for a comment is
  deferred as out of #252 scope. DR-001's own text stays untouched by design (append-only).
- Reconcile with `spec/clock-domains.md` (#241) when it lands; a conflict is resolved by a
  superseding record.
