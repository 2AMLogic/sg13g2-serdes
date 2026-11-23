# Clock domains and stage boundaries (evidence gate G3, row R2)

**Status: evidence index for a PROPOSED spec.** This is the per-stage clock-domain
list that DR-014 gate G3 asks for ([DR-014 at `8f213e3`][dr014], "Gates that keep
rows at target only"): which TX and RX stages exist, at which clock and data rate,
in which circuit family, and what timing evidence each carries. It does not assign
the stages DR-008 leaves open, does not relax R2 or DR-001, and is not a decision
record. A conflict named here is resolved by a new decision record, not by editing
this file's findings. Source files were read at `f9dd877` (line numbers below
refer to that commit); every figure is simulated, none measured.

[dr014]: https://github.com/2AMLogic/sg13g2-serdes/blob/8f213e390a6d3f278e97494a5a558cdae6d0437f/spec/decisions/DR-014-ratification-scope.md

**G3 stays open.** Section [Gate G3 status](#gate-g3-status) lists what is
missing. In one line: no serializer or deserializer stage is clocked at or
above 1.25 GHz today (the only CMOS running that fast is the clock squarer
inside the TX S4 CML cell), but the implemented RX hands 5 Gb/s CMOS streams
to a deserializer that does not exist, the two implemented converters have no
requirement and no post-layout evidence, and the RX converter misses its
first-look bounds at 43 of 45 corners.

## Rates

DR-001: 10 Gb/s line rate, half-rate architecture on a 5 GHz clock, so one
unit interval (UI) is 100 ps. A 2:1 stage clocked at *f* (DDR, both edges)
takes wires at *f* Gb/s and produces wires at 2*f* Gb/s. DR-008's stage table
counts the same way. The 16-bit word moves at 5 GHz / 8 = 625 MHz, 1.6 ns per
word, 625 Mb/s per wire. "Clock" and "data rate per wire" are separate columns
below because a CMOS stage at a 2.5 GHz DDR clock carries 5 Gb/s per wire
while the 625 MHz word registers carry 625 Mb/s per wire (one bit per clock,
not DDR): the clock says what the standard cells must toggle at, the wire
rate says what the converter must pass.

## TX stage list

Instances are in [`design/tx/netlists/tx_top.spice`](../design/tx/netlists/tx_top.spice);
`tx_word` is in [`rtl/serdes_digital_top.v`](../rtl/serdes_digital_top.v).

| Stage | Instance | Clock | Data rate per wire, in -> out | Circuit | DR-001 | DR-008 | Status |
|---|---|---|---|---|---|---|---|
| S4, 2:1 to the line | `Xmux_main` (L25), `Xmux_post` (L26), cell `mux2to1_cml` | 5 GHz, `ckp/ckn` | 5 -> 10 Gb/s; four 5 Gb/s differential inputs: `da`, `db` (even/odd UI) and `dpa`, `dpb` (the same two delayed by one UI) | HBT CML pair with thin-oxide MOS tail switches and a self-biased CMOS clock squarer (`sqa`, `sqb`) | decision 2 and 3: final 2:1 mux in CML | S4 "consistent" | implemented |
| S3, 4:2 | none | 2.5 GHz | 2.5 -> 5 Gb/s; must deliver the four streams above | DR-001 16:1 table: last two stages CML; decision 3: CMOS below 625 MHz | **conflict** (DR-001 prose vs R2; B1 proposes CML) | not implemented |
| S2, 8:4 | none | 1.25 GHz | 1.25 -> 2.5 Gb/s | DR-001 is silent; its 8:1 row calls 1.25 GHz "too fast for the CMOS standard cells" | **gap** (unassigned) | not implemented |
| S1, 16:8 | none | 625 MHz | 625 Mb/s -> 1.25 Gb/s | DR-001 is silent; the RTL port comment says "to the CML serialiser, 625 MHz" | **gap** (unassigned) | not implemented |
| Word, TX | `tx_word[15:0]`, output of `u_lb` (`serdes_digital_top.v` L23, L68) | 625 MHz, `clk` | 16 wires at 625 Mb/s | CMOS standard cells | decision 3 and 4 | "Word: CMOS, assumption" | implemented (RTL, synthesized, routed) |
| TX clock converter | `Xlvl` (L31), cell `tx_lvl_cml2cmos` | input `ckdp/ckdn`: 2.5 GHz in the only bench, 625 MHz-domain in `design/README.md` | n/a (clock), output `ckd_cmos` | thin-oxide MOS | decision 3: boundary at "the first divided clock" | **conflict**: B1 puts the converter at the 625 MHz word | implemented; no consumer |
| TX word-data converter | none | 625 MHz | 16 x 625 Mb/s, CMOS -> CML | proposed | decision 3 leaves it "a design item" | B1 item 1 | **proposed only**, no implementation |

The two S4 muxes are the two FFE taps, not two stages in series: `Xmux_main`
feeds the main tap through `Xpre_main`, `Xmux_post` feeds the post-cursor tap
through `Xpre_post`, and `driver_ffe` sums them. That is why `tx_top` needs
four 5 Gb/s inputs and not two. [`design/README.md`](../design/README.md)
"Interface requirements on other partitions" states the same: the serializer
must supply the even/odd streams and their one-UI-delayed copies, and `rtl/`
produces neither today.

## RX stage list

Instances are in [`design/rx/netlists/rx_top.spice`](../design/rx/netlists/rx_top.spice);
the word ports are in `serdes_digital_top.v` (L24, L25).

| Stage | Instance | Clock | Data rate per wire, in -> out | Circuit | DR-001 | DR-008 | Status |
|---|---|---|---|---|---|---|---|
| Samplers (S4 mirror) | `Xlat_d0`, `Xlat_d180`, `Xlat_e90`, `Xlat_e270` (L25, 27, 29, 31), cell `latch_cml`, clocked by `Xclk` `clk_buf_quad` (L24) | 5 GHz, four phases 0/90/180/270 | 10 -> 5 Gb/s on each of four wires (`qp/qn_d0`, `_d180`, `_e90`, `_e270`) | HBT CML | decision 2 and 3: four sampling latches | S4 "consistent" | implemented |
| RX converter, data and edge | `Xlvl_d0`, `Xlvl_d180`, `Xlvl_e90`, `Xlvl_e270` (L26, 28, 30, 32), cell `lvl_cml2cmos` | none (combinational); input toggles at up to 2.5 GHz | 5 -> 5 Gb/s CMOS on each of `d0`, `d180`, `e90`, `e270` | thin-oxide MOS | decision 3: boundary at "the first divided clock" (2.5 GHz) | **conflict**: B1 item 1 puts the RX converter at the 16 x 625 Mb/s word | implemented at 5 Gb/s |
| S3 mirror, 1:2 | none | 2.5 GHz | 5 -> 2.5 Gb/s on each of the four wires | B1: CML; after the implemented converter its input is already CMOS, and a CMOS stage here is CMOS at 2.5 GHz, against R2's "CMOS <= 625 MHz" | **unassigned** | not implemented |
| S2 mirror, 1:2 | none | 1.25 GHz | 2.5 -> 1.25 Gb/s | same | **unassigned** | not implemented |
| S1 mirror, 1:2 | none | 625 MHz | 1.25 Gb/s -> 625 Mb/s | same | **unassigned** | not implemented |
| Word, RX | `rx_data_word[15:0]`, `rx_edge_word[15:0]` (`serdes_digital_top.v` L24, L25) | 625 MHz, `clk` | 32 wires at 625 Mb/s (16 data, 16 edge) | CMOS standard cells | decision 3 and 4: a 16-bit word; the edge samples are not mentioned | "Word: 16 wires"; the 16 edge wires are not addressed | implemented as RTL ports; fed by a bench model only |

The implemented RX stops at the converter outputs. Four 5 Gb/s streams hold the
10 Gb/s data and the 10 Gb/s edge samples (one sample per 200 ps per latch);
the RTL needs 32 bits per 1.6 ns, which is three 1:2 stages per stream. No
circuit in `design/` or `rtl/` performs them: the deserializer is a bench
model in `rtl/tests/test_top.py` (`rtl/README.md`, "Scope").

## Dividers and clocks

| Item | Where | Frequency | Status |
|---|---|---|---|
| 5 GHz clock, TX | `ckp/ckn`, input port of `tx_top` | 5 GHz | from outside the block (`spec/clock-requirement.md`) |
| 5 GHz clock, RX | `ck0/ck180/ck90/ck270`, input ports of `rx_top` | 5 GHz, four phases | from outside the block |
| Divider chain 5 -> 2.5 -> 1.25 -> 0.625 GHz | none in `design/` or `rtl/` | | **gap** (DR-008 table, unassigned) |
| `ckdp/ckdn` | input port of `tx_top` | 2.5 GHz in the TX bench; "the CML 625 MHz-domain clock" in `design/README.md` | **conflict**, see the TX clock converter row above |
| `ckd_cmos` | output port of `tx_top` | follows `ckdp/ckdn` | no consumer: the RTL has one clock, `clk` at 625 MHz, and nothing connects `ckd_cmos` |
| `clk` (word clock) | `serdes_digital_top.v` L12 | 625 MHz | no divider produces it in the committed design |

## Converter mapping

Each record is attributed to the one path it exercises.

| Converter | Instance, cell | Direction and signal | Rate | Record | What the record covers |
|---|---|---|---|---|---|
| TX clock | `Xlvl`, `tx_lvl_cml2cmos` (`tx_top.spice` L31) | CML -> CMOS, `ckdp/ckdn` -> `ckd_cmos` | 2.5 GHz | [`sim/tx/records/20261110-224611-4092fc2-mos`](../sim/tx/records/20261110-224611-4092fc2-mos/record.md), request `tx_mos_tx_lvl_cml2cmos` | the clock path only, at 2.5 GHz with an ideal source; not the 625 MHz-domain rate `design/README.md` names, and not the word-data path |
| RX data and edge | `Xlvl_d0`, `Xlvl_d180`, `Xlvl_e90`, `Xlvl_e270`, `lvl_cml2cmos` (`rx_top.spice` L26 to L32) | CML -> CMOS, latch outputs `qp/qn_*` -> `d0`, `d180`, `e90`, `e270` | 5 Gb/s per wire | [`sim/rx/records/20261123-025944-cd608e7-mos`](../sim/rx/records/20261123-025944-cd608e7-mos/record.md), request `lvl_cml2cmos` | one instance driven by the latch it loads; the four have the same cell, the same latch type and the same clock amplitude, so one covers four |
| TX word data | none | CMOS -> CML at the 16 x 625 Mb/s word boundary (DR-008 B1 item 1) | 625 Mb/s per wire | none | **no implementation** at `f9dd877`: no CMOS-to-CML cell exists under `design/`, and no bench drives one |

## Evidence per implemented row

The gate asks for a PVT, post-layout STA or SPICE record for each CMOS stage
clocked at >= 1.25 GHz and for each converter. "First-look bounds" are not
requirements: they are the limits a request declares so its corners grade, and
they are stated where used.

| Row | Record | Stimulus | Load | Corner set | Parasitics source | Measured | Applicable requirement | Verdict |
|---|---|---|---|---|---|---|---|---|
| TX S4 clock squarer (CMOS at 5 GHz, inside the CML cell) | `sim/tx/records/20261110-224611-4092fc2-mos`, `tx_mos_mux2to1_cml` | ideal complementary 5 GHz clock, 0.4 V per side (an assumption) | predriver input + 20 fF | 5 MOS x 3 V x 3 T = 45 | none (schematic) | `sqa` high 0.525 to 1.335 V, low -0.014 to 0.264 V; at 3 corners (`ss_wcs/1.080V/-40C`, `ss_wcs/1.080V/27C`, `fs_typ/1.080V/-40C`) its swing is under half of vdd | none (the clock requirement does not reach inside the cell) | partial: ideal clock, no limit, 36/45 pass, 7 fail, 2 error |
| TX clock converter `Xlvl` | `sim/tx/records/20261110-224611-4092fc2-mos`, `tx_mos_tx_lvl_cml2cmos` | ideal complementary 2.5 GHz, 300 mV single-ended, vdd-referenced CML, 20 ps edges | 20 fF | 45 (MOS corner ganged with HBT/CAP/RES) | none (schematic) | 45/45 "pass" with no limit declared: duty 27.3 to 39.2 % (typ 34.8 %); delay LH 113.7 to 210.4 ps, HL 59.6 to 129.3 ps from the input zero crossing to vdd/2; output high 68 to 101 % of vdd; Idd 0.23 to 0.56 mA | none defined for `ckd_cmos`; the +/-1 % duty in `clock-requirement.md` is on the 5 GHz clock this block receives, not on this output | partial: ideal input, rate in conflict, no limit, no consumer |
| RX converter `Xlvl_d0/d180/e90/e270` | `sim/rx/records/20261123-025944-cd608e7-mos`, `lvl_cml2cmos` | driven by `latch_cml`: ideal 5 GHz four-phase clock, +/-10 mV data, so the input is the 1010 stream at 5 Gb/s per wire; latch output swing 0.29 to 1.14 V differential, common mode vdd - 0.07 to vdd - 0.30 V | 20 fF (assumed) | 45 (MOS corner ganged with HBT/CAP/RES) | none (schematic; the cell has no layout) | 2/45 inside the first-look bounds; see below | none defined (DR-008 item 3: "not sized, simulated or specified") | **fails its first-look bounds at 43/45**; schematic only |
| CMOS stage clocked >= 1.25 GHz | none exists | | | | | | | open: S3 and S2 of the RX deserializer would be CMOS at 2.5 and 1.25 GHz if built behind the implemented converter; they are not built |
| TX word-data CMOS -> CML | no cell | | | | | | | open: not implemented |

### RX converter record, read

First-look bounds in `sim/rx/lvl_cml2cmos.request.json`: `d0` reaches 90 % of
vdd rising and 10 % of vdd falling within 100 ps of the clock edge that closes
the latch's sample phase (half the 5 GHz period, the `latch_regen` limit). All
45 corners ran on the batch fleet (job `klt-sim-0b9e4e0f9fe7`, 0 error):

- 14 corners: the output never rises above vdd/2. Eleven are at 1.080 V (all
  five process corners at -40 C, four at 27 C, and `ss_wcs` and `fs_typ` at
  125 C); three are at 1.200 V (`ss_wcs` and `fs_typ` at -40 C, `ss_wcs` at
  27 C). This is not only the latch's 1.080 V swing limit: at
  `ss_wcs/1.200V/27C` the latch output swings 0.62 V and the converter still
  stops at 0.274 V.
- 4 corners: the output crosses vdd/2 but the rising edge stops under 90 % of
  vdd (`tt_typ/1.200V/-40C` reaches 1.060 V, 88 %).
- Of the 27 corners that reach 90 %, the time from the hold edge is 86.4 ps
  (`ff_bcs/1.320V/125C`) to 210.2 ps (`ss_wcs/1.200V/125C`); 24 are over 100 ps.
  Of the 31 that reach 10 %, 66.7 ps (`ff_bcs/1.320V/-40C`) to 185.8 ps
  (`sf_typ/1.080V/125C`); 18 are over 100 ps.
- 2 of 45 are inside both bounds with full levels: `ff_bcs/1.320V/-40C` and
  `ff_bcs/1.320V/27C`. At 1.080 V and at 1.200 V, 0 of 15 each.
- Typical, `tt_typ/1.200V/27C`: output 1.215 V high, -0.030 V low; 158.4 ps
  from the hold edge to 90 % rising and 114.1 ps to 10 % falling; the output
  is high for 158.7 ps and low for 241.2 ps per 400 ps where the input is
  200/200; supply current 0.443 mA.

## Word-clock domain, 625 MHz

The word domain is the one CMOS clock domain with post-route evidence. It is
cited here for completeness; its closure is issue #197's and this document
re-runs nothing. From `corners[]` of the in-flow report
[`layout/digital/records/2026-11-21-eec180f/report.json`](../layout/digital/records/2026-11-21-eec180f/report.json)
(`name`, `setup_slack_ns`, `hold_slack_ns`; `timing_status: constrained` in
every corner; `clock_skew_ns` 0.09047, `interconnect_corner: nom`,
`spef_sta: null`, i.e. the record's "ideal clocks, global-routing RC
estimates" model):

| corner | setup slack (ns) | hold slack (ns) |
|---|---|---|
| `fast_1p32V_m40C` | +0.63951 | +0.13524 |
| `fast_1p65V_m40C` | +0.92507 | +0.09988 |
| `slow_1p08V_125C` | **-0.73221** | +0.31988 |
| `slow_1p35V_125C` | +0.13260 | +0.20860 |
| `typ_1p20V_25C` | +0.13280 | +0.20191 |
| `typ_1p50V_25C` | +0.62616 | +0.13953 |

Setup is met at five corners and missed at slow 1.08 V / 125 C (TNS -108.556
ns there; the report's top-level `setup_violation_count` is 394). Hold is
positive in all six.
The 1.6 ns period is a synthesis constraint from the PROPOSED spec, not a
ratified number. The +0.014 ns pre-layout figure of DR-005/DR-006 is
historical.

The standalone `klt sta` report beside it, `sta-corners.json`, is a different
model (`clock_mode: ideal`, `geometry_source: routed`, no SPEF, no wire-load
model, no clock uncertainty). Its per-corner worst setup slack, over the
constrained endpoints only, is -0.47660 ns at `slow_1p08V_125C` (217 violating
endpoints, TNS -39.1535 ns) and +0.28679, +0.28402, +0.73045, +0.73587 and
+0.99410 ns at the other five corners; the worst path is
`u_pd/_699_/Q -> u_pd/_721_/D` at all six. **Disclosure (#239):** in every one
of the six corners `constraint_completeness.status` is `incomplete`,
`unconstrained_endpoints.count` is 43 (top-level output ports such as
`eye_ph_off[*]`, `eye_smp_off[*]`, `pi_code[*]`, which carry no setup check in
that model) and `unclocked_registers.count` is 0 (no register escapes the
setup check). A violating-endpoint count from that report is taken over the
constrained set only, and nothing here attributes the 217-versus-394
difference between the two models.

## Gate G3 status

G3 here is DR-014's evidence gate for R2 (clock-domain list plus records). It
is not the simulation gate G3 of [`validation-plan.md`](validation-plan.md)
("does the digital partition hold 625 MHz post-layout", issue #197), and not
that plan's gate G2, which asks for a converter record at the 625 MHz boundary.

| G3 asks for | State at `f9dd877` | Closes it? |
|---|---|---|
| A per-stage clock-domain list | this document; every row traced to a netlist or RTL line | yes |
| Record for each CMOS stage at >= 1.25 GHz | no serializer or deserializer stage is clocked that fast today; the CMOS that does run at 5 GHz is the TX squarer inside a CML cell (ideal-clock sizing record) and the RX converter output (record above) | partially, schematic only |
| Record for the level converter | TX clock converter: ideal-input 2.5 GHz sizing record; RX converter: latch-driven schematic record, fails its bounds at 43/45; TX word-data converter: no cell | no |
| Post-layout | no analog cell has a layout; the converters have no extracted parasitics | no |
| A requirement to grade against | none for either converter (DR-008 item 3) | no |
| The 1.25 GHz and 2.5 GHz stages assigned | DR-008 is Proposed; S3 conflicts, S2 and S1 are gaps | no |
| 625 MHz word domain | in-flow post-route STA: five of six corners meet setup, slow 1.08 V misses (#197) | no |

What keeps G3 open, as work items rather than findings:

1. The RX converter does not work at 43 of 45 corners against bounds that are
   not even requirements. It needs a sized or re-topologised cell and a
   requirement (output levels, valid window at 5 Gb/s per wire), then a new
   record from `sim/rx/run_sizing.sh mos` (#251).
2. Where the RX converter sits is undecided: DR-001 decision 3 says the first
   divided clock, DR-008 B1 says the 625 MHz word, the netlist says the latch
   output. Until a decision record settles it, the stages behind it cannot be
   assigned, and if it stays at the latch output the first deserializer stage
   is CMOS at 2.5 GHz, which R2 does not allow today (#253).
3. The TX clock converter's input rate is stated two ways (2.5 GHz in the
   bench and in decision 3's wording, 625 MHz-domain in `design/README.md`),
   its only record is at 2.5 GHz from an ideal source, and nothing consumes
   `ckd_cmos` (#252).
4. Neither converter has post-layout evidence; neither has a load that is
   known rather than assumed (20 fF).
5. The divider chain and the TX word-data converter are not implemented; the
   TX serializer stages S1 to S3 are not implemented.
6. DR-008's 16-wire word does not account for the RX edge word (16 more
   wires at 625 Mb/s).

## Conflicts, unassigned and proposed rows

- **Conflicting**: TX S3 (DR-001 prose CML versus R2 unassigned, B1 proposes
  CML); TX clock converter (2.5 GHz at "the first divided clock" versus B1's
  625 MHz boundary, and `design/README.md` naming `ckdp/ckdn` the 625 MHz-domain
  clock); RX converter (implemented at 5 Gb/s per wire, B1 places it at
  625 Mb/s).
- **Unassigned**: TX S2 and S1; the divider chain; RX S3, S2 and S1 mirrors;
  the RX edge word's 16 wires.
- **Proposed only**: TX word-data CMOS -> CML converter (DR-008 B1 item 1);
  option B3 (32:1, 312.5 MHz word).

## Conventions

Records cited here are append-only; a correction to one is a dated `Erratum`
paragraph at its end, and a correction to a finding here is a dated paragraph
under the table it corrects, citing the commit or PR. A new run goes in a new
record directory and this file is updated to cite it; nothing above is edited
to match a later result.
