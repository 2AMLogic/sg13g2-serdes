# Source me:  source scripts/env.sh
# Exports the repo-local PDK and tool environment produced by scripts/setup-env.sh.
# shellcheck shell=bash
_serdes_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDK="ihp-sg13g2"
export PDK_ROOT="${_serdes_repo}/.cache/pdk/IHP-Open-PDK-0.3.0"
export PATH="${_serdes_repo}/.venv/bin:${PATH}"
unset _serdes_repo
