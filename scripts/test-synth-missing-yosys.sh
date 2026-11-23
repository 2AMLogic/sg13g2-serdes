#!/usr/bin/env bash
# test-synth-missing-yosys.sh -- prove synth-regen.sh exits 3 (the tool-gap
# exit), not 127, when yosys is off PATH, and still exits 3 on a version
# mismatch (issue #262).
# Runs in a disposable repo with a mocked `uvx` and stub yosys: no EDA tool, no
# network, no real PDK. Requires bash and jq. Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-synth-missing-yosys: FAIL: $*" >&2; exit 1; }

R="$TMP/repo"
mkdir -p "$R/scripts" "$R/layout" "$TMP/bin" "$TMP/yosys-bin"
cp "$SRC/scripts/synth-regen.sh" "$SRC/scripts/klt-lib.sh" "$R/scripts/"
cp "$SRC/layout/toolchain.json" "$SRC/layout/tools.json" "$R/layout/"
# Stubs: jq/dirname/head are linked in, uvx is a no-op, PDK_ROOT is preset so klt_env passes.
for t in jq dirname head mkdir; do ln -s "$(command -v "$t")" "$TMP/bin/$t"; done
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/bin/uvx"; chmod +x "$TMP/bin/uvx"
mkdir -p "$TMP/pdk"
BASH_BIN="$(command -v bash)"

run() { # run <extra-path> -- restricted PATH; sets OUT and RC
  OUT="$(cd "$R" && PATH="$1$TMP/bin" PDK_ROOT="$TMP/pdk" "$BASH_BIN" scripts/synth-regen.sh 2>&1)"; RC=$?
}

run ""
[ "$RC" = 3 ] || fail "yosys off PATH: want exit 3, got $RC: $OUT"
case "$OUT" in *yosys*) ;; *) fail "refusal does not name yosys: $OUT" ;; esac

printf '#!%s\necho "Yosys 0.0 (wrong)"\n' "$BASH_BIN" > "$TMP/yosys-bin/yosys"; chmod +x "$TMP/yosys-bin/yosys"
run "$TMP/yosys-bin:"
[ "$RC" = 3 ] || fail "wrong yosys version: want exit 3, got $RC: $OUT"
case "$OUT" in *mismatch*) ;; *) fail "mismatch message lost: $OUT" ;; esac
echo "test-synth-missing-yosys: OK"
