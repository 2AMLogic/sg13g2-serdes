#!/usr/bin/env bash
# test-sta-paths-liberty.sh -- prove sta-paths.sh preflights the Liberty the
# synth request routes (issue #276, same class as #237 and #260).
#
# The request selects pdk.cell_library and pdk.corner; the preflight must
# require <cell_library>_<corner>.lib and nothing else, and the klt sta
# request and the OpenSTA script must name that same Liberty. The committed
# request routes the typical corner, so the disposable copy is jq-rewritten
# to a non-typical one. Runs in a disposable repo with a mocked `uvx`
# (records args, prints a klt sta report) and `openroad`: no EDA tool, no
# network, no real PDK.
#   routed-corner-only PDK      : exit 0 (the false refusal this guards); klt sta
#                                 and the OpenSTA script name the routed Liberty
#   typ-only PDK                : exit 3 naming the routed Liberty (before klt)
#   no-Liberty PDK              : exit 3 naming the routed Liberty (before klt)
#   renamed cell library        : exit 0; Liberty, LEF and sta_request.json all
#                                 follow pdk.cell_library
# Requires bash and jq. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-sta-paths-liberty: FAIL: $*" >&2; exit 1; }

R="$TMP/repo"
CORNER=slow_1p08V_125C
O="$R/.cache/sta"
mkdir -p "$R/scripts" "$R/layout" "$R/rtl/synth" "$TMP/bin"
cp "$SRC/scripts/sta-paths.sh" "$SRC/scripts/sta-paths.tcl" "$SRC/scripts/klt-lib.sh" "$R/scripts/"
cp "$SRC/layout/toolchain.json" "$R/layout/"
req() { # req [cell_library] -- the committed request, re-routed to $CORNER and to $1 (default: its own library)
  if [ $# -eq 0 ]; then
    jq --arg c "$CORNER" '.pdk.corner = $c' "$SRC/rtl/synth/request.json"
  else
    jq --arg c "$CORNER" --arg l "$1" '.pdk.corner = $c | .pdk.cell_library = $l' "$SRC/rtl/synth/request.json"
  fi
}
req > "$R/rtl/synth/request.json"
CELL="$(jq -r .pdk.cell_library "$R/rtl/synth/request.json")"
GOT="$(jq -r .pdk.corner "$R/rtl/synth/request.json")"
[ "$GOT" = "$CORNER" ] || fail "could not override the request corner"
[ "$GOT" != typ_1p20V_25C ] || fail "corner under test is the typical corner; the test would be a tautology"
UVX_LOG="$TMP/uvx.log"
cat > "$TMP/bin/uvx" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "$UVX_LOG"
printf '{"worst_slack_ns": -0.5, "hdl_toplevel": "top", "fmax_mhz": 500, "setup_violation_count": 3}\n'
EOF
chmod +x "$TMP/bin/uvx"
printf '#!/usr/bin/env bash\nprintf "== global worst setup path ==\\nslack (VIOLATED) -0.5 ns\\n"\n' > "$TMP/bin/openroad"
chmod +x "$TMP/bin/openroad"

pdk() { # pdk <name> <cell_library> <corner>... -- a PDK whose <cell_library> holds its LEF and only the named Liberty corners
  local d="$TMP/pdk-$1" cell="$2" c; shift 2
  mkdir -p "$d/ihp-sg13g2/libs.ref/$cell/lib" "$d/ihp-sg13g2/libs.ref/$cell/lef"
  for c in "$@"; do : > "$d/ihp-sg13g2/libs.ref/$cell/lib/${cell}_${c}.lib"; done
  : > "$d/ihp-sg13g2/libs.ref/$cell/lef/sg13g2_stdcell.lef"
  echo "$d"
}
run() { # run <pdk> [cell_library] -- route the request, run sta-paths.sh; sets OUT and RC
  : > "$UVX_LOG"
  req ${2:+"$2"} > "$R/rtl/synth/request.json"
  OUT="$(cd "$R" && PATH="$TMP/bin:$PATH" PDK_ROOT="$1" UVX_LOG="$UVX_LOG" bash scripts/sta-paths.sh 2>&1)"; RC=$?
}
tcl_must_have() { # tcl_must_have <exact line> -- the generated OpenSTA script contains it
  grep -qx "$1" "$O/sta-paths.run.tcl" || fail "$2: $1 absent from sta-paths.run.tcl: $(cat "$O/sta-paths.run.tcl")"
}

P="$(pdk slow "$CELL" "$CORNER")"
run "$P"
[ "$RC" = 0 ] || fail "routed-corner-only PDK: want exit 0, got $RC: $OUT"
grep -qE 'klt sta .*sta_request\.json --format json$' "$UVX_LOG" \
  || fail "routed-corner-only PDK did not reach klt sta: $OUT"
jq -e --arg l "$CELL" --arg c "$CORNER" '.pdk == {cell_library: $l, corner: $c}' "$O/sta_request.json" >/dev/null \
  || fail "sta_request.json does not route the request's cell library and corner: $(cat "$O/sta_request.json")"
tcl_must_have "read_liberty $P/ihp-sg13g2/libs.ref/$CELL/lib/${CELL}_${CORNER}.lib" \
  "OpenSTA script does not read the routed Liberty"
tcl_must_have "read_lef $P/ihp-sg13g2/libs.ref/$CELL/lef/sg13g2_stdcell.lef" \
  "OpenSTA script does not read the cell library's LEF"

run "$(pdk typ "$CELL" typ_1p20V_25C)"
[ "$RC" = 3 ] || fail "typical-only PDK: want exit 3, got $RC: $OUT"
case "$OUT" in *"${CELL}_${CORNER}.lib"*) ;; *) fail "refusal does not name the routed Liberty: $OUT" ;; esac
[ ! -s "$UVX_LOG" ] || fail "typical-only PDK invoked klt despite the Liberty refusal"

run "$(pdk none "$CELL")"
[ "$RC" = 3 ] || fail "no-Liberty PDK: want exit 3, got $RC: $OUT"
case "$OUT" in *"${CELL}_${CORNER}.lib"*) ;; *) fail "missing-Liberty refusal does not name the routed Liberty: $OUT" ;; esac
[ ! -s "$UVX_LOG" ] || fail "no-Liberty PDK invoked klt despite the Liberty refusal"

ALT=alt_stdcell
P="$(pdk alt "$ALT" "$CORNER")"
run "$P" "$ALT"
[ "$RC" = 0 ] || fail "renamed cell library: want exit 0, got $RC: $OUT"
grep -qE 'klt sta .*sta_request\.json --format json$' "$UVX_LOG" \
  || fail "renamed cell library did not reach klt sta: $OUT"
jq -e --arg l "$ALT" '.pdk.cell_library == $l' "$O/sta_request.json" >/dev/null \
  || fail "sta_request.json does not route the renamed cell library: $(cat "$O/sta_request.json")"
tcl_must_have "read_liberty $P/ihp-sg13g2/libs.ref/$ALT/lib/${ALT}_${CORNER}.lib" \
  "OpenSTA script does not read the renamed library's Liberty"
tcl_must_have "read_lef $P/ihp-sg13g2/libs.ref/$ALT/lef/sg13g2_stdcell.lef" \
  "OpenSTA script does not read the renamed library's LEF"
echo "test-sta-paths-liberty: OK"
