# R18 pad capacitance on extracted pad metal, 2026-11-12 (issue #94, DR-012)

Append-only. Request `sim/tx/pad_cap_extracted_5ghz.request.json` (27 corners: 3 HBT process
legs x 1.08/1.2/1.32 V x -40/27/125 C), run with `klt sim --backend batch --wait-for-capacity 600`
(batch job `klt-sim-687b4f41fca0`). 27 of 27 corners ran, 0 errors, no limits declared.
**Simulated and extracted, not measured.** Raw report: `stdout.json`; stderr: `*.stderr.txt`.

Capacitance is `C = -Im(I) / (2 pi f)` at 1 V ac, one pad leg, 0.6 V pad bias.
The report lists min/max per measurement only (same limitation as `../20261112-pad/`).

| Quantity (27 PVT corners) | Min | Max |
|---|---|---|
| Total, metal + both clamps, 5 GHz | 119.5 fF | 125.9 fF |
| Total, 0.1 GHz (check: same as 5 GHz) | 119.5 fF | 125.9 fF |
| Pad metal only (extracted, no PVT dependence) | 70.66 fF | 70.66 fF |
| ESD clamps only (PDK diode models) | 48.8 fF | 55.2 fF |

Pad-metal source: `layout/analog/pads/records/2026-11-12-fc8a7fa/` (`pad_esd.gds`, `padp` with
bondpad TM2, `klt extract --deck sg13g2 --parasitics`). The metal and ESD legs add up to the total
(70.66 + 48.8..55.2), which cross-checks the deck.

Not covered: bondwire/package, pad-to-pad coupling, the 4.57 ohm series `rsil`, any
distributed or 5 GHz extraction effect, bias other than 0.6 V, return loss.
