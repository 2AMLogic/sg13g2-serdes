#!/usr/bin/env bash
# Per-module cocotb benches for the digital partition.
#
#   rtl/tests/run.sh            all benches, one after another
#   rtl/tests/run.sh prbs_gen   one bench (prbs_gen prbs_chk cdr_pd cdr loopback eye ctrl top)
#
# cocotb is never installed on the host: it is provisioned per run in a
# throwaway uvx environment at the version pinned in layout/tools.json; iverilog
# comes from the worker (version checked against the same file). Benches run
# strictly one at a time.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TOOLS="$ROOT/layout/tools.json"
die() { echo "run.sh: $*" >&2; exit 2; }

COCOTB_VER="$(jq -r .cocotb.version "$TOOLS")"
COCOTB_PY="$(jq -r .cocotb.python "$TOOLS")"
ICARUS_WANT="$(jq -r .icarus.version_prefix "$TOOLS")"
[ -n "$COCOTB_VER" ] && [ "$COCOTB_VER" != null ] || die "cocotb version not pinned in layout/tools.json"
ICARUS_GOT="$(iverilog -V 2>&1 | head -1)"
case "$ICARUS_GOT" in "$ICARUS_WANT"*) ;; *) die "icarus mismatch: pinned '$ICARUS_WANT', found '$ICARUS_GOT' (worker-spec gap; do not install here)";; esac

UV=(uvx --quiet --python "$COCOTB_PY" --from "cocotb==$COCOTB_VER")
got="$("${UV[@]}" cocotb-config --version 2>&1 | tail -1)"
[ "$got" = "$COCOTB_VER" ] || die "cocotb mismatch: pinned '$COCOTB_VER', environment reports '$got'"

run_one() { # name test_module toplevel sources
  echo "== $1"
  (cd "$ROOT/rtl/tests" && "${UV[@]}" python -I runner.py "$2" "$3" "$4")
}
bench() {
  case "$1" in
    prbs_gen) run_one "$1" test_prbs_gen serdes_prbs_gen serdes_prbs_gen.v ;;
    prbs_chk) run_one "$1" test_prbs_chk serdes_prbs_chk serdes_prbs_chk.v ;;
    cdr)      run_one "$1" test_cdr serdes_cdr_filter serdes_cdr_filter.v ;;
    cdr_pd)   run_one "$1" test_cdr_pd serdes_cdr_pd serdes_cdr_pd.v ;;
    loopback) run_one "$1" test_loopback serdes_loopback serdes_loopback.v ;;
    eye)      run_one "$1" test_eye serdes_eye_mon serdes_eye_mon.v ;;
    ctrl)     run_one "$1" test_ctrl serdes_ctrl serdes_ctrl.v ;;
    top)      run_one "$1" test_top serdes_digital_top serdes_prbs_gen.v,serdes_prbs_chk.v,serdes_cdr_pd.v,serdes_cdr_filter.v,serdes_loopback.v,serdes_eye_mon.v,serdes_ctrl.v,serdes_digital_top.v ;;
    *) die "unknown bench '$1'" ;;
  esac
}
if [ $# -gt 0 ]; then bench "$1"; exit $?; fi
rc=0
for b in prbs_gen prbs_chk cdr_pd cdr loopback eye ctrl top; do bench "$b" || rc=1; done
exit $rc
