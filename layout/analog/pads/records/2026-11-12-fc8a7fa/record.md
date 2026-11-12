# Pad/ESD layout record, 2026-11-12 (generator base commit fc8a7fa)

Append-only. Supersedes the extraction picture of `../2026-11-11-835e58e/` (which is
untouched). Re-run with `layout/analog/pads/regen.sh`, then
`layout/analog/pads/verify.sh <this dir>`. Issue #131 (follow-up of #94 / DR-011).

| Item | Value |
|---|---|
| Generator | `layout/analog/pads/gen_pad_cells.py` (diode marker + pad-net strap/stack added) |
| Cells | `pad_esd.gds` (TX), `rx_term_pad.gds` (RX), `pad_esd_nobondpad.gds` (bondpad instances removed, analysis variant only) |
| Tool | `klayout-tools==0.9.0`, deck `sg13g2` (hash in each `*.json` `provenance`), IHP-Open-PDK 0.3.0 |
| Reports | `extract-*.json` (`klt extract --deck sg13g2 --parasitics`), `drc-*.json` (`klt drc --deck sg13g2`) |

## Cause of the 2026-11-11 gap: layout omission, not a deck limitation

- Diodes: the PDK `diodevdd_2kv`/`diodevss_2kv` cells carry `Recog.esd` (99/30) but
  **not** `Recog.diode` (99/31), which the deck requires, drawn by the user, for
  `dantenna`/`dpantenna` (`klt deck devices --deck sg13g2 --class dantenna`). The old
  extraction warned about exactly 2+2 candidate regions. The generator now draws 99/31
  over the Activ bbox of every placed diode instance (both cells). No tool issue filed:
  the deck behaves as documented.
- Bondpad: the PDK `bondpad` is only TopMetal2 (134/0) + Passiv (9/0) + pad opening
  (41/0). 9/0 and 41/0 are non-conducting and correctly outside the connectivity graph;
  the TM2 was *dead metal* because nothing connected to it. The generator now straps,
  per leg, the seam-resistor pad-side terminal, both diode `PAD` pin boxes (M2) and a
  Metal2..Metal5/TopMetal1 via stack (V2-V4, TV1, TV2 at the `klt deck rules` sizes)
  that lands under the bondpad TM2.
- Tool friction already tracked upstream: `klt extract` without `-o` writes
  `<gds>.spice` next to the input (2AMLogic/klayout-tools#2850, closed; still happens in
  the pinned 0.9.0). `verify.sh` removes those files so the record stays clean.

## Result: extracted, not measured

`pad_esd.gds` now extracts 2 `dantenna` + 2 `dpantenna` + 2 `rsil` (was 2 `rsil`).
Diode terminals land on the pad nets: `padp` joins the rsil B terminal, the
`dpantenna` anode, the `dantenna` cathode and the bondpad (same for `padn`).

| Pad net `padp` (`klt extract --parasitics`) | Capacitance, extracted |
|---|---|
| 2026-11-11 record (metal0 only, nothing connected) | 0.784 fF |
| New, **without** bondpad TM2 (`pad_esd_nobondpad.gds`) | 45.25 fF |
| New, **with** bondpad TM2 | 70.66 fF (TM2 share 25.41 fF) |

By layer with bondpad (fF): M1 14.68, M2 19.70, M3 3.23, M4 2.68, M5 2.35, TM1 2.61,
TM2 25.41 (the deck labels these metal0..metal6; M1 is the deck's metal0). `padn` is
identical.

What the number is: the deck's **interconnect** area/fringe capacitance to substrate of
the geometry on the pad net, from `klt extract --parasitics`. It is an extracted
figure, never a measurement. It does **not** include the ESD diodes' junction
capacitance (a device model, supplied by the PDK models in simulation), pad-to-pad or
bondwire/package parasitics, or any 5 GHz effect. R18 must add those from their own
sources; this record only supplies the pad-metal budget and its split.

## DRC and LVS

- `klt drc --deck sg13g2`: `pad_esd` clean (0 violations), `rx_term_pad` clean (0).
  The deck does not enforce `Pad.*` and `LU.*` rules (14 rules, `klt deck info`), so
  clean here says nothing about pad spacing, latch-up or ESD-structure rules.
- LVS: **not run.** It is #27's scope; the reference netlists model each clamp as a
  `diodevdd_2kv`/`diodevss_2kv` subcircuit, which this deck extracts as plain
  `dantenna`/`dpantenna` (it has no native `Recog.esd` recognition), so a compare would
  not be meaningful without the PDK's own runset.

## Still open / limits

- Only `pad_esd` is strapped. `rx_term_pad` gets the diode marker (4 diodes extract) but
  its diode `PAD` terminals and resistors are still unrouted; its nets extract as
  isolated 0.78 fF metal0 stubs. RX pad capacitance is the 50 fF model element
  `Cpad_*`, not a layout figure.
- Diode `VDD`/`VSS` rails are unstrapped; 2 M1 clusters remain dead metal (warned).
- Resistor bodies are still sized with a nominal 7 ohm/sq (not verified).
