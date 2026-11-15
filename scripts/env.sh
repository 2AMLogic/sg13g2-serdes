# Source me:  source scripts/env.sh
# Exports the repo-local PDK and tool environment produced by scripts/setup-env.sh.
# shellcheck shell=bash
_serdes_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDK="ihp-sg13g2"
# shellcheck source=scripts/klt-lib.sh
. "${_serdes_repo}/scripts/klt-lib.sh"
_pdk_root="$(pdk_default_root "${_serdes_repo}")"
export PDK_ROOT="${_pdk_root}"
export PATH="${_serdes_repo}/.venv/bin:${PATH}"
unset _serdes_repo _pdk_root
