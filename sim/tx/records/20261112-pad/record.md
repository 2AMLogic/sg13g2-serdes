# Pad ESD benches, 2026-11-12 (issue #94)

Append-only. Requests: `sim/tx/pad_cap_5ghz.request.json`, `sim/tx/pad_esd_iv.request.json`
(27 corners each: 3 process legs x 3 supplies x -40/27/125 C), run with
`klt sim --backend batch --wait-for-capacity 600` (klt 0.9.2.dev805 client, runner 0.9.0,
ngspice 46). Fleet jobs `klt-sim-c3f9eeb54e3b` (cap) and `klt-sim-f0a55d578665` (IV).
A local single-corner run of each (hbt_typ, 1.2 V, 27 C) was used first to debug the decks.

All 27 corners ran, 0 errors, no limits declared. Simulated, not measured.
Friction filed as 2AMLogic/klayout-tools#5385.
Scope and numbers: `spec/decisions/DR-011-pad-model-source.md`. This is the ESD diode
share only; bondpad and pad-metal capacitance are NOT included, and R18 is not graded here.
Capacitance is derived from `Im(I)` at 1 V ac: `C = -Im(I) / (2 pi f)`.
