# DR-003: Supplies, device flavours and HBT breakdown limits

- **Status**: proposed (ratification is the operator's act on merge)
- **Date**: 2026-10-17
- **Decided by**: Builder agent, issue #2
- **Fixes rows**: target-spec R3

## Context

PDK process specification Rev. 1.2 (`libs.doc/doc/SG13G2_os_process_spec.pdf`,
§3, "min" column) gives the HBT breakdown limits that bound any node that
sees the CML supply:

| Device | BVCEO | BVCBO | BVEBO | fT / fmax (target) |
|---|---|---|---|---|
| `npn13G2` | 1.4–1.6 V | 3.8–4.8 V | 1.0–1.6 V | 300–350 / 400–450 GHz |
| `npn13G2L` | 1.4–1.6 V | 3.8–4.8 V | 1.0–1.6 V | 280–330 / 380–430 GHz |
| `npn13G2V` | 2.2–2.5 V | 7–8.5 V | 1.0–1.8 V | 90–120 / 280–330 GHz |

Min–max are the process-control spec window, measured on minimum devices;
BVCEO is the open-base value. Process rev 1.2 describes a 1.2 V thin-oxide and
3.3 V thick-oxide MOS option. The PDK's IO liberty corner files span
1.08–1.32 V (core) and 3.0–3.6 V (IO), consistent with ±10 %; the process
spec itself states no supply tolerance, so ±10 % is **unconfirmed** as a PDK
figure and is a proposal here.

## Options considered

- **3.3 V CML rail.** Every HBT collector node would sit at up to 3.63 V, above
  BVCEO of every flavour. Rejected.
- **`npn13G2V` with ~1.8–2.0 V.** Clears BVCEO but fT 90–120 GHz at 5 GHz
  CML is a poor use of the device and costs speed margin. Kept as the fallback
  if `npn13G2` breakdown behaviour in the switching limit proves unusable.
- **`npn13G2` on 1.2 V ±10 %.** Maximum 1.32 V is 94 % of the smallest BVCEO
  minimum (1.4 V); thin headroom, but the stack (tail source + pair +
  load) fits 1.2 V CML at 0.3–0.5 Vppd swings. Chosen.

## Decision

- **CML rail**: 1.2 V nominal, tolerance ±10 % *(unconfirmed, proposal)*, all
  HBT stages `npn13G2`, MOS tail/bias devices thin-oxide. **No HBT collector
  node may exceed 1.32 V** (1.4 V is the smallest BVCEO in the spec); no
  emitter-base may be reverse-biased beyond 1.0 V (smallest BVEBO), which
  bounds the RX input swing and clamps the pad network must provide.
- **Digital core**: 1.2 V thin-oxide CMOS from the same 1.2 V rail domain, with
  separate regulated/filtered supply pins for CML and digital.
- **IO ring**: 3.3 V thick-oxide only for the PDK's pad/ESD cells.
- **Not simulated**: every breakdown check in this record is arithmetic on the
  PDK table; no transient has been run. Whether `npn13G2` models include
  breakdown is for #3 and the bring-up smoke tests to show; until then the
  checks are `not simulated`.

## Consequences

- A 1.2 V CML rail leaves little headroom: the swing and tail-current budgets
  in target-spec TX and RX rows (R4–R10) depend on it.
- Pad network (target-spec R18, R19) must clamp the HBT input below BVEBO.
- A CML rail above 1.32 V needs a superseding record.
