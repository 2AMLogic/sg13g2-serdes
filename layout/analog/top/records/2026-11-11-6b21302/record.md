# Analog top assembly record, 2026-11-11 (source commit 6b21302)

Append-only. Re-run with `layout/analog/top/regen.sh` into a new dated directory.

| Item | Value |
|---|---|
| Generator | `layout/analog/top/gen_analog_top.py` (klayout.db only, no PDK) |
| Top cell | `serdes_analog_top` = `tx_top` + `rx_top` |
| `tx_top` | TX core cells (`tx_core_lib.gds`, 2026-11-11-835e58e) + `pad_esd` (pads, 2026-11-11-835e58e) |
| `rx_top` | RX core cells (`rx_core.gds`, 2026-11-11-835e58e) + `rx_term_pad` (pads, 2026-11-11-835e58e) |
| Attestation | `manifests/evidence/item2.analog-top.json` (`klt signoff --attest 2`, klt 0.9.0) |

## Partition label

Item 2 is graded per partition. This record is the **analog** partition as
declared in `partition_boundary.analog` of `manifests/sg13g2-serdes.signoff.json`
(HBT CML from the serial pad down to the 625 MHz word boundary, including both
level converters, plus pads and ESD). The **digital** partition is
`layout/digital/records/2026-11-10-f6fe587/serdes_digital_top.gds`
(`partition_boundary.digital`: the `rtl/serdes_digital_top.v` hierarchy), cited
by `manifests/evidence/item2.json` under evidence key `2.digital`. This record
is cited under `2.analog`. The seam between them is DR-008's word boundary;
no analog-to-digital interconnect is drawn here.

## What this is

Input records are read, never modified. Cells are **placed** (shelf placement,
20 um gaps; `tx_top` row at y=0, `rx_top` row above it), instance names are the
cell names, and the pad cells keep their net labels (`cp`/`cn`, `padp`/`padn`,
`inp`/`inn`, `vcm`). Nothing is routed between cells. The core-to-pad seam is
**placed** only: no capacitance or 5 GHz claim (pad model #94), and no DRC (#26),
LVS (#27) or extraction claim.

Re-running into a scratch directory gives a stream `klt diff` reports
`equivalent` (bytes differ only by GDS write timestamps), and an identical
`summary.json`. The attestation therefore records no `regeneration` hash.
