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
  tx/                    TX high-speed path (issue #21)
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

## `design/tx/`

Schematics (`*.sch`) and symbols (`*.sym`) are generated from the cell tables in
`gen_schematics.py` (committed with them: `python3 -I design/tx/gen_schematics.py`).
Netlists in `netlists/` are exported with `klt netlist --block`, never raw `xschem`.

| Cell | What | Devices |
|---|---|---|
| `mux2to1_cml` | final 2:1 mux on the 5 GHz clock (DR-001) | HBT pairs, thin-oxide MOS tail switches and clock squarers |
| `predriver` | CML pre-driver | HBT, resistors |
| `driver_ffe` | line driver, 2-tap FFE (main + 3 post-cursor slices), 50 ohm back-termination | HBT, resistors |
| `bias` | tail-bias reference (placeholder Rref) | HBT, resistors, MIM cap |
| `ffe_en` | enables the post-cursor slices (4 steps) | thin-oxide MOS |
| `tx_lvl_cml2cmos` | CML-to-CMOS at the first divided clock (prefixed: `design/rx/` has its own `lvl_cml2cmos`, and `xschemrc` puts every partition on one symbol path) | thin-oxide MOS |
| `pad_esd` | pad and ESD network, own cell for the layout (#24) | PDK ESD diodes, bondpad placeholder, resistors |
| `tx_top` | instantiates all of the above | |

Rules for this tree: only `npn13G2` and thin-oxide MOS on the CML rail (R3).
Cell file names are stable: #24 (layout) depends on them and on the `pad_esd` boundary.

Netlist staleness: the shared `design/check-netlists.sh` covers `design/tx/` (exit 0 when
every netlist matches its schematic, 3 when any has drifted; `--write` re-exports).
Needs `source scripts/env.sh`. Not wired into CI here (coordinate with #4).

### Interface requirements on other partitions

- **Post-cursor streams.** `tx_top` takes the main bit streams (`dap/dan`, `dbp/dbn`,
  even/odd UI) and the same streams delayed by one UI (`dpap/dpan`, `dpbp/dpbn`). The
  digital serializer must supply the delayed copies; `rtl/` does not produce them
  today (it outputs a 16-bit word).
- **Clock.** `ckp/ckn` is the 5 GHz differential clock of DR-001. Its amplitude, duty
  and edge rate at the mux clock squarer are not specified yet; they belong in the
  clock requirement and are the unproven seam of this block.
- **Divided clock.** `ckdp/ckdn` is the CML 625 MHz-domain clock the level converter
  turns into CMOS.

### What the first-cut values are

Placeholders chosen to find the headroom problem early: 10 mA main tail, 3 x 1.11 mA
post-cursor slices, 100/60/50 ohm loads, 1.2 V rail. The pad cell's diodes and bondpad
carry no 5 GHz capacitance number (the PDK `bondpad` model is empty); R18 and R19 are
not assessed here. The bias reference current follows the supply; a supply-independent
reference is a sibling block and is not designed in this repo.
