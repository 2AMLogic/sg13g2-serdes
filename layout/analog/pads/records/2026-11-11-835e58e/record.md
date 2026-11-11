# Pad/ESD layout record, 2026-11-11 (source commit 835e58e)

Append-only. Re-run with `layout/analog/pads/regen.sh` into a new dated directory.

| Item | Value |
|---|---|
| Generator | `layout/analog/pads/gen_pad_cells.py` |
| Cells | `pad_esd.gds` (TX, 2 legs), `rx_term_pad.gds` (RX, 2 legs) |
| Sources | `design/tx/netlists/pad_esd.spice`, `design/rx/netlists/rx_term_pad.spice` |
| Geometry | PDK `sg13g2_pr.gds` cells `bondpad`, `diodevdd_2kv`, `diodevss_2kv` as drawn; `klt gen res_array` for rsil |
| Tool | `klayout-tools==0.9.0` (`layout/toolchain.json`), IHP-Open-PDK 0.3.0 |

## What this is

Cells are **placed and net-labelled** (`cp`/`cn` core-side seam, `padp`/`padn`,
`inp`/`inn`, `vcm`). Nothing is routed, and no DRC, LVS, extraction,
capacitance or 5 GHz claim is made (DRC #26, LVS #27, pad model #94).

- `klt gen --list-pdk-pcells` lists no SG13G2 pcells here: the PDK release
  tarball omits the `pycell4klayout-api` submodule the PDK pcell library needs.
  The PDK's fixed GDS cells are used instead.
- `Cpad_p`/`Cpad_n` (50 fF) are pad-capacitance model elements, not drawn devices.
- rsil bodies are sized with a nominal 7 ohm/sq (not verified): `Rs` w=8 um, l=4.571 um
  (from the TX netlist), `Rt` 50 ohm as w=1 um, l=7.143 um. Resistance is unchecked.
- Diode `PAD` terminals are not strapped to the resistor/bondpad.
