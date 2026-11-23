# TX core record, 2026-11-23 (source commit 4e3c174)

Append-only. Re-run with `layout/analog/tx/scripts/tx-core-regen.sh` into a new
dated directory. Supersedes `2026-11-21-4ff16d8` for `tx_lvl_cml2cmos` (review
of PR #212, issue #199): that record's `out` leg `XMN3.U0_D→XMP3.U0_D` was
rejected (`comes within 0.21um of already-routed net 'o1'`) and the router
re-planned the whole output route. Here **every planned leg is drawn as
planned**: 0 unrouted legs in `tx_lvl_cml2cmos/compose.response.json`, enforced
by `layout_common.assert_plan_followed` at generation time. The other five
cells (`bias`, `ffe_en`, `mux2to1_cml`, `predriver`, `driver_ffe`) are
unchanged: shelf-packed, boundary pins, **no routing**.

## What changed in the plan

At the `XMN3.D` pad centre the `out` vertical ran 0.02 um from `XMN3.G`'s
metal2 landing (net `o1`). `out` now leaves the pad horizontally to a metal2
lane 0.75 um east of the pad centre, rises clear of both landings and re-enters
`XMP3.D`; a 0.45 um shift alone left a sliver (`metal2.space.1`, one marker) in
a scratch build and was not recorded.

| Item | Value |
|---|---|
| Planes | metal2: `vss, s, d1, o1, out`; metal3: `vdd, vbm` |
| Route length | vdd 106.3, vss 73.6, s 24.5, d1 27.3, o1 59.1, vbm 111.4, out 15.2 um |
| Body ties / well | 1 substrate tie, 1 well tie, 1 merged NWell polygon, enforced before the GDS is written |
| DRC | `tx_lvl_cml2cmos/drc.report.json`: `status: clean`; `.provenance.input.content_hash` is the sha256 of `tx_lvl_cml2cmos.gds` in this record |
| LVS | `tx_lvl_cml2cmos/lvs.report.json`: `status: match`, engine `klayout`, devices 9/9, nets 9/9, `combine_devices: true` (ng=2 fingers and the drawn rppd); layout hash is that GDS, reference hash is `design/tx/netlists/tx_lvl_cml2cmos.spice`; `power_connectivity.status: unchecked` |
| Evidence gates | `scripts/check-ci.sh fresh` axes 7-8 and `scripts/check-analog-lvs-fresh.sh` select this (newest) record first and bind both reports to its GDS and the reference |

Engine note: KLayout 0.30.14 against the tested 0.30.12 (`klayout_version_mismatch:
true`); verdicts unaffected.

## What is not routed here

`bias`, `ffe_en`, `mux2to1_cml`, `predriver`, `driver_ffe`, the top-level
interconnect and the core-to-pad seam stay with #127; partition-level LVS stays
with #128. No claim that T1 item 4 (analog) is met.

## Addendum (2026-11-23, issue #258)

Self-containment pass: the negative control and the parameter probes below
were run against **this record's** GDS — scratch copies under /tmp, this
record's `lvs.request.json` with absolute paths, reference unchanged, pinned
klt 0.9.0 / KLayout 0.30.14 (the same engine note as above; the un-perturbed
base copy re-verified `match` 9/9 devices, 9/9 nets, before each control).
Scratch files are not committed.

- Negative control: remove one device instance (`tx_lvl_cml2cmos_XMP3`, cell
  `XMP3__tx_lvl_cml2cmos_XMP3`): `mismatch`. Erase every Metal3 (30/0) shape —
  21 shapes, `vdd` + `vbm` unrouted: `mismatch`.
- LVS parameter coverage of the committed `lvs.report.json`
  (`options.compare_parameters: null`): the drawn `rppd` had **zero**
  parameters compared — `R` is the literal-0 placeholder
  (`device.placeholder_value`: the reference `rppd` comes from a subckt call,
  `reference.form: "subckt-call"`) and `A/L/P/W` are geometry secondaries
  (`device.geometry_not_compared`: the resistor is paired on topology alone;
  its geometry could differ by any amount and the run would still report
  `match`). Reporting-gap context:
  https://github.com/2AMLogic/klayout-tools/issues/5653
- Probes (scratch): (1) `options.compare_parameters: {"rppd": ["W", "L"]}` on
  an otherwise-unchanged copy keeps `status: match`, with the coverage block
  now `compared: ["L", "W"]` and no `parameter_tolerance` needed — the drawn
  geometry agrees with the reference `w=0.5u l=19.23u`; worth requesting at
  the next regeneration so the resistor's coverage is positive rather than
  empty. (2) Shrinking one MOS's drawn W (XMP3 active height 4.0 → 3.4 um,
  topology intact) flips the verdict to `mismatch` (`device.property: matched
  device parameter 'w_um' differs`) — MOS W/L are compared by default at
  klt 0.9.0 with `compare_parameters: null`.
- Seeded-leg rejection data point behind this record's plan (link carried from
  the superseded `2026-11-21-4ff16d8`): all 2026-11-21 rejections and the two
  pad-geometry constraints are posted as generic data points on
  2AMLogic/klayout-tools#1962 (comment 2026-11-21):
  https://github.com/2AMLogic/klayout-tools/issues/1962#issuecomment-7054026274
