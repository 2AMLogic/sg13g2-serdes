#!/usr/bin/env bash
# test-osdi-missing-dpkg-deb.sh -- prove build-osdi.sh's missing-dpkg-deb
# diagnostic (issue #283) is actionable: with an empty extraction cache and
# the extractor absent it exits 3, names the missing executable, names the
# package that provides it, and tells the operator to rerun the build -- and
# no longer prints a manual recovery recipe that itself needs dpkg-deb (the
# executable the diagnostic just said is missing). Also pins the two
# behaviors the message now relies on instead of that recipe: the extraction
# cache still short-circuits the check with no dpkg-deb on PATH, and a
# placeholder library exported via LD_LIBRARY_PATH cannot bypass the
# file-based cache check. No network, no PDK, no EDA tool: bash + cat only.
# Exit 0 = the contract holds.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="$(cd "${HERE}/../.." && pwd)"
TMP="$(mktemp -d)" || exit 1
trap 'rm -rf "$TMP"' EXIT
fail() { echo "test-osdi-missing-dpkg-deb: FAIL: $*" >&2; exit 1; }

# Build a runnable harness from the REAL script: the LIBLLVM21 pins, the
# OPENVAF_TAG the diagnostic cites, and the ensure_libllvm21 helper verbatim,
# so the test cannot drift from the shipped message.
BUILD="$SRC/sim/tools/build-osdi.sh"
sed -n '/^OPENVAF_TAG=/p;/^LIBLLVM21_DEB_URL=/,/^LIBLLVM21_DEB_ASSET=/p;/^ensure_libllvm21() {/,/^}$/p' \
  "$BUILD" > "$TMP/helper.sh"
grep -q '^ensure_libllvm21() {' "$TMP/helper.sh" \
  || fail "could not extract ensure_libllvm21 from $BUILD"
grep -q '^LIBLLVM21_DEB_ASSET=' "$TMP/helper.sh" \
  || fail "could not extract the LIBLLVM21 pins from $BUILD"
echo 'ensure_libllvm21' >> "$TMP/helper.sh"

# PATH with no dpkg-deb on it: cat (the diagnostic heredoc) is the only
# external command the helper needs on the refusal path.
BIN="$TMP/bin"
mkdir -p "$BIN"
ln -s "$(command -v cat)" "$BIN/cat"
BASH_BIN="$(command -v bash)"
CACHE_DIR="$TMP/empty-cache"
mkdir -p "$CACHE_DIR"

run_helper() (
  cd "$TMP" || exit 1
  PATH="$BIN" CACHE_DIR="$CACHE_DIR" "$BASH_BIN" "$TMP/helper.sh"
) >"$TMP/stdout" 2>"$TMP/stderr"

# --- case 1: empty cache, extractor absent -------------------------------
run_helper; RC=$?
ERR=$(<"$TMP/stderr")
[ "$RC" = 3 ] || fail "dpkg-deb off PATH: want exit 3, got $RC: $ERR"
[ ! -s "$TMP/stdout" ] || fail "refusal wrote to stdout: $(<"$TMP/stdout")"
case "$ERR" in *dpkg-deb*) ;; *) fail "refusal does not name the missing executable dpkg-deb: $ERR" ;; esac
install_dpkg='(^|[[:space:]])[Ii]nstall[[:space:]]+(the[[:space:]]+)?dpkg\.?([^[:alnum:]_.+-]|$)'
[[ $ERR =~ $install_dpkg ]] || fail "refusal does not tell the operator to install the dpkg package: $ERR"
case "$ERR" in *sim/tools/build-osdi.sh*) ;; *) fail "refusal does not tell the operator to rerun the build: $ERR" ;; esac
case "$ERR" in *dpkg-deb\ -x*) fail "refusal still prints the manual dpkg-deb -x recipe it just called unusable: $ERR" ;; esac

# --- case 2: placeholder via LD_LIBRARY_PATH must not bypass -------------
# Why the removed recipe could never work: a libLLVM.so.21.1 extracted on
# another host and exported via LD_LIBRARY_PATH still leaves the build's own
# cache check empty, so the only usable retry is install + rerun.
mkdir -p "$TMP/placeholder-lib"
: > "$TMP/placeholder-lib/libLLVM.so.21.1"
LD_LIBRARY_PATH="$TMP/placeholder-lib" run_helper; RC=$?
[ "$RC" = 3 ] || fail "placeholder LD_LIBRARY_PATH must not bypass the cache check: want exit 3, got $RC: $(<"$TMP/stderr")"

# --- case 3: cache hit short-circuits without dpkg-deb -------------------
# The pinned download / checksum / cache behavior is untouched by the new
# message: a cached library satisfies the helper with no dpkg-deb at all.
# shellcheck disable=SC1090
source <(sed -n '/^LIBLLVM21_DEB_URL=/,/^LIBLLVM21_DEB_ASSET=/p' "$BUILD")
libdir="${CACHE_DIR}/${LIBLLVM21_DEB_ASSET%.deb}/usr/lib/x86_64-linux-gnu"
mkdir -p "$libdir"
: > "$libdir/libLLVM.so.21.1"
run_helper; RC=$?
[ "$RC" = 0 ] || fail "cache hit must succeed without dpkg-deb: want exit 0, got $RC: $(<"$TMP/stderr")"
OUT=$(<"$TMP/stdout")
[ "$OUT" = "$libdir" ] || fail "cache hit must print the cached libdir on stdout, got: $OUT"
echo "test-osdi-missing-dpkg-deb: OK"
