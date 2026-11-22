#!/usr/bin/env bash
# test-reserve-record-dir.sh -- prove the record-directory reservation contract
# of the three digital layout writers (issue #219; the pnr/lvs half landed in
# #208, the erc half is the bug this closes): every record write goes through
# the exclusive reservation in scripts/klt-lib.sh, so a duplicate or racing
# launch cannot touch a saved record.
#
# Script layer, per writer (pnr-regen.sh, lvs-regen.sh, erc-regen.sh), in a
# disposable git repo with a fixed clock (a PATH `date` shim prints one UTC
# day, so every launch names the same record) and a mocked `uvx` standing in
# for klt (no EDA tool, no network, no PDK install):
#   naming: the first launch reserves <records-root>/<date>-<short-sha> and
#           writes its complete record there;
#   retry:  a relaunch against the saved record exits 1 with the script's own
#           diagnostic and changes no byte of it (append-only holds);
#   race:   two concurrent launches -- exactly one reserves the record and,
#           for lvs/erc (whose reservation precedes the tool run), exactly one
#           reaches the tool at all. pnr-regen.sh runs its tool before the
#           reservation, so both launches are expected to reach it; a start
#   barrier keeps the race at the reservation, never in the shared .klt tree.
# Function layer, on scripts/klt-lib.sh sourced directly:
#   creation under a missing parent succeeds; a non-directory parent and a
#   dangling symlink at the destination each refuse with a diagnostic; the
#   occupied-destination refusal keeps a sentinel intact; two concurrent
#   reservations of one destination admit exactly one writer.
# Requires bash, git, jq and python3. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
FIXED_DATE=2038-01-19
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() {
  echo "test-reserve-record-dir: FAIL: $*" >&2
  echo "  artifacts kept under $TMP" >&2
  trap - EXIT
  exit 1
}
tree_hash() { ( cd "$1" && find . -type f -print0 | sort -z | xargs -0r sha256sum | sha256sum ); }

# --- disposable repo: the three writers, their libs and inputs, nothing else
mkdir -p "$TMP/repo/scripts" "$TMP/repo/layout/digital" "$TMP/repo/layout/erc" \
         "$TMP/bin" "$TMP/pdk/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef"
cp "$SRC/scripts/klt-lib.sh" "$SRC/scripts/pnr-lib.sh" \
   "$SRC/scripts/pnr-regen.sh" "$SRC/scripts/lvs-regen.sh" \
   "$SRC/scripts/erc-regen.sh" "$TMP/repo/scripts/"
cp "$SRC/layout/toolchain.json" "$TMP/repo/layout/"
cp "$SRC/layout/digital/place-and-route.request.json" \
   "$SRC/layout/digital/lvs.request.json" "$TMP/repo/layout/digital/"
cp "$SRC/layout/erc/digital.erc.json" "$TMP/repo/layout/erc/"
: > "$TMP/pdk/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef"

# fixed clock: the writers' record-name date is one fixed UTC day; any other
# date call falls through to the real binary
cat > "$TMP/bin/date" <<EOF
#!/usr/bin/env bash
if [ "\$*" = "-u +%Y-%m-%d" ]; then echo "$FIXED_DATE"; else exec /usr/bin/date "\$@"; fi
EOF

# PNR and LVS check for OpenROAD on PATH. Their tool calls go through mock uvx.
cat > "$TMP/bin/openroad" <<'EOF'
#!/bin/sh
echo "test-reserve-record-dir: unexpected direct invocation of openroad" >&2
exit 1
EOF

# mock uvx: klt stand-in. Logs each invocation (argv after the pin args) to
# \$KLT_LOG, then serves the subcommand the writer under test expects. PNR_GATE
# (a directory) turns place-and-route into a two-phase barrier: a call writes
# its build outputs only once PNR_GATE_N calls have STARTED (so every launch's
# earlier \`rm -rf .klt\` has already run) and returns only once PNR_GATE_N
# calls have WRITTEN -- concurrent launches always meet at the reservation.
cat > "$TMP/bin/uvx" <<'EOF'
#!/usr/bin/env bash
shift 4 # --quiet --from <pin> klt
echo "klt $*" >> "${KLT_LOG:?mock uvx: KLT_LOG unset}"
sub="${1:-}"; shift || true
gate_started() { mktemp -d "${PNR_GATE:?}/started.XXXXXX" >/dev/null; }
gate_written() { mktemp -d "${PNR_GATE:?}/written.XXXXXX" >/dev/null; }
gate_wait() { # gate_wait <started|written> -- until PNR_GATE_N markers exist
  local n=0
  while [ "$(ls -d "$PNR_GATE/$1".* 2>/dev/null | wc -l)" -lt "${PNR_GATE_N:?}" ]; do
    n=$((n + 1)); [ "$n" -gt 600 ] && { echo "mock uvx: gate $1 timeout" >&2; exit 9; }
    sleep 0.05
  done
}
case "$sub" in
  erc)
    if [ "${1:-}" = "--validate-spec" ]; then echo '{"status":"ok"}'; exit 0; fi
    echo '{"erc_status":"clean","erc_findings":[],"nets":[{"name":"VDD","matched_islands":1},{"name":"VSS","matched_islands":1}],"erc_coverage":{"checked":[],"skipped":[],"layers_in_stream_without_declaration":[]}}'
    exit 0 ;;
  place-and-route)
    req=""
    for a in "$@"; do case "$a" in *place-and-route.request.json) req="$a";; esac; done
    top="$(jq -r .hdl_toplevel "$req")"
    if [ -n "${PNR_GATE:-}" ]; then gate_started; gate_wait started; fi
    bld="$(dirname "$req")/.klt/place-and-route"
    mkdir -p "$bld"
    printf 'mock gds\n' >"$bld/$top.gds.tmp" && mv "$bld/$top.gds.tmp" "$bld/$top.gds"
    printf 'mock def\n' >"$bld/$top.def.tmp" && mv "$bld/$top.def.tmp" "$bld/$top.def"
    printf 'mock v\n'   >"$bld/$top.v.tmp"   && mv "$bld/$top.v.tmp"   "$bld/$top.v"
    if [ -n "${PNR_GATE:-}" ]; then gate_written; gate_wait written; fi
    echo '{"status":"ok","stage_reached":"route","worst_setup_slack_ns":0.10,"route_drc_violation_count":0,"antenna_violation_count":0}'
    exit 0 ;;
  extract)
    out=""; prev=""
    for a in "$@"; do [ "$prev" = "-o" ] && out="$a"; prev="$a"; done
    printf '* mock extracted layout netlist\n' >"$out"
    echo '{"status":"ok"}'
    exit 0 ;;
  lvs)
    echo '{"status":"match","engine":"netgen","environment":{"engine_version":"1.5.29"},"power_connectivity":{"status":"match"},"mismatch_count":0}'
    exit 0 ;;
  *) echo "mock uvx: unhandled klt subcommand ${sub:-<none>}" >&2; exit 9 ;;
esac
EOF
chmod +x "$TMP/bin/date" "$TMP/bin/openroad" "$TMP/bin/uvx"
export PATH="$TMP/bin:$PATH" KLT_LOG="$TMP/klt.log" PDK_ROOT="$TMP/pdk"
: > "$KLT_LOG"

git -C "$TMP/repo" init -q
git -C "$TMP/repo" add -A
git -C "$TMP/repo" -c user.name=test -c user.email=test@example.com \
  -c commit.gpgsign=false commit -qm fixture || fail "fixture commit failed"
SHA="$(git -C "$TMP/repo" rev-parse --short=7 HEAD)"
TOP="$(jq -r .hdl_toplevel "$TMP/repo/layout/digital/place-and-route.request.json")"

writer() { bash "$TMP/repo/scripts/$1"; }
race_two() { # race_two <script> <out-prefix> -- two concurrent writer launches
  writer "$1" >"$TMP/$2.a.out" 2>"$TMP/$2.a.err" & RACE_A=$!
  writer "$1" >"$TMP/$2.b.out" 2>"$TMP/$2.b.err" & RACE_B=$!
  wait "$RACE_A"; RACE_SA=$?
  wait "$RACE_B"; RACE_SB=$?
}
races_exits_0_1() { # races_exits_0_1 <name> -- last race_two ended 0 and 1
  { [ "$RACE_SA" -eq 0 ] && [ "$RACE_SB" -eq 1 ]; } \
    || { [ "$RACE_SA" -eq 1 ] && [ "$RACE_SB" -eq 0 ]; } \
    || fail "$1: race exits were $RACE_SA/$RACE_SB (want one 0 and one 1)"
}
race_one_refusal() { # race_one_refusal <name> <out-prefix> -- exactly one stderr refused
  [ "$(grep -l 'exists (records are append-only)' "$TMP/$2.a.err" "$TMP/$2.b.err" | wc -l)" -eq 1 ] \
    || fail "$1: race did not produce exactly one append-only refusal"
}
# --- pnr-regen.sh: naming, retry, race ---------------------------------------
PNR_DIR="$TMP/repo/layout/digital/records"
PNR_REC="$PNR_DIR/$FIXED_DATE-$SHA"
writer pnr-regen.sh >"$TMP/pnr1.out" 2>"$TMP/pnr1.err" \
  || fail "pnr: first launch failed: $(cat "$TMP/pnr1.err")"
[ -d "$PNR_REC" ] || fail "pnr: first launch reserved no record at $PNR_REC"
for f in "$TOP.gds" "$TOP.def" "${TOP}_postroute.v" report.json; do
  [ -f "$PNR_REC/$f" ] || fail "pnr: record missing $f"
done
[ "$(jq -r .status "$PNR_REC/report.json")" = ok ] || fail "pnr: report.json is not the tool report"
[ "$(find "$PNR_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "pnr: unexpected entries in records/"
grep -q "wrote layout/digital/records/$FIXED_DATE-$SHA (stage_reached=route)" "$TMP/pnr1.out" \
  || fail "pnr: first launch stdout lost the record path"

echo "do not touch" >"$PNR_REC/record.md"
h0="$(tree_hash "$PNR_REC")"
if writer pnr-regen.sh >"$TMP/pnr2.out" 2>"$TMP/pnr2.err"; then
  fail "pnr: relaunch against the saved record exited 0"
fi
grep -q "pnr-regen.sh: $PNR_REC exists (records are append-only)" "$TMP/pnr2.err" \
  || fail "pnr: relaunch diagnostic changed: $(cat "$TMP/pnr2.err")"
[ "$(tree_hash "$PNR_REC")" = "$h0" ] || fail "pnr: relaunch changed the saved record"

rm -rf "$PNR_DIR"; mkdir -p "$PNR_DIR" "$TMP/pnr-gate"
: > "$KLT_LOG"
export PNR_GATE="$TMP/pnr-gate" PNR_GATE_N=2
race_two pnr-regen.sh pnr-race
unset PNR_GATE PNR_GATE_N
[ -d "$PNR_REC" ] || fail "pnr: race reserved no record"
[ "$(find "$PNR_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "pnr: race left more than the one record"
for f in "$TOP.gds" "$TOP.def" "${TOP}_postroute.v" report.json; do
  [ -f "$PNR_REC/$f" ] || fail "pnr: raced record missing $f"
done
races_exits_0_1 pnr
race_one_refusal pnr pnr-race
[ "$(grep -c '^klt place-and-route' "$KLT_LOG")" -eq 2 ] \
  || fail "pnr: race reached place-and-route $(grep -c '^klt place-and-route' "$KLT_LOG") times (the tool runs before the reservation; both launches reach it)"
echo "test-reserve-record-dir: PASS: pnr-regen.sh (naming, retry refused untouched, race: one writer)"

# --- lvs-regen.sh: naming, retry, race ---------------------------------------
LVS_DIR="$TMP/repo/layout/digital/lvs-records"
LVS_REC="$LVS_DIR/$FIXED_DATE-$SHA"
: > "$KLT_LOG"
writer lvs-regen.sh >"$TMP/lvs1.out" 2>"$TMP/lvs1.err" \
  || fail "lvs: first launch failed: $(cat "$TMP/lvs1.err")"
[ -d "$LVS_REC" ] || fail "lvs: first launch reserved no record at $LVS_REC"
for f in lvs.report.json lvs.request.json "$TOP.gate.spice"; do
  [ -f "$LVS_REC/$f" ] || fail "lvs: record missing $f"
done
[ -e "$LVS_REC/extract.json" ] && fail "lvs: large extract.json left behind"
[ "$(jq -r .status "$LVS_REC/lvs.report.json")" = match ] || fail "lvs: report is not the tool report"
[ "$(find "$LVS_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "lvs: unexpected entries in lvs-records/"
grep -q "wrote layout/digital/lvs-records/$FIXED_DATE-$SHA (klt lvs exit 0)" "$TMP/lvs1.out" \
  || fail "lvs: first launch stdout lost the record path"

echo "do not touch" >"$LVS_REC/record.md"
h0="$(tree_hash "$LVS_REC")"
if writer lvs-regen.sh >"$TMP/lvs2.out" 2>"$TMP/lvs2.err"; then
  fail "lvs: relaunch against the saved record exited 0"
fi
grep -q "lvs-regen: $LVS_REC exists (records are append-only)" "$TMP/lvs2.err" \
  || fail "lvs: relaunch diagnostic changed: $(cat "$TMP/lvs2.err")"
[ "$(tree_hash "$LVS_REC")" = "$h0" ] || fail "lvs: relaunch changed the saved record"

rm -rf "$LVS_DIR"; mkdir -p "$LVS_DIR"
: > "$KLT_LOG"
race_two lvs-regen.sh lvs-race
[ -d "$LVS_REC" ] || fail "lvs: race reserved no record"
[ "$(find "$LVS_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "lvs: race left more than the one record"
races_exits_0_1 lvs
race_one_refusal lvs lvs-race
[ "$(grep -c '^klt extract' "$KLT_LOG")" -eq 1 ] \
  || fail "lvs: race reached extract $(grep -c '^klt extract' "$KLT_LOG") times (the reservation precedes the tool; one writer only)"
[ "$(grep -c '^klt lvs ' "$KLT_LOG")" -eq 1 ] \
  || fail "lvs: race reached the compare $(grep -c '^klt lvs ' "$KLT_LOG") times (one writer only)"
echo "test-reserve-record-dir: PASS: lvs-regen.sh (naming, retry refused untouched, race: one writer)"

# --- erc-regen.sh: naming, retry, race (the check-then-mkdir bug of #219) ----
ERC_DIR="$TMP/repo/layout/digital/erc-records"
ERC_REC="$ERC_DIR/$FIXED_DATE-$SHA"
: > "$KLT_LOG"
writer erc-regen.sh >"$TMP/erc1.out" 2>"$TMP/erc1.err" \
  || fail "erc: first launch failed: $(cat "$TMP/erc1.err")"
[ -d "$ERC_REC" ] || fail "erc: first launch reserved no record at $ERC_REC"
cmp -s "$TMP/repo/layout/erc/digital.erc.json" "$ERC_REC/erc.spec.json" \
  || fail "erc: archived spec is not the supply spec"
[ "$(jq -r .erc_status "$ERC_REC/erc.report.json")" = clean ] || fail "erc: report is not the tool report"
[ "$(find "$ERC_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "erc: unexpected entries in erc-records/"
grep -q "wrote layout/digital/erc-records/$FIXED_DATE-$SHA (klt erc exit 0)" "$TMP/erc1.out" \
  || fail "erc: first launch stdout lost the record path"
[ "$(grep -c -- '--findings-only' "$KLT_LOG")" -eq 1 ] || fail "erc: first launch reached the tool more than once"

echo "do not touch" >"$ERC_REC/record.md"
h0="$(tree_hash "$ERC_REC")"
if writer erc-regen.sh >"$TMP/erc2.out" 2>"$TMP/erc2.err"; then
  fail "erc: relaunch against the saved record exited 0"
fi
grep -q "erc-regen: $ERC_REC exists (records are append-only)" "$TMP/erc2.err" \
  || fail "erc: relaunch diagnostic changed: $(cat "$TMP/erc2.err")"
[ "$(tree_hash "$ERC_REC")" = "$h0" ] || fail "erc: relaunch changed the saved record"

rm -rf "$ERC_DIR"; mkdir -p "$ERC_DIR"
: > "$KLT_LOG"
race_two erc-regen.sh erc-race
[ -d "$ERC_REC" ] || fail "erc: race reserved no record"
[ "$(find "$ERC_DIR" -mindepth 1 -maxdepth 1 | wc -l)" -eq 1 ] || fail "erc: race left more than the one record"
races_exits_0_1 erc
race_one_refusal erc erc-race
[ "$(grep -c -- '--findings-only' "$KLT_LOG")" -eq 1 ] \
  || fail "erc: race admitted $(grep -c -- '--findings-only' "$KLT_LOG") writers to the tool (want exactly 1)"
echo "test-reserve-record-dir: PASS: erc-regen.sh (naming, retry refused untouched, race: one writer)"

# --- scripts/klt-lib.sh reserve_record_dir, sourced directly -----------------
FN="$TMP/fn"
fn_checks() (
  # shellcheck source=scripts/klt-lib.sh
  . "$SRC/scripts/klt-lib.sh"
  local d out rc
  d="$FN/deep/missing/records/2038-01-19-abc1234"
  reserve_record_dir "$d" fn-pref || { echo "creation under a missing parent refused"; return 1; }
  [ -d "$d" ] || { echo "destination not created under a missing parent"; return 1; }
  echo sentinel >"$d/record.md"
  out="$(reserve_record_dir "$d" fn-pref 2>&1)"; rc=$?
  [ "$rc" -ne 0 ] || { echo "occupied destination admitted"; return 1; }
  case "$out" in
    "fn-pref: $d exists (records are append-only)") ;;
    *) echo "occupied-destination diagnostic: $out"; return 1 ;;
  esac
  grep -qx sentinel "$d/record.md" || { echo "occupied-destination refusal touched the sentinel"; return 1; }
  touch "$FN/afile"
  d="$FN/afile/under/2038-01-19-abc1234"
  out="$(reserve_record_dir "$d" fn-pref 2>&1)"; rc=$?
  [ "$rc" -ne 0 ] || { echo "non-directory parent admitted"; return 1; }
  [ ! -e "$d" ] || { echo "non-directory parent produced a destination"; return 1; }
  case "$out" in
    "fn-pref: "*) ;;
    *) echo "filesystem-error diagnostic lost its prefix: $out"; return 1 ;;
  esac
  case "$out" in
    *"exists (records are append-only)"*) echo "filesystem error reported as an append-only duplicate: $out"; return 1 ;;
  esac
  mkdir -p "$FN/rec2"
  ln -s nowhere "$FN/rec2/dangling"
  out="$(reserve_record_dir "$FN/rec2/dangling" fn-pref 2>&1)"; rc=$?
  [ "$rc" -ne 0 ] || { echo "dangling symlink at the destination admitted"; return 1; }
  case "$out" in
    *"exists (records are append-only)"*) ;;
    *) echo "dangling-symlink diagnostic: $out"; return 1 ;;
  esac
)
mkdir -p "$FN"
fn_checks_out="$(fn_checks)" || fail "reserve_record_dir: ${fn_checks_out:-function contract broken}"

mkdir -p "$FN/race"
fn_one() { bash -c 'ROOT=$1; . "$ROOT/scripts/klt-lib.sh"; reserve_record_dir "$2" fn-pref && echo WON' _ "$SRC" "$FN/race/records/2038-01-19-race1234"; }
fn_one >"$FN/r1.out" 2>"$FN/r1.err" & p1=$!
fn_one >"$FN/r2.out" 2>"$FN/r2.err" & p2=$!
wait "$p1"; wait "$p2"
[ "$(cat "$FN/r1.out" "$FN/r2.out" | grep -c WON)" -eq 1 ] \
  || fail "reserve_record_dir: concurrent reservations did not admit exactly one writer"
[ -d "$FN/race/records/2038-01-19-race1234" ] || fail "reserve_record_dir: concurrent reservations created no destination"
echo "test-reserve-record-dir: PASS: reserve_record_dir (missing parent, sentinel intact, fs errors, race: one writer)"

echo "test-reserve-record-dir: all three writers and the shared reservation hold the contract"
