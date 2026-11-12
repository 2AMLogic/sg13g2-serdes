# R6 TX return loss on the extracted pad, 2026-11-12 (issue #142)

Append-only. Requests `sim/bench/r6_tx_return_loss_on.request.json` and `..._off.request.json` (27 corners each: 3 HBT/CAP/DIO ganged process legs x 1.08/1.2/1.32 V x -40/27/125 C), `klt sim --wait-for-capacity 600` on the batch fleet. 54 of 54 corners ran, no limits declared (R6 is reported, not graded here; spec limits unchanged). **Simulated, not measured.**

Pad leg: each bondpad is the **extracted pad-metal C, 70.66 fF** (record `layout/analog/pads/records/2026-11-12-fc8a7fa`, `klt extract --deck sg13g2 --parasitics` on `pad_esd.gds`, net padp, with bondpad TM2) plus the PDK ESD diodes from `design/tx/netlists/pad_esd.spice` and the 4.57 ohm-class series rsil stand-in. Same value and source as `sim/tx/pad_cap_extracted_5ghz.sp`; total per-leg C at 5 GHz is 119.5..125.9 fF (`sim/tx/records/20261112-pad-extracted`).
Previous run, kept in `placeholder-100f/` (same decks except the bondpad was a 100 fF capacitor, diodes included, so about 150 fF per leg in total): shown side by side below. Min..max over the 27 corners, dB.

| Measurement | driver | placeholder 100 fF (old) | extracted 70.66 fF (new) |
|---|---|---|---|
| r6_sdd22_1m_db | on | -27.15 .. -13.81 | -27.15 .. -13.81 |
| r6_sdd22_0p1g_db | on | -25.29 .. -14.61 | -25.29 .. -14.61 |
| r6_sdd22_1g_db | on | -23.62 .. -14.43 | -23.99 .. -14.49 |
| r6_sdd22_2p5g_db | on | -19.65 .. -13.30 | -20.36 .. -13.60 |
| r6_sdd22_5g_db | on | -15.13 .. -10.94 | -16.12 .. -11.56 |
| r6_sdd22_7p5g_db | on | -12.14 .. -9.01 | -13.19 .. -9.79 |
| r6_sdd22_max_to_5g_db | on | -15.53 .. -11.18 | -16.51 .. -11.78 |
| r6_sdd22_max_to_7p5g_db | on | -12.14 .. -9.01 | -13.19 .. -9.79 |
| r6_sdd22_1m_db | off | -25.37 .. -14.68 | -25.37 .. -14.68 |
| r6_sdd22_0p1g_db | off | -25.36 .. -14.68 | -25.36 .. -14.68 |
| r6_sdd22_1g_db | off | -24.27 .. -14.54 | -24.58 .. -14.58 |
| r6_sdd22_2p5g_db | off | -21.00 .. -13.87 | -21.85 .. -14.10 |
| r6_sdd22_5g_db | off | -17.04 .. -12.13 | -18.26 .. -12.74 |
| r6_sdd22_7p5g_db | off | -14.12 .. -10.33 | -15.49 .. -11.20 |
| r6_sdd22_max_to_5g_db | off | -17.41 .. -12.33 | -18.60 .. -12.90 |
| r6_sdd22_max_to_7p5g_db | off | -14.12 .. -10.33 | -15.49 .. -11.20 |

Reading: SDD22 improves by about 1 dB at 5 GHz (worst corner -11.56 dB driver-on, was -10.94 dB) because the placeholder over-counted the pad; low frequency is unchanged. The R6 limit and its grade are the spec's business: this record adds no limit and does not relax one.

Not covered: bondwire/package, pad-to-pad coupling, any distributed 5 GHz effect (Cmetal is quasi-static), FFE-on slices and the mux/predriver input stage, resistor corner (rsil is a typical-rsh stand-in). PDK `dantenna`/`dpantenna` equivalence to the `diodevdd_2kv` clamp is not established (LVS #27, DR-013); only the TX `padp` leg is covered.
