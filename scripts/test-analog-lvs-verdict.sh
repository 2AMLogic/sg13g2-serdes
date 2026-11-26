#!/usr/bin/env bash
# test-analog-lvs-verdict.sh -- prove analog-lvs-regen.sh uses ONE verdict for
# fresh and stored reports (issue #281): whatever the fresh write accepts must
# also pass the rerun over the stored files, and whatever it rejects must fail
# the rerun too, with the stored evidence left byte-identical.
#
# Runs the RX generator twice per case in a disposable repo with a mocked uvx
# standing in for klt that replays the committed RX converter reports (the
# newest committed record's GDS and reference netlist are copied alongside, so
# the replayed hashes stay bound). First run = fresh write, second = the
# existing-record path. No EDA tool, no network, no real PDK.
#   committed reports           : exit 0 twice, report digests unchanged
#   reference SHA-256 zeroed    : exit 1 twice (previously 0 then 1)
#   power connectivity mismatch : exit 1 twice (previously 1 then 0)
#   valid newer record published during LVS: the original mismatch exits 1
# Requires bash, jq and sha256sum. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-analog-lvs-verdict: FAIL: $*" >&2; exit 1; }

CREC="$(ls -d "$SRC/layout/analog/rx/records"/*/ | sort | tail -1)" || fail "no committed rx record"
CREC="${CREC%/}"
REC_NAME="${CREC##*/}"
CELL=lvl_cml2cmos
R="$TMP/repo"
REC="$R/layout/analog/rx/records/$REC_NAME"
NEWER="$R/layout/analog/rx/records/9999-12-31-valid"
FIX="$TMP/fixtures"
mkdir -p "$R/scripts" "$R/layout/analog/rx/records" "$R/design/rx/netlists" \
         "$REC" "$FIX" "$TMP/bin" "$TMP/pdk"
cp "$SRC/scripts/analog-lvs-regen.sh" "$SRC/scripts/analog-cell-evidence-lib.sh" \
   "$SRC/scripts/klt-lib.sh" "$R/scripts/"
cp "$SRC/layout/toolchain.json" "$R/layout/"
cp "$CREC/$CELL.gds" "$REC/"
cp "$SRC/design/rx/netlists/lvl_cml2cmos.spice" "$R/design/rx/netlists/"

# uvx stub: klt drc/lvs replay the fixture reports to stdout (cat at call
# time, so swapping the fixture between cases retargets the stub).
cat >"$TMP/bin/uvx" <<EOF
#!/usr/bin/env bash
case " \$* " in
  *" drc "*) exec cat "$FIX/drc.report.json" ;;
  *" lvs "*)
    if [ -d "$TMP/next-record" ]; then
      mv "$TMP/next-record" "$NEWER" || exit 1
    fi
    exec cat "$FIX/lvs.report.json" ;;
  *) echo "uvx stub: unexpected klt call: \$*" >&2; exit 127 ;;
esac
EOF
chmod +x "$TMP/bin/uvx"

run() { # run -- one analog-lvs-regen.sh rx pass; sets OUT and RC
  OUT="$(cd "$R" && PATH="$TMP/bin:$PATH" PDK_ROOT="$TMP/pdk" \
    bash scripts/analog-lvs-regen.sh rx 2>&1)"; RC=$?
}

digests() { # digests -- sha256 of every file the generator wrote for the cell
  (cd "$REC/$CELL" && sha256sum * 2>/dev/null | sort)
}

case_run() { # case_run <name> <want-first> <want-rerun>
  local name="$1" want1="$2" want2="$3" d1 d2
  rm -rf "${REC:?}/$CELL"
  run
  [ "$RC" = "$want1" ] || fail "$name: first run: want exit $want1, got $RC: $OUT"
  d1="$(digests)"
  [ -n "$d1" ] || fail "$name: first run wrote no reports: $OUT"
  run
  [ "$RC" = "$want2" ] || fail "$name: rerun: want exit $want2, got $RC: $OUT"
  d2="$(digests)"
  [ "$d1" = "$d2" ] \
    || fail "$name: rerun changed the stored evidence (append-only violated)"$'\n'"first:  $d1"$'\n'"rerun:  $d2"
}

# Case 1: the committed reports verbatim -- accepted on the fresh write and on
# the rerun, with the stored evidence untouched.
cp "$CREC/$CELL/drc.report.json" "$CREC/$CELL/lvs.report.json" "$FIX/"
case_run committed 0 0
case "$OUT" in
  *"evidence already recorded and valid"*) ;;
  *) fail "committed: rerun did not report the stored evidence as valid: $OUT" ;;
esac

# Case 2: reference SHA-256 zeroed -- rejected on both runs (the fresh write
# used to accept it because it never checked the hashes).
jq '.environment.reference_sha256 = "0000000000000000000000000000000000000000000000000000000000000000"' \
  "$CREC/$CELL/lvs.report.json" >"$FIX/lvs.report.json" || fail "cannot build zeroed-reference fixture"
case_run ref-hash-zeroed 1 1
case "$OUT" in
  *reference*hash*) ;;
  *) fail "ref-hash-zeroed: failure does not name the reference hash: $OUT" ;;
esac

# Case 3: power connectivity mismatch -- rejected on both runs (the rerun used
# to accept it because the stored path never checked power).
jq '.power_connectivity.status = "mismatch"' \
  "$CREC/$CELL/lvs.report.json" >"$FIX/lvs.report.json" || fail "cannot build power-mismatch fixture"
case_run power-mismatch 1 1
case "$OUT" in
  *power*) ;;
  *) fail "power-mismatch: failure does not name power connectivity: $OUT" ;;
esac

# Case 4: publish a valid later record while LVS writes the mismatch into REC.
rm -rf "${REC:?}/$CELL"
cp -R "$CREC" "$TMP/next-record" || fail "cannot stage the valid newer record"
run
[ "$RC" = 1 ] || fail "concurrent record: want exit 1 for the original mismatch, got $RC: $OUT"
[[ "$OUT" == *"file=layout/analog/rx/records/$REC_NAME/$CELL/lvs.report.json::analog-lvs-regen: power connectivity status is mismatch"* ]] \
  || fail "concurrent record: expected the mismatch in $REC_NAME: $OUT"
run
[ "$RC" = 0 ] || fail "concurrent record: next run rejected the valid record: $OUT"
[[ "$OUT" == *"evidence already recorded and valid (record ${NEWER#"$R"/})"* ]] \
  || fail "concurrent record: expected the next run to validate the newer record: $OUT"

echo "test-analog-lvs-verdict: OK"
