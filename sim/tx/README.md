# sim/tx

PVT-edge sizing evidence for the TX high-speed path (issue #21). **Sizing evidence, not
a spec result and not a measurement.**

| Path | What |
|---|---|
| `make_tb.py` | generates the decks and requests below from `design/tx/netlists/` |
| `tx_sizing_ffe{0,1}_{typ,bcs,wcs}.sp` / `.request.json` | six `klt sim` requests, each 3 supplies (1.08/1.2/1.32 V) x 3 temperatures (-40/27/125 C) = 9 corners (54 over the six); FFE off or all three post-cursor slices on; HBT, capacitor and resistor corners move together |
| `tx_mos_{mux2to1_cml,tx_lvl_cml2cmos,ffe_en}.sp` / `.request.json` | three MOS-cell `klt sim` requests (issue #80), each 5 process pairings x 3 supplies x 3 temperatures = 45 corners; PSP103 and the real `r3_cmc` resistors via `osdi_preload` |
| `run_sizing.sh [mos\|vce]` | runs the six HBT requests, `mos` the three MOS requests, `vce` the R3 per-device Vce set -- six HBT + mux2to1_cml + ffe_en, every TX bench with an HBT (batch fleet via `KLT_SIM_BACKEND=batch`; no local fallback) and writes `records/<id>/` (`<id>-mos/` / `<id>-vce/` for the MOS / VCE sets) |
| `make_record.py` / `make_record_mos.py` / `make_record_vce.py` | render `records/<id>/record.md` for the HBT / MOS / VCE set |
| `make_sweep_r4.py` / `run_r4sweep.sh <proc> [tag]` / `make_record_r4sweep.py` | the R4 swing-shortfall sweep (issue #286): tail-bias and back-termination candidates on the TX sizing bench, FFE off, `r4sweep_<cand>_<proc>.{sp,request.json}`, one batch set per process pairing, record id suffixed `-r4sweep-<proc>`; the [dated verdict correction](records/20261126-r4sweep-verdict/verdict.md#erratum-2026-11-26) links the corrected probe checks and the outstanding fleet runs |
| `records/<id>/` | append-only run records; never edited after the fact |

Reproduce: `source scripts/env.sh && python3 -I sim/tx/make_tb.py && sim/tx/run_sizing.sh`.
Every record traces to `sim/pdk.json`.

What runs, HBT set: `bias`, `predriver` (x2) and `driver_ffe`. The PDK `rsil` there is a
behavioural resistor from the PDK symbol's formula. The batch worker did not honour
`corners.params` (it returned 27 corner reports for 162 dispatched points,
`params_unsupported_worker`), so FFE and the resistor corner are baked into six decks
instead of being a parameter axis.

What runs, MOS set (the blocker #3 was cleared by PR #76; same `osdi_preload` as
`sim/smoke/mixed_tran.request.json`; `rsil`/`rppd` are the real `r3_cmc` models, no
behavioural resistor):

| Cell | Bench | Measured |
|---|---|---|
| `mux2to1_cml` | ideal 5 GHz complementary clock (0.4 V swing, an assumption), A held 1 / B held 0 so the output is a 1010 stream, loaded by the `predriver` main input + 20 fF | differential swing, rise/fall between fixed +-30 mV crossings (not a conforming 20-80 %), collector V and reverse Vbe per HBT, Vce |
| `tx_lvl_cml2cmos` | ideal 625 MHz CML input (300 mV; the word-boundary clock, DR-014 — before DR-014 this bench ran at 2.5 GHz), 20 fF load | CMOS high/low, duty, propagation delay |
| `ffe_en` | enable codes 000, 001, 011, 111 stepped, vbn from the real `bias` cell, vbp unloaded | `vbp0..2` against `vbn` per code |

Corner pairing (MOS / HBT / CAP / RES sections moved together): `mos_tt`/`hbt_typ`,
`mos_ff`/`hbt_bcs`, `mos_ss`/`hbt_wcs`, and `mos_fs`, `mos_sf` with the typical
HBT/CAP/RES (no HBT skew exists for them). Parameter axes are baked into the decks.

MOS-set run status:

- `records/20261106-054913-a506fea-mos/` (klt client 0.8.0): nothing simulated. The fleet
  runner was klt 0.9.0, so all 135 units returned `batch_runner_version_mismatch`.
- `records/20261110-221849-506b37e-mos/` (client pinned to 0.9.0 by issue #80, the runner
  version re-read from a fresh fleet report): all 135 units executed on the fleet, none
  errored on the version. `tx_lvl_cml2cmos` 45/45 and `ffe_en` 45/45 corners pass.
  `mux2to1_cml` is 36 pass, 7 fail, 2 error. Sizing evidence, not a spec result.
  - The 7 failures are `vc_max_mux_outp/outn` over the 1.32 V collector limit (about 1 to
    5 mV over at 1.32 V supply, same class as the RX latch finding), kept and reported.
  - The 2 errors (`ss_wcs/1.080V` at -40C and 27C) are the fixed +-30 mV rise/fall
    thresholds never being crossed: the output swing there is under 30 mV. At other
    low-swing corners the same thresholds give rise/fall values (some negative) that are
    threshold artifacts, not 20-80 % times. Do not read rise/fall from this record.
  - Not changed in this pass: node names and `.ic` values were exercised and the benches
    ran. The rise/fall measurement still needs a 20-80 % derivation from the measured swing.
  - 0.4 V clock swing, checked against the records (issue #80, no new run): it cannot be
    validated against the predriver record `20261027-024044-2e55774`. That record measures
    the driver output (R4) and collector stress at the predriver outputs, not a predriver
    output swing, and the mux clock is not driven by the predriver anyway (it comes from
    the clock provider, `spec/clock-requirement.md`). The only written figure is the
    `sg13g2-vco` row there, "swing >= 0.40 Vpp at the tank nodes". The bench source is
    0.4 V to 0.8 V on each of `ckp`/`ckn` (0.4 V per side, 0.8 V differential
    peak-to-peak); whether the sibling's 0.40 Vpp is per node or differential is not
    stated, so the bench is at or above that floor and is not shown to match it. The
    swing is kept as is and remains an assumption, no generator change and no re-run.
    Open: the clock provider should state its swing at the mux input (per node or
    differential, with its buffer load), after which `mux2to1_cml` should be re-run at
    that swing on the fleet in a new append-only record.
  - Request bound: each 45-unit job finished in about 100 s, so the 45 x 1800 s
    `timeout_s` bound warning was advisory. `timeout_s` is now 75 s per unit in the MOS
    requests (45 x 75 s = 3375 s, under the fleet's 3600 s ceiling); per-unit runtime was
    not recorded, only the ~100 s per job, so a re-run confirms it fits: record `20261110-224611-4092fc2-mos` re-ran all 135 units at
    75 s with the same 36 pass / 7 fail / 2 error on `mux2to1_cml` and no timeouts.
  - Rise/fall stays at the fixed +-30 mV thresholds (artifacts at low swing, see above);
    no 20-80 % derivation was added because the benches keep no waveforms.
- `records/20261123-035024-5214c04-mos/` (DR-014, issue #252): the converter bench moved to
  the 625 MHz word-boundary clock (`make_tb.py` `LV_T = 1.6 ns`, was 400 ps; the request is
  unchanged -- same corners, measurements and window). `tx_lvl_cml2cmos` 45/45 corners pass
  at 625 MHz (out 1.087..1.349 V high, -0.036..-0.015 V low, tpd 60..216 ps, 0.20..0.49 mA);
  `mux2to1_cml` and `ffe_en` re-ran on unchanged decks with the same results as
  `20261110-224611-4092fc2-mos` (36 pass / 7 fail / 2 error, and 45/45). The 2.5 GHz
  converter records above are now margin data points (4x the intended rate, DR-014), not
  evidence at 625 MHz.
  - Duty (both rates): the column is a single-period trig/targ edge-pairing result --
    ngspice searches `trig` and `targ` independently from their own `td`. At 2.5 GHz it is
    a valid pulse width: **27.30..39.22 %** over the 45 corners of the two archived records,
    equal to the 50 % input duty plus the measured tpd skew (tpd HL - tpd LH) to within
    0.001 percentage points at every corner, i.e. real pulse-width distortion, not an
    artifact. At 625 MHz the `targ` edge is found in a different cycle than `trig`,
    `t_high_s` is negative and the renderer marks duty n/a in all 45 corners; no same-cycle
    duty is measured at 625 MHz. tpd, out hi/lo and Idd are unaffected.
  - `make_record_mos.py` takes the converter input rate from the reported `t_period_s`
    (heading included) and refuses to write when the corners disagree, so a record cannot
    be re-rendered under a rate its reports do not show.

## R3 per-device Vce pass (issue #242)

`run_sizing.sh vce` writes one record, `records/<id>-vce/`, that closes the R3 evidence
gap of gate G2 (tracker #238): a per-device table (24 rows) of collector / Vce /
reverse-Vbe worst cases over each bench family's full grid including the 1.32 V supply,
for every HBT on TX. Since that pass, the `tx_sizing_*` decks carry a **limited**
`vce_max_*` card (open-base BVCEO 1.4 V) for every HBT -- the post-cursor slice pairs and
tails, the predriver tails and the bias device were the missing ones -- and the `ffe_en`
bench measures the same three stress values for its one HBT (bias `XQref`). `tx_lvl_cml2cmos`
is not run for Vce: it has no HBT (R3 Vce n/a; its CMOS evidence is the `-mos` record).
Violations are kept and marked in the table, not dropped and not fixed there. First record:
`records/20261123-022802-fedf656-vce/`.

## Pad ESD benches (issue #94)

`pad_cap_5ghz.sp` (ESD diode capacitance at the pad, AC) and `pad_esd_iv.sp` (DC clamp IV), with requests; record `records/20261112-pad/`. ESD diode share only, no bondpad, no R18/R19 grade. See `spec/decisions/DR-011-pad-model-source.md`.

`pad_cap_extracted_5ghz.sp` (R18: extracted pad-metal C 70.66 fF from the #131 layout record plus the ESD diodes, AC, 27 corners); record `records/20261112-pad-extracted/`: 119.5 to 125.9 fF per leg, simulated. Lower-bound model, no R18 pass claimed. See `spec/decisions/DR-012-pad-cap-extracted-r18.md`.

`pad_esd_iv_extracted.sp` (R19 DC clamp IV on the devices extracted from `pad_esd.gds`: dantenna/dpantenna at extracted area/perimeter plus the seam resistor), request, record `records/20261112-pad-esd-iv-extracted/`. Simulated, no ESD claim. See `spec/decisions/DR-013-r19-extracted-clamp-iv.md`.

## Pad network on the TX benches (issue #142)

The R4 sizing decks (`tx_sizing_*`, generated by `make_tb.py`) and the R6 decks (`sim/bench/gen_r6_r20.py`) now load each output with the extracted pad-metal C (70.66 fF per leg, `layout/analog/pads/records/2026-11-12-fc8a7fa`) plus the PDK ESD clamp diodes, in place of the 100 fF stand-in. Records: `records/20261112-141317-582746a/` (R4, with `compare-vs-20261027.md` per-corner) and `../bench/records/20261112-r6-extracted-pad/` (R6, old run kept in `placeholder-100f/`). R4 steady swing is insensitive to the pad C; R6 SDD22 improves about 1 dB at 5 GHz. Simulated, not measured; no bondwire/package or pad coupling; clamp-model equivalence is LVS #27.
