# R19 clamp IV on the extracted pad_esd devices, 2026-11-12 (issue #94, DR-013)

Append-only. Request `sim/tx/pad_esd_iv_extracted.request.json` (27 corners: 3 HBT process
legs x 1.08/1.2/1.32 V x -40/27/125 C), run with `klt sim --backend batch --wait-for-capacity 600`
(batch job `klt-sim-a21feb66cbf7`, klt 0.9.2.dev865 client, ngspice 46). A local single-corner run
(hbt_typ, 1.2 V, 27 C) debugged the deck first. 27 of 27 corners ran, 0 errors, no limits declared.
**Simulated from extracted device geometry, not measured.** Raw report: `stdout.json` (schema 3 JSON, re-fetched from the finished batch job; the original console summary is kept as `stdout.txt`).

Devices come from `layout/analog/pads/records/2026-11-12-fc8a7fa/extract-pad_esd.json`
(`padp` leg): `dpantenna` (pad to VDD) and `dantenna` (VSS to pad), each 35.0028 um2 /
58.08 um perimeter, plus the 5.119632 ohm seam `rsil` as an ideal resistor. The pad is swept
-0.6 to 1.8 V; the current is `i(Vp)` (negative = into the pad network from the source).

| Pad V | -40 C | 27 C | 125 C |
|---|---|---|---|
| -0.6 V | 9.3e-11 A | 7.04e-8 A | 5.76e-6 A |
| +0.6 V | -4.6e-12 .. -3.9e-12 A | -5.6e-11 A | -5.09e-10 .. -5.08e-10 A |
| +1.2 V | -1.2e-11 .. -1.1e-11 A | -9.4e-11 .. -9.3e-11 A | -7.5e-10 .. -7.3e-10 A |
| +1.8 V | -1.7e-8 .. -2.1e-11 A | -2.0e-6 .. -5.5e-10 A | -1.9e-5 .. -4.3e-7 A |

(Ranges are over the supply legs; the three process legs are identical.) Min/max over all 27
corners: -0.6 V 9.32e-11 .. 5.76e-6 A; +1.8 V -1.88e-5 .. -2.1e-11 A.

Reading: at 0.6 and 1.2 V the clamp current is sub-nA at every corner; the reverse leakage at -0.6 V reaches
5.8 uA at 125 C, and 1.8 V (0.48 to 0.72 V above VDD) gives up to 19 uA. The PDK `dantenna`/`dpantenna`
models are fitted for reverse bias and do not model forward bipolar action, so the forward
current is a lower bound. The `dio_*` corner sections do not move these models, hence no process spread.

Not covered: TLP, HBM, any clamp turn-on or failure current, `rx_term_pad` (unrouted),
the `diodevdd_2kv`/`diodevss_2kv` models (DR-011 bench covers those from the schematic side),
LVS of the pad cell (#27). No ESD qualification claim.
