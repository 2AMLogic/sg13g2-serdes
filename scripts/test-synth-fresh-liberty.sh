#!/usr/bin/env bash
# test-synth-fresh-liberty.sh -- prove check-synth-fresh.sh and synth-regen.sh
# preflight the Liberty the synth request routes (issue #260, same class as #237).
#
# The request selects pdk.corner; each preflight must require
# <cell_library>_<corner>.lib and nothing else. The committed request routes the
# typical corner, so the disposable copy is jq-rewritten to a non-typical one.
# Runs in a disposable repo with mocked `uvx` (records args, exit 0) and `yosys`:
# no EDA tool, no network, no real PDK.
#   check-synth-fresh, routed-corner-only PDK : exit 0 (reaches klt synthesize --check)
#   check-synth-fresh, typ-only PDK           : exit 3 naming the routed Liberty (before klt)
#   synth-regen, typ-only PDK                 : exit 3 naming the routed Liberty (before klt)
#   synth-regen, routed-corner-only PDK       : passes the Liberty preflight, reaches
#                                               klt synthesize, and exits 1 on the empty mock report
# Requires bash, jq and sha256sum. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-synth-fresh-liberty: FAIL: $*" >&2; exit 1; }

R="$TMP/repo"
CORNER=slow_1p08V_125C
mkdir -p "$R/scripts" "$R/layout" "$R/rtl/synth" "$R/.cache" "$TMP/bin"
cp "$SRC/scripts/check-synth-fresh.sh" "$SRC/scripts/synth-regen.sh" "$SRC/scripts/klt-lib.sh" "$R/scripts/"
cp "$SRC/layout/toolchain.json" "$SRC/layout/tools.json" "$R/layout/"
jq --arg c "$CORNER" '.pdk.corner = $c' "$SRC/rtl/synth/request.json" > "$R/rtl/synth/request.json"
CELL="$(jq -r .pdk.cell_library "$R/rtl/synth/request.json")"
GOT="$(jq -r .pdk.corner "$R/rtl/synth/request.json")"
[ "$GOT" = "$CORNER" ] || fail "could not override the request corner"
[ "$GOT" != typ_1p20V_25C ] || fail "corner under test is the typical corner; the test would be a tautology"
TOP="$(jq -r .hdl_toplevel "$R/rtl/synth/request.json")"
echo "module $TOP; endmodule" > "$R/rtl/synth/${TOP}_synth.v"
printf '{"netlist_sha256": "%s"}\n' "$(sha256sum "$R/rtl/synth/${TOP}_synth.v" | awk '{print $1}')" \
  > "$R/rtl/synth/$TOP.synth.json"
UVX_LOG="$TMP/uvx.log"
cat > "$TMP/bin/uvx" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$UVX_LOG"
exit 0
EOF
chmod +x "$TMP/bin/uvx"
printf '#!/usr/bin/env bash\necho "%s mock"\n' "$(jq -r .yosys.version_prefix "$R/layout/tools.json")" > "$TMP/bin/yosys"
chmod +x "$TMP/bin/yosys"

pdk() { # pdk <name> <corner>... -- a PDK holding only the named Liberty corners
  local d="$TMP/pdk-$1" c; shift
  mkdir -p "$d/ihp-sg13g2/libs.ref/$CELL/lib"
  for c in "$@"; do : > "$d/ihp-sg13g2/libs.ref/$CELL/lib/${CELL}_${c}.lib"; done
  echo "$d"
}
run() { # run <script> <pdk> -- resets UVX_LOG, sets OUT and RC
  : > "$UVX_LOG"
  OUT="$(cd "$R" && PATH="$TMP/bin:$PATH" PDK_ROOT="$2" UVX_LOG="$UVX_LOG" bash "scripts/$1" 2>&1)"; RC=$?
}
refused_at_liberty() { case "$OUT" in *"${CELL}_${CORNER}.lib"*) return 0 ;; *) return 1 ;; esac; }

run check-synth-fresh.sh "$(pdk slow "$CORNER")"
[ "$RC" = 0 ] || fail "check-synth-fresh, routed-corner-only PDK: want exit 0, got $RC: $OUT"
grep -qE 'klt synthesize .* --check ' "$UVX_LOG" \
  || fail "check-synth-fresh, routed-corner-only PDK did not reach klt synthesize --check: $OUT"
run check-synth-fresh.sh "$(pdk typ typ_1p20V_25C)"
[ "$RC" = 3 ] || fail "check-synth-fresh, typical-only PDK: want exit 3, got $RC: $OUT"
refused_at_liberty || fail "check-synth-fresh refusal does not name the routed Liberty: $OUT"
[ ! -s "$UVX_LOG" ] || fail "check-synth-fresh, typical-only PDK invoked klt despite Liberty refusal"
run synth-regen.sh "$(pdk typ typ_1p20V_25C)"
[ "$RC" = 3 ] || fail "synth-regen, typical-only PDK: want exit 3, got $RC: $OUT"
refused_at_liberty || fail "synth-regen refusal does not name the routed Liberty: $OUT"
[ ! -s "$UVX_LOG" ] || fail "synth-regen, typical-only PDK invoked klt despite Liberty refusal"
run synth-regen.sh "$(pdk slow "$CORNER")"
[ "$RC" = 1 ] || fail "synth-regen, routed-corner-only PDK: want exit 1 (empty mock report after preflight), got $RC: $OUT"
grep -qE 'klt synthesize .* --format json$' "$UVX_LOG" \
  || fail "synth-regen, routed-corner-only PDK did not reach klt synthesize: $OUT"
case "$OUT" in
  *"synth-regen.sh: synthesis status= has_critical="*) ;;
  *) fail "synth-regen, routed-corner-only PDK did not fail at empty mock report: $OUT" ;;
esac
echo "test-synth-fresh-liberty: OK"
