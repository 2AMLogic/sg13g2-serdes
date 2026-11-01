# DR-006: Digital partition restructured to meet the 1.6 ns word clock (pre-layout)

- **Status**: proposed
- **Date**: 2026-11-01
- **Decided by**: builder (issue #36); ratification needs a human or Champion

Records are append-only: a ratified record is never rewritten; a new record
says what it supersedes. This record **does not supersede DR-005** (still
proposed) and does not change the ratified spec: the target stays 16:1 / 625 MHz
/ 1.6 ns.

## Context

DR-005 measured the digital partition at -2.09 ns worst setup slack (fmax
270.7 MHz) and proposed option 2 then 1. Option 2 (declaring `serdes_ctrl`
configuration quasi-static, with multicycle/false-path constraints) needs a
design statement nobody has made. Following the issue's sequencing, only the
option-1 restructuring that needs no such statement was done first, and it was
enough: **no multicycle or false-path constraint exists or was added**, and
`scripts/sta-paths.sh` is unchanged.

## What changed (option 1)

| Block | Change |
|---|---|
| top | each `serdes_ctrl` mode/pulse output re-registered before the datapath (one clock) |
| `serdes_loopback` | selected `rx_d`/`rx_e` registered (the RX seam register) |
| `serdes_cdr_pd` | 1 -> 3 stages: votes + 4-bit group counts, totals, difference |
| `serdes_cdr_filter` | integrator keeps the unclamped sum with registered over-range flags; carry-select adder; phase accumulator split into 7-bit halves, `pi_code` = upper half at +3 |
| `serdes_prbs_chk` | 5-stage pipeline (see the module header); counters keep registered carries; `err_cnt` port is the resolved value |
| `serdes_eye_mon` | registered end-of-phase flags; counters with registered carries; `done` one clock after the last word |
| `serdes_prbs_gen` | word bits as flat XOR masks of the state (same bits) |
| `serdes_ctrl` | checker counters staged through a register before the snapshot |

## Result (pre-layout, one corner, ideal clock, no wires)

`scripts/sta-paths.sh`, OpenSTA 26Q3 via the pinned `klt sta`, `typ_1p20V_25C`,
netlist `rtl/synth/serdes_digital_top_synth.v`: worst setup slack **+0.014 ns**
at 1.6 ns, fmax 630.5 MHz, 0 violating endpoints, worst hold +0.19 ns. Evidence:
`rtl/synth/sta/`. This is a pre-layout single-corner estimate. A margin of ~1 %
will not survive wire load, clock skew or other PVT corners; closing the placed
design is P&R work (#25). It is not a PVT or post-layout claim.

## Costs and behaviour changes (what a reviewer must accept)

1. **CDR loop delay 2 -> 7 clocks** (RX register 1, phase detector 3, filter to
   `pi_code` 3). On the top bench's bang-bang plant at +300 ppm the worst phase
   error after acquisition rose from 462 to 1618 LSB (half a UI = 4096 LSB) and
   the integrator now rings around its mean (39.8 vs ideal 39). No slip, but the
   margin is smaller. **No loop analysis exists on `main`** (DR-001/DR-002 and
   `spec/clock-requirement.md` do not contain one), so this latency could not be
   checked against one; that analysis is filed as #62. KP/KI were not
   retuned.
2. **Checker semantics** (`serdes_ref.PrbsChk` follows the RTL cycle by cycle):
   loss of lock is decided from the registered word result and reaches the lock
   state four words late, so the lost word and up to four following words are still
   counted as locked (up to ~64 extra bit errors on a true loss); lock gain is
   unchanged (applied to the next word). The hunt history is the received bits
   (previously the older half kept predicted bits after a loss). Lock, per-error
   counting, saturation and re-lock tests are unchanged in intent.
3. **Latency**: checker `word_valid`/`word_err` +4 clocks, SPI writes take effect
   one clock later, eye-monitor `done` one clock later, counter snapshot taken one
   clock earlier than before.
4. Area 51 291 -> 71 244 um2.

## Consequences

- DR-005 stays proposed; its question (ratify a different budget) is no longer
  forced, but a human still has to ratify or supersede it.
- 625 MHz is demonstrated for the digital partition only as the pre-layout
  estimate above.
- Option 2 was not used; the quasi-static register-write statement is not needed
  for this result and remains unwritten.
