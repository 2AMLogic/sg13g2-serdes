# R4 main-tail probe check at WCS, 1.08 V, −40 °C

Two single-corner simulations exercise the corrected probes at zero and positive bias offset. Both use the FFE-off bench at `d13baf3`, the main driver at `5c4eac5`, the R18 pad stand-in and the fixed 100 Ω differential load. The PDK is the SHA-256 verified IHP v0.3.0 archive from `sim/pdk.json`. Local klt `978f7464fae1` ran ngspice 47. Each raw report includes the deck hash, tool provenance and terminal measurements.

| Candidate | Static hi / lo (mV) | Static (mVppd) | PRBS run (mVppd) | XQTM Ic / Ie (mA) | Min tail Vce (mV) | Max Ve − Vb (V) |
|---|---:|---:|---:|---:|---:|---:|
| Control | 103.339 / −103.724 | 207.063 | 206.576 | 4.593 / 4.603 | 109.495 | −0.885318 |
| +80 mV, RT ×3 | 203.085 / −205.434 | 408.519 | 408.007 | 5.926 / 6.075 | 90.276 | −0.939022 |

The control reproduces both FFE-off pad samples and minimum tail Vce in the historical WCS report. At +80 mV, RT ×3, the static swing is 91.481 mV below the proposed 500 mVppd target and 108.519 mV above the 300 mVppd fallback at this corner. Both simulations returned exit 0. Ranking the candidates or bounding R3 at high supply requires the replacement fleet grid. [Historical control](../20261123-022802-fedf656-vce/tx_sizing_ffe0_wcs.report.json)

`Voffset` sits between the shared bias node and XQTM's base. `Vsc` measures current into its collector from the differential pair, and `Vse` measures current out through REM. Both currents are averaged from 0.9 to 1.35 ns. Reverse Vbe uses XQTM's emitter and base. Static and PRBS windows are defined in the [verdict](../20261126-r4sweep-verdict/verdict.md#erratum-2026-11-26).

To repeat either single-corner check, source `scripts/env.sh` with the pinned PDK installed, then run `klt sim --format json ctl.request.json` or `klt sim --format json c_p80_r300.request.json` from this directory.
