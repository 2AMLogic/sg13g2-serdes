# synth-lib.sh -- shared by synth-regen.sh and check-synth-fresh.sh (sourced).
# Defines KLT (the pinned klt via a throwaway uvx env) and exports PDK_ROOT/PDK;
# the shared pin and PDK resolution lives in scripts/klt-lib.sh. The yosys pin
# is this flow's own check.
# shellcheck shell=bash
# shellcheck source=scripts/klt-lib.sh
. "$ROOT/scripts/klt-lib.sh"

synth_env() {
  klt_env
  local want got
  want="$(jq -r .yosys.version_prefix "$ROOT/layout/tools.json")"
  got="$(yosys -V 2>&1 | head -1)"
  case "$got" in "$want"*) ;; *) echo "synth-lib: yosys mismatch: pinned '$want', found '$got' (worker-spec gap; do not install here)" >&2; exit 3;; esac
  require_pdk_file ihp-sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p20V_25C.lib \
    "synth-lib: SG13G2 stdcell liberty not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)"
}
