# Source me:  source scripts/env.sh
# Exports the repo-local PDK and tool environment produced by scripts/setup-env.sh.
# shellcheck shell=bash
_serdes_repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PDK="ihp-sg13g2"
_pdk_dir="$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["extracted_dir"])' "${_serdes_repo}/sim/pdk.json")"
export PDK_ROOT="${_serdes_repo}/.cache/pdk/${_pdk_dir}"
export PATH="${_serdes_repo}/.venv/bin:${PATH}"
unset _serdes_repo _pdk_dir
