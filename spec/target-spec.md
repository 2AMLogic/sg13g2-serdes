# sg13g2-serdes target specification

**Status: PROPOSED — not ratified.** Ratification is the operator's act on
merge; no agent marks it ratified. Every number is labelled by its basis:
**PDK** (cited from a PDK document), **arith** (arithmetic written out in the
cited record), **sibling** (a sibling's ratified target, cited at a commit) or
**proposal** (an engineering judgement with reasoning in a decision record or
the row). No number here is a measurement; nothing is designed or simulated yet.
10 Gb/s is the driving target; 12.5 Gb/s shapes nothing (`CLAUDE.md`).

Decision records: [`decisions/`](decisions/). Clock interface:
[`clock-requirement.md`](clock-requirement.md). Channel: [`channel/`](channel/README.md).

## Corner sets

Every recorded analog result states which set it ran. Corner names are the
PDK's (`libs.tech/ngspice/models/corner*.lib`).

| Set | Process | Supply | Temperature | Points |
|---|---|---|---|---|
| **PVT-full** | MOS lv and hv: `mos_tt/ss/ff/sf/fs` (5); HBT: `hbt_typ/bcs/wcs` (3), with CAP/RES/DIO corners ganged to the same typ/bcs/wcs index (ganging is a proposal; confirm in #3) | each rail −10 % / nominal / +10 % (proposal, **unconfirmed** as a PDK tolerance; see DR-003) | −40 / 27 / 125 °C (proposal, process spec Rev. 1.2 states temperature coefficients are extracted for −40…125 °C) | 5×3×3×3 = 135 |
| **PVT-edge** | `ss`+`hbt_wcs`, `ff`+`hbt_bcs`, `tt`+`hbt_typ` | worst-speed pairings only (low V/hot with ss/wcs, high V/cold with ff/bcs) plus nominal | the matching extremes | 7 |
| **TT-27** | `mos_tt`, `hbt_typ` | nominal | 27 °C | 1 (debug only, never a recorded result on its own) |

MOS and HBT corner families are independent libraries, so a "worst case" for a
mixed stage is not obvious; PVT-full crosses them (ganged with passives) rather
than assuming which pairing is worst. Statistical mismatch/Monte Carlo is run
only where a row says so (offsets, CDR samplers).

## Parameter table

Verification column names the testbench class; no testbench exists yet.

| # | Parameter | Target | Fallback | Stretch | Verification | Corners | Basis |
|---|---|---|---|---|---|---|---|
| R1 | Line rate | 10 Gb/s | 5 Gb/s (full-rate, same 5 GHz clock) | 12.5 Gb/s (outside the clock band, see clock-requirement) | Rate is "met" when R15 BER ≤ 1e-12 (extrapolated) holds over R14 at that rate | PVT-full | CLAUDE.md; DR-001 |
| R2 | Architecture | half-rate TX and RX at 5 GHz; 4-phase RX; HBT CML for the last 2:1 mux, driver, RX front end, 4 sampling latches and 5 GHz clock path; CMOS ≤ 625 MHz; **16:1, 16-bit word @ 625 MHz** | full-rate at 5 Gb/s | quarter-rate RX (2.5 GHz) | Netlist/RTL review against DR-001; boundary checked by clock-domain list | n/a (structural) | DR-001 |
| R3 | Supplies and device flavours | CML 1.2 V ±10 % with `npn13G2` and thin-oxide MOS bias; digital 1.2 V thin-oxide; IO ring 3.3 V thick-oxide only; no HBT collector node > 1.32 V; no reverse Vbe > 1.0 V | `npn13G2V` on ~1.8–2.0 V CML rail | — | Node-voltage extraction per corner from transient runs; breakdown limits checked against the table below | PVT-full, incl. the +10 % supply | PDK (breakdown), proposal (rails); DR-003 |
| R4 | TX differential output swing into 100 Ω | 500 mVppd | 300 mVppd | 800 mVppd | Transient, 100 Ω differential load, PRBS-7, measure steady-state swing; loaded by the R18 pad model | PVT-full | proposal |
| R5 | TX FFE | 2 taps (main + 1 post-cursor); post-cursor de-emphasis 0–6 dB in ≥ 4 steps | no FFE | 3 taps | Pulse response measured in simulation; step-by-step against the model | PVT-full | proposal (README draft) |
| R6 | TX output return loss (SDD22, 100 Ω) | ≤ −10 dB from DC to 5 GHz | ≤ −8 dB to 5 GHz | ≤ −10 dB to 7.5 GHz | AC/S-parameter of driver + pad network, driver on | PVT-full | proposal |
| R7 | TX rise/fall (20–80 %) | ≤ 30 ps (0.3 UI) | ≤ 50 ps (0.25 UI at 5 Gb/s) | ≤ 25 ps | Transient step, R4 load | PVT-full | proposal |
| R8 | RX input sensitivity | 50 mVppd at the pad for BER 1e-12 (extrapolated) after R14 | 100 mVppd | 25 mVppd | Statistical-eye with sampler offset/noise from Monte Carlo records (DR-002) | PVT-full + MC on samplers | proposal |
| R9 | RX termination and return loss | 100 Ω differential ±10 %; SDD11 ≤ −10 dB to 5 GHz | ±15 %; ≤ −8 dB | ≤ −10 dB to 7.5 GHz | DC resistance and AC/S-parameter of termination + pad | PVT-full, incl. resistor corners | proposal |
| R10 | RX CTLE | peaking 0–10 dB at 5 GHz in ≥ 8 steps (covers CH-A's 10.18 dB with margin for FFE to share) | peaking 0–6 dB | + 1 DFE tap (not designed) | AC response per setting; combined channel+FFE+CTLE pulse response | PVT-full | proposal; R14 |
| R11 | CDR | bang-bang (Alexander), half-rate, 4 phases, digital loop filter | CTLE only, forwarded clock (no CDR) | — | Time-domain behavioural model fitted to latch records (DR-002); lock/hold from simulation | PVT-edge for the loop, PVT-full for the latch fits | README draft; DR-002 |
| R12 | Jitter-tolerance mask (sinusoidal, UIpp) | ≥ 0.15 above 10 MHz; −20 dB/dec up to ≥ 1.5 at 1 MHz and ≥ 15 at 100 kHz | ≥ 0.1 above 10 MHz, ≥ 1 at 1 MHz | ≥ 0.2 above 10 MHz | Statistical sim sweeping SJ amplitude vs frequency to BER 1e-12 | PVT-edge | proposal; shape is common practice, **not taken from a named standard** |
| R13 | Frequency-offset tolerance | ±300 ppm | ±100 ppm | ±500 ppm | CDR behavioural run at offset, no slips over 1e6 UI | PVT-edge | proposal |
| R14 | Channel loss at Nyquist | CH-A: 10.18 dB @ 5 GHz | CH-B: 5.09 dB @ 5 GHz (CH-A at 5 Gb/s: 5.65 dB @ 2.5 GHz) | CH-A at 12.5 Gb/s: 12.38 dB @ 6.25 GHz | Committed model `channel/channel_model.py`; fed to the statistical sim | n/a (a model) | proposal; DR-004 |
| R15 | Error-rate method | PRBS-31; statistical eye + behavioural CDR; 1e-12 by dual-Dirac extrapolation; labelled simulated/extrapolated, never measured | PRBS-7 | — | DR-002 | PVT-full for stage records | DR-002 |
| R16 | Power per lane (TX+RX+CDR+pads, **excluding** clock source) | ≤ 150 mW (15 mW/Gb/s) | ≤ 250 mW | ≤ 100 mW | DC supply power at nominal rails over PRBS-31, from block simulations summed | PVT-full | proposal, not derived from a device-level estimate yet |
| R17 | Area per lane (core + pads) | ≤ 1.0 mm² | ≤ 2.0 mm² | ≤ 0.6 mm² | Layout bounding box | n/a | proposal; shuttle area limit unknown |
| R18 | Pad capacitance budget at 5 GHz (signal pad incl. ESD) | ≤ 100 fF | ≤ 150 fF | ≤ 60 fF | Extracted/EM pad+ESD model at 5 GHz; **the PDK's `bondpad` model is an empty placeholder** (`sg13g2_bondpad.lib`), so no value comes from the PDK | PVT-full (ESD junction caps vary) | proposal; see Pads |
| R19 | ESD | HBM 2 kV target on supply and non-HS pins; high-speed pins protected by the smallest PDK diode clamp that meets R18 (level to be measured, none claimed) | 1 kV HBM | 4 kV HBM | Extracted clamp characteristics only; no ESD qualification claim | n/a | proposal; see Pads |
| R20 | Clock requirement | 5.0 GHz, 4 phases, duty ±1 %, quadrature ±2°, RJ ≤ 0.5 ps rms | duty ±2 %, quad ±5° | — | See `clock-requirement.md` | PVT-full on the receiving buffer | proposal |
| R21 | Signoff | DRC + LVS clean, pads included, post-layout re-verified | — | — | `klt drc` / `klt lvs`; deck-gap issues filed at `2AMLogic/klayout-tools` | n/a | README draft |
| R22 | On-chip test access | PRBS-7/31 generator and checker with error counter; TX→RX loopback (serial, at the pad side) and parallel loopback; eye monitor by stepping sampling phase and sampler offset; all through a ≤ 8-pin digital control/readout | PRBS checker + parallel loopback only | — | RTL tests + behavioural eye-monitor sim | n/a | proposal; answers open question 3 |

HBT breakdown limits on every node that sees the CML rail (PDK process spec
Rev. 1.2 §3, min column; open-base BVCEO; **not simulated**, see DR-003):
`npn13G2` BVCEO 1.4 V, BVCBO 3.8 V, BVEBO 1.0 V. R3 uses these as hard limits.

### Pads and ESD (R18, R19)

What the PDK offers (`libs.ref/sg13g2_io`, `libs.tech/ngspice/models`): a CMOS
IO-cell library (3.3 V IO, diode and clamp cells such as `sg13g2_DCNDiode`,
`sg13g2_Clamp_N43N43D4R`), ESD diode models (`sg13g2_esd.lib`, e.g.
`diodevdd_2kv`) and ESD clamp device recognition (`nmoscl_2`, `nmoscl_4`,
`scr1`). **What must be drawn**: the high-speed pad and its ESD network. The IO
cells are built for CMOS signalling and their pad capacitance is not stated in
any document searched; the `bondpad` model is a placeholder with no
capacitance. The 5 GHz pad capacitance, return loss and the core-to-pad seam are
therefore the least supported rows in this spec. They need a pad-network
study (extraction or EM) before R4, R6 and R9 can be graded.

## Open questions: disposition

| Question | Disposition |
|---|---|
| Does ngspice simulate HBT CML at 5 GHz with acceptable runtime and convergence across all corners, and with which HBT model? | **Open; owner #3** (bring-up smoke results). The PDK ships VBIC (`sg13g2_hbt_mod.lib`, corners `cornerHBT.lib`: `hbt_typ/bcs/wcs`). Nothing here is simulated. |
| Can a bang-bang CDR be verified credibly with behavioural models fitted to transistor-level latch results, and how is the fit validated? | **Answered as a procedure in DR-002** (fit on a subset, validate on held-out corners/stimuli, stated tolerance); whether the fit passes is **open**. Owner: the CDR-verification issue to be filed under the T1 tracker (#5). |
| What on-chip test access does a shuttle part need? | **Answered as a proposal: R22.** |

## Not decided here

Line coding/protocol; the clock source (see clock-requirement.md); the
`consumes:` manifest (operator decision); any schematic or RTL.
