#!/usr/bin/env bash
# test-pnr-fresh-liberty.sh -- prove check-pnr-fresh.sh's Liberty preflight
# follows the corner the P&R request routes (issue #236 review of PR #237).
#
# The request selects pdk.corner; the preflight must require
# <cell_library>_<corner>.lib and nothing else, so a PDK holding only the routed
# corner is enough for cheap mode, and a PDK holding only a different corner
# is refused. Runs in a disposable repo with a mocked `uvx` standing in for klt
# (exit 0): no EDA tool, no network, no real PDK.
#   slow-only PDK, default mode : exit 0 (the false refusal this guards)
#   typ-only PDK, default mode  : exit 3 naming the routed Liberty
#   slow-only PDK, --rerun      : passes the Liberty preflight, then exit 3 at
#                                 the missing tool/LEF -- never at the Liberty
# Requires bash, jq and sha256sum. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-pnr-fresh-liberty: FAIL: $*" >&2; exit 1; }

R="$TMP/repo"
mkdir -p "$R/scripts" "$R/layout/digital/records/2038-01-19-abc1234" "$R/rtl/synth" "$TMP/bin"
cp "$SRC/scripts/check-pnr-fresh.sh" "$SRC/scripts/klt-lib.sh" "$R/scripts/"
cp "$SRC/layout/toolchain.json" "$R/layout/"
cp "$SRC/layout/digital/place-and-route.request.json" "$R/layout/digital/"
TOP="$(jq -r .hdl_toplevel "$R/layout/digital/place-and-route.request.json")"
CELL="$(jq -r .pdk.cell_library "$R/layout/digital/place-and-route.request.json")"
CORNER="$(jq -r .pdk.corner "$R/layout/digital/place-and-route.request.json")"
[ "$CORNER" != typ_1p20V_25C ] || fail "request routes the typical corner; this test needs a non-typical one"
REC="$R/layout/digital/records/2038-01-19-abc1234"
for f in "$TOP.gds" "$TOP.def" "${TOP}_postroute.v"; do echo x > "$REC/$f"; done
echo '{"status": "ok"}' > "$REC/report.json"
echo "module $TOP; endmodule" > "$R/rtl/synth/${TOP}_synth.v"
printf '{"netlist_sha256": "%s"}\n' "$(sha256sum "$R/rtl/synth/${TOP}_synth.v" | awk '{print $1}')" \
  > "$R/rtl/synth/$TOP.synth.json"
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/bin/uvx"; chmod +x "$TMP/bin/uvx"

pdk() { # pdk <name> <corner>... -- a PDK holding only the named Liberty corners
  local d="$TMP/pdk-$1" c; shift
  mkdir -p "$d/ihp-sg13g2/libs.ref/$CELL/lib"
  for c in "$@"; do : > "$d/ihp-sg13g2/libs.ref/$CELL/lib/${CELL}_${c}.lib"; done
  echo "$d"
}
run() { # run <pdk> [args] -- sets OUT and RC
  OUT="$(cd "$R" && PATH="$TMP/bin:$PATH" PDK_ROOT="$1" bash scripts/check-pnr-fresh.sh "${@:2}" 2>&1)"; RC=$?
}

run "$(pdk slow "$CORNER")"
[ "$RC" = 0 ] || fail "routed-corner-only PDK, default mode: want exit 0, got $RC: $OUT"
run "$(pdk typ typ_1p20V_25C)"
[ "$RC" = 3 ] || fail "typical-only PDK, default mode: want exit 3, got $RC: $OUT"
case "$OUT" in *"${CELL}_${CORNER}.lib"*) ;; *) fail "refusal does not name the routed Liberty: $OUT" ;; esac
run "$(pdk slow "$CORNER")" --rerun
[ "$RC" = 3 ] || fail "routed-corner-only PDK, --rerun: want exit 3, got $RC: $OUT"
case "$OUT" in *liberty*) fail "--rerun refused at the Liberty, not the tool/LEF: $OUT" ;; esac
echo "test-pnr-fresh-liberty: OK"
