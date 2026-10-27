# synth-lib.sh -- shared by synth-regen.sh and check-synth-fresh.sh (sourced).
# Defines KLT (the pinned klt via a throwaway uvx env) and exports PDK_ROOT/PDK.

synth_env() {
  command -v jq >/dev/null || { echo "synth-lib: jq missing" >&2; exit 3; }
  command -v uvx >/dev/null || { echo "synth-lib: uvx missing" >&2; exit 3; }
  local want got
  want="$(jq -r .yosys.version_prefix "$ROOT/layout/tools.json")"
  got="$(yosys -V 2>&1 | head -1)"
  case "$got" in "$want"*) ;; *) echo "synth-lib: yosys mismatch: pinned '$want', found '$got' (worker-spec gap; do not install here)" >&2; exit 3;; esac
  local pin
  pin="$(jq -r .klt_install "$ROOT/layout/toolchain.json")"
  KLT=(uvx --quiet --from "$pin" klt)
  if [ -z "${PDK_ROOT:-}" ]; then
    local tag
    tag="$(jq -r .extracted_dir "$ROOT/sim/pdk.json")"
    PDK_ROOT="$ROOT/.cache/pdk/$tag"
  fi
  [ -f "$PDK_ROOT/ihp-sg13g2/libs.ref/sg13g2_stdcell/lib/sg13g2_stdcell_typ_1p20V_25C.lib" ] || {
    echo "synth-lib: SG13G2 stdcell liberty not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)" >&2; exit 3; }
  export PDK_ROOT PDK=ihp-sg13g2
  mkdir -p "$ROOT/.cache"
}
