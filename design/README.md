# design

Analog schematic sources. See the repo README for scope.

| Path | What |
|---|---|
| `xschemrc` | project xschem config (PDK symbols, `design/tx` cells); load with `klt netlist --rcfile design/xschemrc` |
| `tx/` | TX high-speed path (T1 item 1, analog partition, issue #21) |

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
| `lvl_cml2cmos` | CML-to-CMOS at the first divided clock | thin-oxide MOS |
| `pad_esd` | pad and ESD network, own cell for the layout (#24) | PDK ESD diodes, bondpad placeholder, resistors |
| `tx_top` | instantiates all of the above | |

Rules for this tree: only `npn13G2` and thin-oxide MOS on the CML rail (R3).
Cell file names are stable: #24 (layout) depends on them and on the `pad_esd` boundary.

Netlist staleness: `design/tx/check-netlists.sh --check` exits 0 when every netlist
matches its schematic and 3 when any has drifted; `design/tx/check-netlists.sh`
regenerates them. Needs the repo env (`scripts/setup-env.sh`, then it sources
`scripts/env.sh` itself). Not wired into CI here (coordinate with #4).

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
