# record-dir double reservation — investigation record (issue #220)

Append-only evidence for the root-causing of the double record reservation
two CI runs showed during PR #216's review. The reservation contract itself is
documented in `record-dir.sh`; this file records why the contract could be
violated on hosted runners and nowhere else.

## Observed (from issue #220)

- Run [44910517015](https://github.com/2AMLogic/sg13g2-serdes/actions/runs/44910517015)
  (head `fcea669`): `tx-mos` — 2 `klt sim` calls, 1 expected.
- Run [44935369166](https://github.com/2AMLogic/sg13g2-serdes/actions/runs/44935369166)
  (head `d436b53`): `rx` — 8 `klt sim` calls, 4 expected; both concurrent
  launches reserved and wrote the same record id.
- Never reproduced on the 8-vCPU dispatch hosts (GNU coreutils), across all
  local repeats recorded in PR #216.

## Live runs (this investigation)

Both via workflow_dispatch of the CI workflow on `feature/issue-220`, which
carried the temporary dispatch-gated probe job (reverted in the final PR; the
standalone probe that followed it, `record-dir-race-probe.sh` and
`.github/workflows/record-dir-race-probe.yml`, was removed on 2026-11-23 once
this investigation concluded -- operator ruling on #234 -- and is retrievable
from history at `42fd372`, the revision that produced every measurement below;
see "Reproducing"):

- Run [44969040860](https://github.com/2AMLogic/sg13g2-serdes/actions/runs/44969040860)
  (branch @ `de832e9`) — first reproduction, instrument commit.
- Run [44969548534](https://github.com/2AMLogic/sg13g2-serdes/actions/runs/44969548534)
  (branch @ `42fd372`) — full evidence set incl. the `os.mkdir` control.

Pinned revisions under test (per the issue): `d436b53` (pre-guard, the
revision the RX failure ran) and `4367f60` (guarded, PR #216 head).

## Runner environment (both runs)

- `ubuntu-latest`, kernel `Linux 7.0.0-1020-azure`, **nproc = 4** (the issue's
  "2-core" premise: the dispatched runners of these runs report 4 vCPU; the
  race reproduces regardless).
- `/tmp` and workspace: `ext4 rw,relatime,discard,journal_async_commit,nobarrier,...`
  — a plain ext4, **not** overlayfs and not tmpfs.
- `mkdir --version`: **`mkdir (uutils coreutils) 0.10.0`**;
  `/usr/bin/mkdir` resolves to `/usr/lib/cargo/bin/coreutils/mkdir` — the
  runner image's coreutils is the Rust rewrite, not GNU. The dispatch hosts
  (where nothing reproduced) run GNU coreutils 9.4.

## Root cause: uutils coreutils 0.10.0 `mkdir` reports success for a lost
## creation race

`uutils/coreutils` tag `0.10.0`, `src/uu/mkdir/src/mkdir.rs`, abridged:

```rust
fn create_dir(path: &Path, is_parent: bool, config: &Config) -> UResult<()> {
    let path_exists = path.exists();          // (1) pre-stat gate
    if path_exists && !config.recursive {
        return Err(USimpleError::new(1, ...));   // "File exists" -- correct,
    }                                            // but only if the loser
    ...                                          // starts AFTER the winner
    create_single_dir(path, is_parent, config)
}

fn create_single_dir(...) -> UResult<()> {
    match create_dir_with_mode(path, mkdir_mode, shaped_umask) {
        Ok(()) => ... Ok(()),
        Err(_) if path.is_dir() => {          // (2) EEXIST rescue
            ...
            Ok(())                             // <-- plain `mkdir x` exits 0
        }                                      //     when x exists and the
        Err(e) => Err(e.into()),               //     syscall lost a race
    }
}
```

GNU `mkdir` reports an error for `mkdir existing` in every path. uutils 0.10.0
returns **success** whenever the underlying `mkdir(2)` fails but the path is
now a directory: a launcher whose exclusive `mkdir` lost a true-concurrent
race still exits 0, so `reserve_record_dir`'s `if ! mkdir -- "${out}"` sees
success and prints the path — both launches "own" the record. A loser that
starts after the winner finished is caught by the pre-stat (1) and errors
correctly, which is why the anomaly needs concurrent in-flight `mkdir`s and
stayed invisible to serialized local repeats.

## Measurements (all from the linked runs; zero counts included)

Raw `mkdir`-pair micro-benchmark, 1000 rounds per line, both racers target the
same fresh path; "both-succeeded" = both processes exited 0:

| run | parent | impl | pinned | both-succeeded |
|---|---|---|---|---|
| 44969040860 | /tmp | uutils mkdir | no | 44 |
| 44969040860 | /tmp | uutils mkdir | `taskset -c 0` | 0 |
| 44969040860 | workspace | uutils mkdir | no | 51 |
| 44969040860 | workspace | uutils mkdir | `taskset -c 0` | 0 |
| 44969548534 | /tmp | uutils mkdir | no | 18 |
| 44969548534 | /tmp | uutils mkdir | `taskset -c 0` | 16 |
| 44969548534 | workspace | uutils mkdir | no | 17 |
| 44969548534 | workspace | uutils mkdir | `taskset -c 0` | 26 |
| 44969548534 | /tmp | python `os.mkdir` (bare `mkdir(2)`) | no | **0** |
| 44969548534 | /tmp | python `os.mkdir` | `taskset -c 0` | **0** |
| 44969548534 | workspace | python `os.mkdir` | no | **0** |
| 44969548534 | workspace | python `os.mkdir` | `taskset -c 0` | **0** |

Full runner race (`record-dir-race-probe.sh race` -- the probe script as of
`42fd372`, since removed; 150 concurrent pairs per case, fixed clock, mock
`klt`, per-launcher logs):

| revision | case | doubles (both reserved) | mkdir refusals | `.reserved` refusals | loser exit 3 |
|---|---|---|---|---|---|
| `d436b53` pre-guard | rx | 59 | 91 | 0 | 91 |
| `d436b53` pre-guard | smoke | 63 | 87 | 0 | 87 |
| `d436b53` pre-guard | tx-hbt | 62 | 88 | 0 | 88 |
| `d436b53` pre-guard | tx-mos | 73 | 77 | 0 | 77 |
| `4367f60` guarded | rx | **0** | 98 | 52 | 150 |
| `4367f60` guarded | smoke | **0** | 99 | 51 | 150 |
| `4367f60` guarded | tx-hbt | **0** | 86 | 64 | 150 |
| `4367f60` guarded | tx-mos | **0** | 92 | 58 | 150 |

Every pre-guard double had both launchers reach the mock (klt-sims
4+4 / 3+3 / 1+1 / 1+1), both write `record.md`, and `exit-codes.txt` doubled —
the exact signature of the RX failure log. On the guarded revision the
`.reserved` refusals (52/51/64/58 of 150) match the pre-guard double counts:
the second, independent O_EXCL claim catches exactly the launches whose
`mkdir` was falsely reported successful, and the refused launcher exits 3
having made zero `klt sim` calls — 150 of 150 attempts per case.

Full-contract spot checks on the runner: run 44969040860 pre-guard failed at
`smoke` (6 calls vs 3) with the PR #216 diagnostics dumping the doubled
record; run 44969548534 pre-guard failed at `tx-mos` (2 calls vs 1) and
passed rx/smoke/tx-hbt; the guarded revision passed all four cases in run
44969548534, and the branch's extended-dump `test-record-dir.sh` passed the
`check` job's harness step in the same run. The race is intermittent per
attempt (roughly 40-49 % of concurrent pairs on this image) — single-shot
passes prove nothing, which is why the original reds looked irreproducible.

## Verdict on the three proposed mechanisms

1. **Overlayfs / `/tmp` non-atomic `mkdir` — refuted.** The fixture
   filesystem is plain ext4, and the bare-syscall control (python `os.mkdir`,
   same paths, same concurrency) measured 0 double-successes in 4000 pairs.
   The kernel's `mkdir(2)` is atomic here; the double success is produced in
   userspace, by `mkdir(1)`.
2. **The fixture shadowing or short-circuiting the loser's `mkdir` — refuted
   as filed, and the check found the real cause.** Inside the fixture `PATH`
   (`$TMP/bin` = `date`, `klt` only) `mkdir` resolves to `/usr/bin/mkdir`,
   unshadowed; the resolution line is what exposed that this image's
   `/usr/bin/mkdir` is uutils coreutils 0.10.0, whose EEXIST rescue is the
   root cause above. The harness shadowed nothing — the binary itself lies.
3. **A refused caller reaching `klt sim` despite a non-zero return —
   refuted.** All three call sites guard the reservation
   (`sim/rx/run_sizing.sh:22`, `sim/tx/run_sizing.sh:27`,
   `sim/smoke/run_smoke.sh:22`: `OUT="$(reserve_record_dir ...)" || exit 3`),
   and in 600 pre-guard + 600 guarded measured pairs the refused launcher
   exited 3 with an empty per-launcher `klt` log every time. The observed
   doubles were not ignored refusals — both reservations genuinely
   "succeeded".

## Consequences

- The PR #216 guard (`.reserved`, created with noclobber `>` — an
  `open(O_CREAT|O_EXCL)` in bash itself, not `mkdir(1)`) is unaffected by the
  uutils bug and converted every measured would-be double into a clean
  exit-3 refusal: 0 doubles in 600 guarded pairs with 225 second-claim
  refusals recorded. The two-claim contract in `record-dir.sh` stands.
- The anomaly is image-dependent: any runner whose `mkdir` is uutils
  coreutils 0.10.0 can produce it; hosts with GNU coreutils cannot (the
  pre-stat rescue divergence does not exist there). CI reds of this shape on
  hosted runners are explained without any repo-side defect.
- Residual, unresolved here: whether upstream uutils later removes the
  plain-`mkdir` EEXIST rescue (it diverges from GNU) — out of scope for this
  repo (issue #220: no new locking schemes without evidence); the guard makes
  the answer immaterial to this contract. The exact per-run rate of the two
  original reds is unknowable post hoc, but the measured ~40-49 % per-pair
  rate on this image is consistent with reds appearing as soon as the image
  rolled out and staying rare on the (GNU) hosts used for local repeats.

## Reproducing

2026-11-23: the probe was removed once this investigation concluded (operator
ruling on #234). Nothing in the tree runs it and there is no workflow to
dispatch; it is reproduced from history. `42fd372` is the revision that
produced every measurement above:

    git show 42fd372:sim/tools/record-dir-race-probe.sh
    git show 42fd372:.github/workflows/record-dir-race-probe.yml

The script saw one further change before its removal: #245 (commit `597f1de`)
taught it to classify the post-#244 delegated `record-dir.sh` shape and stage
`scripts/klt-lib.sh` (see the Erratum below). That revision is retrieved the
same way, `git show 597f1de:sim/tools/record-dir-race-probe.sh`; it produced no
measurement recorded here, and the workflow did not change after `42fd372`.

The workflow at `42fd372` is the recipe for the recorded runs. It only runs on a host whose
`mkdir --version` reports uutils coreutils (see "Runner environment" above; a
GNU host does not reproduce): add the two pinned revisions as worktrees,
`d436b53` (pre-guard) and `4367f60` (guarded), then run the script's modes
`env <pinned-repo>`, `micro <parent-dir> <rounds> [pin|python|pin-python]`
and `race <pinned-repo> <rx|smoke|tx-hbt|tx-mos> <attempts>` with the bounds
the linked runs used (`attempts=150`, `micro_rounds=1000`). The
linked runs above used the same probe script through a temporary
dispatch-gated job in `ci.yml` (branch commits `de832e9`/`42fd372`), removed
again in the final PR. Anomaly dumps (record dir with hidden entries,
`.reserved` pid, both launchers' outputs, per-launcher `klt` logs, `mkdir`
resolution) print into the job log; artifacts stay under the printed
per-invocation directory for the runner's lifetime.

## Erratum (2026-11-23)

The consequence above -- "the two-claim contract in `record-dir.sh` stands" --
described the revision this record was written against. Issue #244
consolidated the reservation onto the single `os.mkdir` primitive in
`scripts/klt-lib.sh`: `sim/tools/record-dir.sh` now builds the `<ts>-<sha>`
record id and delegates the exclusive creation to `reserve_record_dir`, and
the second `.reserved` claim was retired with the `mkdir(1)` call it guarded.
This record's own control measurements are the justification -- bare
`os.mkdir` measured 0 double-successes in 4000 pairs on the affected image
(the marker existed to catch exactly the uutils `mkdir` false success that
reading the `mkdir(2)` result directly cannot produce), so the second claim
added no exclusivity on top of the primitive. The pinned-revision probe
(`.github/workflows/record-dir-race-probe.yml`) still measures the pre-guard and
two-claim revisions exactly as they were; nothing in this record's measurements or
verdict changes.
The probe script itself (`sim/tools/record-dir-race-probe.sh race`) was also
updated in this PR to measure all three shapes: it stages `scripts/klt-lib.sh` when
the pinned revision has it, reports `guarded=yes` only for the `.reserved` two-claim revision (`guarded=no` for the pre-guard and delegated ones), and
counts the `record-dir: ... exists (records are append-only)` refusal under
`mkdir-refusals`; it refuses a delegated pin whose `klt-lib.sh` is missing
rather than printing a summary.

## Removal (2026-11-23)

Per the operator ruling on #234 the probe the Erratum above describes -- the
script and its `workflow_dispatch` workflow -- was removed once this
investigation concluded; the Erratum's present-tense description of it refers
to the pre-removal tree. Nothing in the tree runs it. Reproduction from
history, and the revisions to retrieve, are given under "Reproducing" above.
No finding, table or measurement in this record is changed by the removal.
