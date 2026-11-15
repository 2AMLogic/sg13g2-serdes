# klt-lib.sh -- shared klt/PDK environment preflight (sourced).
# One copy of what pnr-lib.sh and synth-lib.sh used to duplicate: the jq/uvx
# preflight, the pinned klt runner (layout/toolchain.json via a throwaway uvx
# env), the $PDK_ROOT fallback (sim/pdk.json -> .cache/pdk), and the
# PDK_ROOT/PDK exports. The per-flow checks -- which tool the flow runs and
# which PDK sentinel it needs -- stay with the caller through require_tool /
# require_pdk_file; every refusal exits 3, this repo's tool-gap exit.
# shellcheck shell=bash

klt_env() { # needs $ROOT (the repo root, as set by the sourcing script)
  require_tool jq
  require_tool uvx
  local pin
  pin="$(jq -r .klt_install "$ROOT/layout/toolchain.json")"
  KLT=(uvx --quiet --from "$pin" klt)
  if [ -z "${PDK_ROOT:-}" ]; then
    PDK_ROOT="$(pdk_default_root "$ROOT")" || exit 3
  fi
  export PDK_ROOT PDK=ihp-sg13g2
  mkdir -p "$ROOT/.cache"
}

require_tool() { # require_tool <cmd> [message] -- exit 3 when <cmd> is off PATH
  command -v "$1" >/dev/null 2>&1 || {
    echo "${2:-klt-lib: $1 missing}" >&2
    exit 3
  }
}

require_pdk_file() { # require_pdk_file <relpath-under-$PDK_ROOT> [message]
  [ -f "$PDK_ROOT/$1" ] || {
    echo "${2:-klt-lib: required PDK file $1 not found under PDK_ROOT=$PDK_ROOT (run scripts/setup-env.sh)}" >&2
    exit 3
  }
}

pdk_default_root() { # pdk_default_root <repo-root> -- the $PDK_ROOT fallback
  # return (not exit): env.sh sources this library and must survive the refusal.
  # Exit-code contract is unchanged: the caller turns the non-zero into exit 3.
  local v
  v="$(jq -r .extracted_dir "$1/sim/pdk.json")" || return 3
  [ -n "$v" ] && [ "$v" != null ] || return 3
  echo "$1/.cache/pdk/$v"
}
