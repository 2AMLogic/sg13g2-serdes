#!/usr/bin/env bash
# record-dir-race-probe.sh -- measure the record-dir race a CI runner showed (issue #220).
#
# Not a gate: a manual instrument (run by .github/workflows/record-dir-race-probe.yml,
# workflow_dispatch only) that repeats the test-record-dir.sh race under a fixed
# clock and counts, per case, how often two concurrent launches BOTH reserve the
# same record id -- the anomaly runs 44910517015 and 44935369166 logged -- plus
# the evidence needed to separate the three candidate mechanisms:
#   (a) filesystem: `micro` races two bare `mkdir`s of one path, so no runner
#       code is involved; `env` records the fixture filesystem type;
#   (b) harness shadowing: every `race` run prints the mkdir resolution and the
#       shim directory contents inside the fixture PATH;
#   (c) a refused caller still reaching klt: every attempt records both
#       launchers' exit codes and per-launcher klt logs (loser must exit 3
#       having made zero klt sim calls).
# The fixture recipe is test-record-dir.sh's, but every copied file comes from
# the pinned revision under test, so a run measures that revision as-is.
#   record-dir-race-probe.sh env    <pinned-repo>
#   record-dir-race-probe.sh micro  <parent-dir> <rounds> [pin]   # pin = taskset -c 0
#   record-dir-race-probe.sh race   <pinned-repo> <rx|smoke|tx-hbt|tx-mos> <attempts>
# Artifacts (kept, never deleted): one directory per invocation, path printed.
set -u

FIXED_TS=20380119-031408

die() { echo "record-dir-race-probe: $*" >&2; exit 2; }
keep_dir() { echo "record-dir-race-probe: artifacts kept in $1"; }

# --- fixture: test-record-dir.sh's disposable repo, files from $1 ------------
make_fixture() { # make_fixture <pinned-repo-root> <tmp-root>
  local pin="$1" tmp="$2"
  mkdir -p "$tmp/repo/sim/tools" "$tmp/repo/sim/rx/tools" "$tmp/repo/sim/tx" \
           "$tmp/repo/sim/smoke" "$tmp/repo/design" "$tmp/repo/layout" "$tmp/bin"
  cp "$pin/sim/tools/record-dir.sh" "$pin/sim/tools/record_common.py" \
     "$pin/sim/tools/build-osdi.sh" "$tmp/repo/sim/tools/"
  cp "$pin/sim/pdk.json" "$tmp/repo/sim/"
  cp "$pin/layout/toolchain.json" "$tmp/repo/layout/"
  cp "$pin/design/check-netlists.sh" "$tmp/repo/design/"
  cp "$pin/sim/rx/run_sizing.sh" "$tmp/repo/sim/rx/"
  cp "$pin/sim/rx/tools/make_record.py" "$tmp/repo/sim/rx/tools/"
  cp "$pin"/sim/rx/*.request.json "$tmp/repo/sim/rx/"
  cp "$pin/sim/tx/run_sizing.sh" "$tmp/repo/sim/tx/"
  cp "$pin/sim/tx/make_record.py" "$pin/sim/tx/make_record_mos.py" "$tmp/repo/sim/tx/"
  cp "$pin/sim/tx/tx_sizing_ffe0_typ.request.json" \
     "$pin/sim/tx/tx_mos_ffe_en.request.json" "$tmp/repo/sim/tx/"
  cp "$pin/sim/smoke/run_smoke.sh" "$pin/sim/smoke/make_record.py" "$tmp/repo/sim/smoke/"
  cp "$pin"/sim/smoke/*.request.json "$tmp/repo/sim/smoke/"
  printf '#!/usr/bin/env bash\necho %s\n' "$FIXED_TS" > "$tmp/bin/date"
  cat > "$tmp/bin/klt" <<'EOF'
#!/usr/bin/env bash
echo "klt $*" >> "${KLT_LOG:?mock klt: KLT_LOG unset}"
[ "${1:-}" = sim ] || exit 0
echo "mock klt sim failure sentinel stderr pid=$$" >&2
exit 1
EOF
  chmod +x "$tmp/bin/date" "$tmp/bin/klt"
  git -C "$tmp/repo" init -q
  git -C "$tmp/repo" add -A
  git -C "$tmp/repo" -c user.name=probe -c user.email=probe@example.com \
    -c commit.gpgsign=false commit -qm fixture || die "fixture commit failed"
}

mode="${1:-}"; [ -n "$mode" ] || die "usage: env|micro|race (see header)"

case "$mode" in

env)
  [ $# -ge 2 ] || die "env <pinned-repo>"
  pin="$(cd "$2" && pwd)" || die "cannot enter $2"
  echo "env: uname=$(uname -sr) nproc=$(nproc)"
  echo "env: pinned-repo sha=$(git -C "$pin" rev-parse --short HEAD) ($(git -C "$pin" rev-parse HEAD))"
  mkdir --version | head -1 | sed 's/^/env: /'
  echo "env: mkdir resolution on this PATH: $(type -a mkdir 2>&1 | tr '\n' ' ')"
  for p in "${TMPDIR:-/tmp}" /tmp "$pin"; do
    echo "env: path=$p fstype=$(stat -f -c %T "$p" 2>&1) mount=$(findmnt -n -T "$p" -o FSTYPE,OPTIONS 2>&1 | head -1)"
  done
  ;;

micro)
  [ $# -ge 3 ] || die "micro <parent-dir> <rounds> [pin]"
  parent="$2"; rounds="$3"; pin="${4:-}"
  [ -d "$parent" ] || die "$parent is not a directory"
  [ "$rounds" -gt 0 ] || die "rounds must be positive"
  mkdir_bin="$(command -v mkdir)" || die "no mkdir on PATH"
  base="$(mktemp -d "$parent/probe-micro.XXXXXX")" || die "mktemp -d under $parent failed"
  both=0
  run_one() { # run_one <target> -- one side of a concurrent mkdir pair
    if [ -n "$pin" ] && command -v taskset >/dev/null 2>&1; then
      taskset -c 0 mkdir -- "$1" 2>/dev/null
    else
      mkdir -- "$1" 2>/dev/null
    fi
  }
  i=0
  while [ "$i" -lt "$rounds" ]; do
    i=$((i + 1))
    t="$base/r$i"; mkdir -- "$t" || die "cannot mkdir round dir"
    run_one "$t/x" && : > "$t/a" &
    run_one "$t/x" && : > "$t/b" &
    wait
    if [ -f "$t/a" ] && [ -f "$t/b" ]; then
      both=$((both + 1))    # both mkdirs reported success: the anomaly
    else
      rm -rf -- "$t"
    fi
  done
  echo "probe micro: parent=$parent fstype=$(stat -f -c %T "$parent") rounds=$rounds" \
       "pin=${pin:+taskset-c0}mkdir=$(readlink -f "$mkdir_bin") both-succeeded=$both"
  keep_dir "$base"
  ;;

race)
  [ $# -ge 4 ] || die "race <pinned-repo> <rx|smoke|tx-hbt|tx-mos> <attempts>"
  pin="$(cd "$2" && pwd)" || die "cannot enter $2"
  case="$3"; attempts="$4"
  [ "$attempts" -gt 0 ] || die "attempts must be positive"
  case "$case" in
    rx)     script=sim/rx/run_sizing.sh   arg=""   suffix=""   sims=4 ;;
    smoke)  script=sim/smoke/run_smoke.sh arg=""   suffix=""   sims=3 ;;
    tx-hbt) script=sim/tx/run_sizing.sh   arg=""   suffix=""   sims=1 ;;
    tx-mos) script=sim/tx/run_sizing.sh   arg=mos suffix="-mos" sims=1 ;;
    *) die "unknown case $case (rx|smoke|tx-hbt|tx-mos)" ;;
  esac
  if grep -q '\.reserved' "$pin/sim/tools/record-dir.sh"; then guarded=yes; else guarded=no; fi
  sha8="$(git -C "$pin" rev-parse --short HEAD)"
  tmp="$(mktemp -d)" || die "mktemp -d failed"
  make_fixture "$pin" "$tmp"
  # the runner names the record after the FIXTURE repo's HEAD, not the pinned one
  fsha="$(git -C "$tmp/repo" rev-parse --short HEAD)"
  export PATH="$tmp/bin:$PATH" PDK_ROOT="$tmp/pdk-root"
  mkdir -p "$PDK_ROOT"
  dir="$tmp/repo/$(dirname "$script")/records"
  rec="$dir/${FIXED_TS}-${fsha}${suffix}"
  cmd=(bash "$tmp/repo/$script"); [ -n "$arg" ] && cmd+=("$arg")
  sim_calls() { grep -c '^klt sim ' "$1" 2>/dev/null || true; }

  doubles=0 mismatch=0 mkdir_refusals=0 reserved_refusals=0 loser_exit3=0
  reserved_refusals_while_clean=0 anomalies=0
  i=0
  while [ "$i" -lt "$attempts" ]; do
    i=$((i + 1))
    rm -rf "$dir"; mkdir -p "$dir"
    la="$tmp/klt.a.log"; lb="$tmp/klt.b.log"; : > "$la"; : > "$lb"
    out="$tmp/out"; err="$tmp/err"
    KLT_LOG="$la" "${cmd[@]}" >"$out.a" 2>"$err.a" &
    pa=$!
    KLT_LOG="$lb" "${cmd[@]}" >"$out.b" 2>"$err.b" &
    pb=$!
    wait "$pa"; sa=$?
    wait "$pb"; sb=$?
    na="$(sim_calls "$la")"; nb="$(sim_calls "$lb")"

    this_double=0 this_reserved=0 this_mkdir=0
    if [ "$na" -gt 0 ] && [ "$nb" -gt 0 ]; then this_double=1; fi
    if grep -q "already claimed by another launch" "$err.a" "$err.b" 2>/dev/null; then
      this_reserved=1
    fi
    if grep -q "already exists -- a same-second launch" "$err.a" "$err.b" 2>/dev/null; then
      this_mkdir=1
    fi
    # the refused launcher (zero klt sim calls) must have exited 3
    loser_ok=0
    if [ "$na" -eq 0 ] && [ "$nb" -gt 0 ] && [ "$sa" -eq 3 ]; then loser_ok=1; fi
    if [ "$nb" -eq 0 ] && [ "$na" -gt 0 ] && [ "$sb" -eq 3 ]; then loser_ok=1; fi

    [ "$this_double" -eq 1 ] && doubles=$((doubles + 1))
    [ "$((na + nb))" -ne "$sims" ] && mismatch=$((mismatch + 1))
    [ "$this_mkdir" -eq 1 ] && mkdir_refusals=$((mkdir_refusals + 1))
    [ "$this_reserved" -eq 1 ] && reserved_refusals=$((reserved_refusals + 1))
    [ "$this_reserved" -eq 1 ] && [ "$this_double" -eq 0 ] && [ "$((na + nb))" -eq "$sims" ] \
      && reserved_refusals_while_clean=$((reserved_refusals_while_clean + 1))
    [ "$loser_ok" -eq 1 ] && loser_exit3=$((loser_exit3 + 1))

    if [ "$this_double" -eq 1 ] || [ "$loser_ok" -eq 0 ] || [ "$((na + nb))" -ne "$sims" ]; then
      anomalies=$((anomalies + 1))
      {
        echo "--- anomaly: case=$case attempt=$i/$attempts pids a=$pa exit=$sa b=$pb exit=$sb klt-sims a=$na b=$nb"
        echo "--- ls -la $dir:"; ls -la "$dir"
        echo "--- ls -la $rec:"; ls -la "$rec" 2>&1
        if [ -e "$rec/.reserved" ]; then
          echo "--- .reserved marker pid: $(cat "$rec/.reserved")"
        else
          echo "--- .reserved marker: absent"
        fi
        echo "--- mkdir resolution in fixture PATH: $(type -a mkdir 2>&1 | tr '\n' ' ')"
        echo "--- shim dir: $(find "$tmp/bin" -maxdepth 1 -type f -printf '%f ' 2>/dev/null)"
        for p in a b; do
          echo "--- launch $p stdout:"; cat "$out.$p"
          echo "--- launch $p stderr:"; cat "$err.$p"
          echo "--- launch $p klt log:"; cat "$tmp/klt.$p.log"
        done
        echo "--- exit-codes files:"; find "$dir" -name exit-codes.txt -print -exec cat {} \;
      }
    fi
  done
  echo "probe race: case=$case pin=$sha8 guarded=$guarded fstype=$(stat -f -c %T "$tmp")" \
       "attempts=$attempts sims-per-launch=$sims doubles=$doubles total-sims-mismatch=$mismatch" \
       "mkdir-refusals=$mkdir_refusals reserved-refusals=$reserved_refusals" \
       "reserved-refusals-while-clean=$reserved_refusals_while_clean loser-exit3=$loser_exit3" \
       "anomalies=$anomalies"
  keep_dir "$tmp"
  ;;

*) die "unknown mode $mode (env|micro|race)" ;;
esac
