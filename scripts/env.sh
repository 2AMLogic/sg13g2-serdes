# Source me:  source scripts/env.sh
# Exports the repo-local PDK and tool environment produced by scripts/setup-env.sh.
# shellcheck shell=bash
_serdes_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDK="ihp-sg13g2"
# shellcheck source=scripts/klt-lib.sh
. "${_serdes_repo}/scripts/klt-lib.sh"
if _pdk_root="$(pdk_default_root "${_serdes_repo}")"; then
  export PDK_ROOT="${_pdk_root}"
else
  # sourced context: refuse loudly, keep the shell alive, never export a
  # truncated PDK_ROOT and never clobber a value the caller already set.
  echo "env.sh: cannot resolve the default PDK root from sim/pdk.json -- is 'jq' on PATH? Prerequisites are listed in README.md; scripts/setup-env.sh --check verifies them. Leaving PDK_ROOT ${PDK_ROOT:-unset}." >&2
fi
export PATH="${_serdes_repo}/.venv/bin:${PATH}"
unset _serdes_repo _pdk_root
unset -f klt_env pdk_default_root require_pdk_file require_tool
