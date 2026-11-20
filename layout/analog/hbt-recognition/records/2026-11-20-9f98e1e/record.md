# HBT `npn13G2` recognition probe, 2026-11-20 (source commit 9f98e1e)

Append-only. Do not edit; a new run goes in a new dated directory. Routing-
independent measurement for T1 item 4 (analog LVS, #128) and item 7
(post-layout, analog): does either LVS/extraction engine available at the
pinned klt recognise the SG13G2 HBT `npn13G2`, with which terminals and
parameters? Filed as #196; this record is its deliverable. Nothing here is
a measurement of silicon; it is a tool-capability record.

## Environment

| Item | Value |
|---|---|
| klt | `klayout-tools==0.9.0` (`layout/toolchain.json`; git `5dbbad05ff42265c92a6f3d2f20d1bbcd2957d49`), repo-local venv via `uv` |
| Standalone `klayout` (runset engine) | 0.30.12 on PATH (`provenance.runset.klayout_application_version`; >= 0.29, so the 0.28.x abort of `2AMLogic/klayout-tools#4397` does not apply) |
| klayout pip module (curated engine) | 0.30.13 (`environment.engine_version`) |
| PDK | IHP-Open-PDK v0.3.0 (`sim/pdk.json`; tarball sha256 `f6afb7a8…254fc` verified by the `setup-env.sh` procedure) |
| LVS runset | `ihp-sg13g2/libs.tech/klayout/tech/lvs/sg13g2.lvs`, sha256 `e01bcb1ec5858e8069bade8f7fd7ec28c1026fc2fd0590e8f611d3398a5bbbd7`, re-derived from the installed PDK and confirmed equal to the `pinned_runsets` entry `klt signoff --describe-grader` reports for klt 0.9.0 (IHP `5cccb161f749`, "v0.3.0") |

## Inputs

- **Bare PDK cell**: `npn13g2.gds` — the `npn13G2` cell written out of
  `sg13g2_pr.gds` by `klt clip --cell npn13G2` (`clip-npn13g2.report.json`;
  2 cells, 32 shapes, bbox matches `-3350,-3330;3350,3780`). sha256
  `97b08aa51764e88422cac80a5b9d2b4d396115af178e782972677c08ade35d22`. This
  is the run `2AMLogic/klayout-tools#4397` asks for; its request
  (`bare.lvs-runset.request.json`, reference `bare.ref.cir` =
  `.subckt npn13G2 c b e bn` / `.ends`) is that issue's, verbatim.
- **Smallest placed cell**: `layout/analog/rx/records/2026-11-12-0193777/
  ctle/XQa0.gds` — one `npn13G2` (`ctle/compose.request.json` block `XQa0`,
  generator `bjt_array`, `device_count` 1; the six `Nx=1` blocks of the
  newest rx record are the smallest, this is the first). sha256
  `1e581b2aef8da8f4fc34e8181c665c1412f6424afd807d04481b5bddef8e19be`.
  Reference `placed.ref.cir` mirrors the `XQa0` line of
  `design/rx/netlists/rx_top.spice` as a Q card (see the dialect finding
  below for why `we`/`le` are on it).

## Result per engine

| # | Engine | Cell | `npn13G2` recognised? | Report field that shows it | Terminals | Parameters to netlist |
|---|---|---|---|---|---|---|
| 1 | `klt lvs` curated (`klayout`) | bare | **No** | `counts.devices.layout: 0` (reference also 0; `status: match` is vacuous) | — | — |
| 2 | `klt lvs` curated (`klayout`) | placed | **No** | `counts.devices.layout: 0`; the reference HBT is `device.unmatched` (`QA0`) | — | — |
| 3 | `klt lvs` `klayout-runset` | bare | **Yes** | `device_census.layout: {"npn13G2": 1}` | C, B, E, S (substrate) | `we`, `le`, `Nx`, `m` |
| 4 | `klt lvs` `klayout-runset` | placed | **Yes** | `device_census.layout: {"npn13G2": 1}`; `counts.devices.matched: 1` with `we`/`le` on the reference Q card | C, B, E, S (substrate) | `we`, `le`, `Nx`, `m` |
| 5 | `klt extract` curated (`sg13g2` deck) | bare | **No** | `device_counts: {}` (only a `vsubs` pin) | — | — |
| 6 | `klt extract` curated (`sg13g2` deck) | placed | **No** | `device_counts: {}` (only a `vsubs` pin; `placed.extract.spice`) | — | — |
| 7 | `klt extract` `klayout-runset` | n/a | **Not available at the 0.9.0 pin** | implemented by `2AMLogic/klayout-tools#5496` for #5481, merged 2026-11-17, in no tagged klt release as of 2026-11-20; not in 0.9.0 (`klt extract --help` has no engine flag) | — | — |

Terminals/parameters in rows 3-4 are evidenced by the runset's own
extracted netlist, `XQa0.runset-extracted.cir` (attachment, produced by the
PDK's runner, command in "Negative and supporting checks"):

```
Q$1 $4 $2 $3 $1 npn13G2 we=70n le=900n Nx=1 m=1
```

four nets = collector, base, emitter, substrate (the shared substrate net is
the 4th; the runset's `extract_devices(CustomBJTExtractor.new('npn13G2',
false), {... 'S' => npn_sub ...})` declares it), and the geometry
parameters the device class compares (`CustomBJT4`: `we`, `le`, `Nx`, `m`).

The expected and non-measured mismatches: the bare runset run compares
against #4397's deliberately empty reference (1 `topology` mismatch); the
placed runs compare against an unlabelled, unrouted cell (`pin.unmatched`
on `Q1_C/Q1_B/Q1_E/vss`; request `deck_vars.ignore_top_ports_mismatch` set
to the PDK regression's own switch). Neither is the recognition result.

## Dialect finding (matters for #128)

The runset's schematic dialect for the HBT is a **Q card** whose model is
`npn13G2` with **`we` and `le` required**: with only `Nx=` (the form the
design netlist `rx_top.spice` uses, `XQa0 ca0 hpp ea0 vss npn13G2 Nx=1`)
the compare leaves both devices unmatched — see "Negative and supporting
checks" (1). A #128 reference therefore cannot be the design netlist as
written; it needs per-device `we`/`le` (for this PDK cell, `we=0.07u
le=0.90u`, the values the PDK's own testcase CDL and the placed instance's
`Ae=1*1*0.07*0.90` GDS property carry) on Q cards, or a generator that
emits them.

## Negative and supporting checks (run 2026-11-20, scratch copies, not committed)

1. **Paramless reference**: the PDK runner (`run_lvs.py --layout=XQa0.gds
   --netlist=<ref> --topcell=ctle_XQa0 --ignore_top_ports_mismatch`) with
   the reference Q card carrying only `Nx=1` reports "Netlists don't
   match"; adding `we=0.07u le=0.90u` (with or without `m=1`) reports
   "Congratulations! Netlists match". `XQa0.runset-extracted.cir` is that
   run's extracted-netlist output, committed here as the terminals/
   parameters evidence.
2. **PDK's own testcase through klt**: `klt lvs --engine klayout-runset`
   on the PDK's `bjt_devices` testcase pair (their GDS + their CDL, 3x
   `npn13G2`) pairs devices 3/3 and nets 10/10; in its default strict-port
   mode the top-level pins are unmatched (the testcase layout carries no
   pin labels) and the verdict is `mismatch` — the PDK's own regression
   runs the same pair with `--ignore_top_ports_mismatch`, and with that
   switch the runner prints "Netlists match". klt exposes it as
   `deck_vars.ignore_top_ports_mismatch` (used in the committed placed
   request); klt's own `pin.unmatched` findings for the unlabelled cell
   remain visible either way, as they should.
3. **Freshness**: `klt lvs --check` / `klt extract --check` on all six
   committed reports exits 0 (input sha256 re-verified: placed
   `1e581b2a…e19be`, bare `97b08aa5…35d22`, runset `e01bcb1e…bbbd7`).

## Consequences written back

- **#128** (item 4 analog): the `klayout-runset` engine is the path — the
  curated deck has no HBT entry (its documented gap; rows 1, 2, 5, 6), the
  runset recognises `npn13G2` with C/B/E/S and `we/le/Nx/m` and pairs it.
  Posted to #128 in a comment.
- **`2AMLogic/klayout-tools#4397`**: rows 3 (bare, that issue's own
  request) and 4 answer its acceptance run; posted there.
- No new upstream gap filed: recognition is complete on the runset path
  (substrate terminal and parameters included). The curated-deck HBT gap
  is already documented in klt's own `docs/cli/extract.md` ("no curated
  bipolar (HBT) entries yet"), and the Q-card dialect requirement is the
  PDK runset's own documented testcase form, not a klt defect.
