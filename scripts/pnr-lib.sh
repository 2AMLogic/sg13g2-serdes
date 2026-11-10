# pnr-lib.sh -- shared by pnr-regen.sh and check-pnr-fresh.sh (sourced).
# Defines KLT (the pinned klt via a throwaway uvx env) and exports PDK_ROOT/PDK.
# Same pin and PDK resolution as scripts/synth-lib.sh; openroad is the worker's.

pnr_env() {
  command -v jq >/dev/null || { echo "pnr-lib: jq missing" >&2; exit 3; }
  command -v uvx >/dev/null || { echo "pnr-lib: uvx missing" >&2; exit 3; }
  command -v openroad >/dev/null || { echo "pnr-lib: openroad missing (worker-spec gap; do not install here)" >&2; exit 3; }
  local pin
  pin="$(jq -r .klt_install "$ROOT/layout/toolchain.json")"
  KLT=(uvx --quiet --from "$pin" klt)
  if [ -z "${PDK_ROOT:-}" ]; then
    PDK_ROOT="$ROOT/.cache/pdk/$(jq -r .extracted_dir "$ROOT/sim/pdk.json")"
  fi
  [ -f "$PDK_ROOT/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_stdcell.lef" ] || {
    echo "pnr-lib: SG13G2 stdcell LEF not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)" >&2; exit 3; }
  export PDK_ROOT PDK=ihp-sg13g2
  mkdir -p "$ROOT/.cache"
  PNR_REQ="$ROOT/layout/digital/place-and-route.request.json"
  PNR_RECORDS="$ROOT/layout/digital/records"
}

# Newest committed record directory (names sort by date).
pnr_latest_record() { ls -d "$PNR_RECORDS"/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::'; }
