#!/usr/bin/env bash
# test-record-dir.sh -- prove the record-directory reservation contract (issue #202).
#
# Runs sim/{rx,tx,smoke} in a disposable git repo with a fixed clock (a PATH
# `date` shim printing one timestamp, so every launch names the same record)
# and a mock `klt` that logs each invocation, writes pid-tagged sentinel stderr
# and exits 1 for `sim` subcommands (exit 0 otherwise, so the netlist
# preflight passes). Per runner (rx, smoke, tx hbt, tx mos) it checks:
#   naming: the first launch reserves records/<ts>-<short-SHA>[-mos] and saves
#           the failed run's stderr and exit log there;
#   retry:  a same-second relaunch exits nonzero before invoking klt and
#           changes no byte of the saved record (append-only holds);
#   race:   two concurrent launches on a fresh id -- only one reaches `klt sim`.
# No PDK, no batch fleet: bash, git and python3 only. Exit 0 = all checks hold.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "${HERE}/../.." && pwd)"
FIXED_TS=20380119-031408
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() {
  echo "test-record-dir: FAIL: $*" >&2
  echo "  artifacts kept under $TMP" >&2
  trap - EXIT
  exit 1
}

# --- disposable repo: the runners, their inputs, and nothing else ----------
mkdir -p "$TMP/repo/sim/tools" "$TMP/repo/sim/rx/tools" "$TMP/repo/sim/tx" \
         "$TMP/repo/sim/smoke" "$TMP/repo/design" "$TMP/repo/layout" "$TMP/bin"
cp "$REPO/sim/tools/record-dir.sh" "$REPO/sim/tools/record_common.py" \
   "$REPO/sim/tools/build-osdi.sh" "$TMP/repo/sim/tools/"
cp "$REPO/sim/pdk.json" "$TMP/repo/sim/"
cp "$REPO/layout/toolchain.json" "$TMP/repo/layout/"
# no design/*/*.sch: check-netlists.sh (the rx preflight) is a no-op exit 0
cp "$REPO/design/check-netlists.sh" "$TMP/repo/design/"
cp "$REPO/sim/rx/run_sizing.sh" "$TMP/repo/sim/rx/"
cp "$REPO/sim/rx/tools/make_record.py" "$TMP/repo/sim/rx/tools/"
cp "$REPO"/sim/rx/*.request.json "$TMP/repo/sim/rx/"
cp "$REPO/sim/tx/run_sizing.sh" "$TMP/repo/sim/tx/"
cp "$REPO/sim/tx/make_record.py" "$REPO/sim/tx/make_record_mos.py" "$TMP/repo/sim/tx/"
cp "$REPO/sim/tx/tx_sizing_ffe0_typ.request.json" \
   "$REPO/sim/tx/tx_mos_ffe_en.request.json" "$TMP/repo/sim/tx/"
cp "$REPO/sim/smoke/run_smoke.sh" "$REPO/sim/smoke/make_record.py" "$TMP/repo/sim/smoke/"
cp "$REPO"/sim/smoke/*.request.json "$TMP/repo/sim/smoke/"

# fixed clock: every `date` the runners run prints FIXED_TS
printf '#!/usr/bin/env bash\necho %s\n' "$FIXED_TS" > "$TMP/bin/date"
# mock klt: log the argv; `sim` writes pid-tagged sentinel stderr (so an
# overwrite by a relaunch is visible in the record tree hash) and exits 1
cat > "$TMP/bin/klt" <<'EOF'
#!/usr/bin/env bash
echo "klt $*" >> "${KLT_LOG:?mock klt: KLT_LOG unset}"
[ "${1:-}" = sim ] || exit 0
echo "mock klt sim failure sentinel stderr pid=$$" >&2
exit 1
EOF
chmod +x "$TMP/bin/date" "$TMP/bin/klt"
export PATH="$TMP/bin:$PATH" KLT_LOG="$TMP/klt.log" PDK_ROOT="$TMP/pdk-root"
mkdir -p "$PDK_ROOT"
: > "$KLT_LOG"

git -C "$TMP/repo" init -q
git -C "$TMP/repo" add -A
git -C "$TMP/repo" -c user.name=test -c user.email=test@example.com \
  -c commit.gpgsign=false commit -qm fixture || fail "fixture commit failed"
SHA="$(git -C "$TMP/repo" rev-parse --short HEAD)"

sim_calls() { grep -c '^klt sim ' "$KLT_LOG"; }
tree_hash() { ( cd "$1" && find . -type f -print0 | sort -z | xargs -0r sha256sum | sha256sum ); }

check_runner() { # check_runner <name> <script> [set-arg] [id-suffix] [sim-calls-per-launch]
  local name="$1" script="$2" arg="${3:-}" suffix="${4:-}" sims="${5:-}"
  local dir rec out err h0 nerr bad e pa pb sa sb
  local cmd=(bash "$TMP/repo/$script")
  [ -n "$arg" ] && cmd+=("$arg")
  dir="$TMP/repo/$(dirname "$script")/records"
  rec="$dir/${FIXED_TS}-${SHA}${suffix}"
  out="$TMP/${name}.out"; err="$TMP/${name}.err"

  # naming + evidence saved: the record is named as ever, holding the failed
  # run's stderr and exit log (tx hbt and tx mos share this records root, so
  # the sibling set's same-second record may sit beside it)
  : > "$KLT_LOG"
  "${cmd[@]}" >"$out" 2>"$err"
  [ -d "$rec" ] || fail "$name: first launch reserved no record at $rec"
  bad=""
  shopt -s nullglob
  for e in "$dir"/* "$dir"/.[!.]* "$dir"/..?*; do
    case "${e##*/}" in
      "${FIXED_TS}-${SHA}"|"${FIXED_TS}-${SHA}-mos") ;;
      *) bad="${bad:+$bad }${e##*/}" ;;
    esac
  done
  shopt -u nullglob
  [ -z "$bad" ] || fail "$name: records/ holds unexpected entries: $bad"
  [ "$(sim_calls)" -eq "$sims" ] \
    || fail "$name: first launch made $(sim_calls) klt sim calls, expected $sims"
  nerr="$(find "$rec" -name '*.stderr.txt' | wc -l)"
  [ "$nerr" -eq "$sims" ] || fail "$name: record holds $nerr stderr files, expected $sims"
  grep -rq "sentinel stderr" "$rec" || fail "$name: sentinel stderr not saved in the record"

  # same-second relaunch: refuse nonzero, invoke no klt, change no byte
  h0="$(tree_hash "$rec")"
  : > "$KLT_LOG"
  if "${cmd[@]}" >"$out" 2>"$err"; then
    fail "$name: same-second relaunch exited 0"
  fi
  if [ -s "$KLT_LOG" ]; then
    fail "$name: same-second relaunch invoked klt before refusing: $(cat "$KLT_LOG")"
  fi
  [ "$(tree_hash "$rec")" = "$h0" ] \
    || fail "$name: same-second relaunch changed the saved record $rec"
  grep -q "record-dir:" "$err" \
    || fail "$name: same-second relaunch did not report the reservation refusal"

  # concurrent launches on a fresh id: exactly one reaches klt sim
  rm -rf "$dir"; mkdir -p "$dir"
  : > "$KLT_LOG"
  "${cmd[@]}" >"$out.a" 2>"$err.a" &
  pa=$!
  "${cmd[@]}" >"$out.b" 2>"$err.b" &
  pb=$!
  wait "$pa"; sa=$?
  wait "$pb"; sb=$?
  [ -d "$rec" ] || fail "$name: concurrent launches reserved no record"
  if [ "$(sim_calls)" -ne "$sims" ]; then
    # artifacts die with the CI runner, so make the red self-explaining
    {
      echo "--- race diagnostics: $name (a/b = the two concurrent launches)"
      echo "--- launch pids/exits: a=$pa exit=$sa  b=$pb exit=$sb (loser must exit 3)"
      echo "--- klt log:"; cat "$KLT_LOG"
      echo "--- ls -la $dir:"; ls -la "$dir"
      echo "--- ls -la $rec (record dir, hidden entries included):"
      ls -la "$rec"
      if [ -e "$rec/.reserved" ]; then
        echo "--- .reserved marker pid: $(cat "$rec/.reserved") (equals launch a or b pid above on the guarded revision)"
      else
        echo "--- .reserved marker: absent (pre-guard revision, or neither claim reached the marker)"
      fi
      echo "--- mkdir resolution in this PATH: $(type -a mkdir 2>&1 | tr '\n' ' ')"
      echo "--- fixture fs: $(stat -f -c %T "$TMP" 2>&1)"
      echo "--- exit-codes files:"; find "$dir" -name exit-codes.txt -print -exec cat {} \;
      for p in a b; do
        echo "--- launch $p stdout:"; cat "$out.$p"
        echo "--- launch $p stderr:"; cat "$err.$p"
      done
      echo "--- HEAD short sha now: $(git -C "$TMP/repo" rev-parse --short HEAD 2>&1) (fixture: $SHA)"
    } >&2
    fail "$name: concurrent launches made $(sim_calls) klt sim calls, expected exactly $sims (one launcher)"
  fi
  echo "test-record-dir: PASS: $name (naming, retry refused untouched, race: one launcher)"
}

check_runner rx      sim/rx/run_sizing.sh   ""   ""     4
check_runner smoke   sim/smoke/run_smoke.sh ""   ""     3
check_runner tx-hbt  sim/tx/run_sizing.sh   ""   ""     1
check_runner tx-mos  sim/tx/run_sizing.sh   mos  "-mos" 1
echo "test-record-dir: all runners hold the reservation contract"
