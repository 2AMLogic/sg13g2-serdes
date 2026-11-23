# pnr-lib.sh -- shared by pnr-regen.sh, check-pnr-fresh.sh, lvs-regen.sh and
# check-lvs-fresh.sh (sourced). Defines KLT (the pinned klt via a throwaway
# uvx env) and exports PDK_ROOT/PDK; the shared pin and PDK resolution lives
# in scripts/klt-lib.sh. openroad is the worker's.
# shellcheck shell=bash
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"

pnr_env() {
  klt_env
  require_tool openroad "pnr-lib: openroad missing (worker-spec gap; do not install here)"
  require_pdk_file ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef \
    "pnr-lib: SG13G2 stdcell LEF not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)"
  PNR_REQ="$ROOT/layout/digital/place-and-route.request.json"
  PNR_RECORDS="$ROOT/layout/digital/records"
}

# Newest committed record directory (names sort by date).
pnr_latest_record() { ls -d "$PNR_RECORDS"/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::'; }
