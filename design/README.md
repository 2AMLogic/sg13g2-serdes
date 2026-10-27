# design

Schematic sources (xschem) and the netlists derived from them. Evidence tier
T1 item 1 is graded from `design/inventory.item1.json` with
`klt signoff --attest 1 --inventory design/inventory.item1.json`.

```
design/
  xschemrc               project xschem config (PDK from PDK_ROOT; block directories on the symbol path)
  check-netlists.sh      staleness gate over design/*/: exit 0 match, 3 drifted (--write re-exports)
  inventory.item1.json   item-1 inventory, shared by every partition
  rx/                    RX high-speed path and 5 GHz clock path (issue #22)
```

Netlists are exported only with `klt netlist` (never raw `xschem`), into
`design/<partition>/netlists/<cell>.spice`, and re-exported on every schematic
change: `source scripts/env.sh && design/check-netlists.sh --write`.

## rx/

| Cell | What |
|---|---|
| `rx_term_pad` | 2 x 50 ohm termination to `vcm`, placeholder 50 fF pad capacitance, smallest PDK ESD clamp pair (`diodevdd_2kv`/`diodevss_2kv`) per pad |
| `ctle` | flat HBT pair plus an AC-coupled high-pass path of binary-weighted cells steered +/-; 3 control bits (8 peaking steps), constant total current |
| `latch_cml` | HBT CML sampling latch, two-level stack (clocked tail HBTs) |
| `clk_buf_quad` | CML buffers for the four clock phases (0/90/180/270), two chains of two stages |
| `lvl_cml2cmos` | latch-to-CMOS conversion, thin-oxide MOS |
| `rx_top` | pad -> CTLE -> four latches (data 0/180, edge 90/270) with clock buffers -> four converters |

Cell names, pin names and file names are stable interfaces for #23, #24, #27
and #28. `rx/tools/gen_schematics.py` is how the sheets were drawn; the `.sch`
files are the source of truth and the generator reproduces them byte for byte.

Known limits of this first pass (none are results):

- Resistors are ideal `res`: the PDK `rsil`/`rppd` models are `r3_cmc` OSDI models, which the host ngspice and the batch fleet cannot load today (`sim/README.md`). Layout (#24) swaps in PDK resistors and re-simulates.
- The pad capacitance is a placeholder; the PDK `bondpad` model is empty. R9/R18 are graded on extraction, not here.
- `vcm` and the CTLE control levels are inputs; their bias generation is not in this cell.
- The clock source is not designed here (`spec/clock-requirement.md`); `clk_buf_quad` passes the source's duty and quadrature error through.
- At 1.2 V the conventional three-level HBT latch does not fit (about 0.85 V per Vbe), so the latch uses a two-level stack with clocked tail HBTs. Records: `sim/rx/records/`.
