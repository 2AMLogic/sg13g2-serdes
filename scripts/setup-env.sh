#!/usr/bin/env bash
# setup-env.sh -- bring a fresh clone to a runnable SG13G2 simulation state.
#
#   scripts/setup-env.sh            # fetch + verify PDK, build OSDI, fetch harness, install klt
#   scripts/setup-env.sh --check    # verify only (no network): everything present and loadable
#   source scripts/env.sh           # afterwards: export PDK_ROOT/PDK/PATH for this shell
#
# Everything lands in repo-local, gitignored paths (.cache/, .venv/, sim/harness/).
# Nothing is written to ~/.local, apt, or `uv tool`: the loom worker host is
# shared and host-wide tools are provisioned separately. A tool that is missing
# or below its floor is REPORTED (exit 3), never installed on the host.
#
# Fails closed: any sha256 mismatch (PDK tarball, OpenVAF, libLLVM, harness
# files) removes the offending download and exits 4.
#
# Pins live in: sim/pdk.json, sim/toolchain.json, layout/toolchain.json,
# reuse.lock.json, and sim/tools/build-osdi.sh. This script reads them; it
# does not restate them.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CACHE="${REPO_DIR}/.cache"
CHECK_ONLY=0
case "${1:-}" in
  --check) CHECK_ONLY=1 ;;
  "") ;;
  -h|--help) sed -n '2,19p' "${BASH_SOURCE[0]}"; exit 0 ;;
  *) echo "setup-env.sh: unknown argument '$1'" >&2; exit 2 ;;
esac

die() { echo "setup-env.sh: $*" >&2; exit "${2:-1}"; }

sha256_of() {
  if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
  else die "neither sha256sum nor shasum available -- cannot verify downloads" 3; fi
}

# verify_or_remove <file> <expected-sha> <label>
verify_or_remove() {
  local got
  got="$(sha256_of "$1")"
  if [[ "${got}" != "$2" ]]; then
    echo "setup-env.sh: SHA256 MISMATCH for $3" >&2
    echo "  expected $2" >&2
    echo "  got      ${got}" >&2
    rm -f "$1"
    die "refusing to use an unverified download; removed it." 4
  fi
  echo "setup-env.sh: sha256 OK ($3)"
}

# json_get <file> <python-expression-on-d>
json_get() { python3 -I -c 'import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2]))' "$1" "$2"; }

for tool in python3 curl tar ngspice; do
  command -v "${tool}" >/dev/null 2>&1 \
    || die "'${tool}' not found on PATH. This script does not install host tools; report the gap (worker spec) instead." 3
done

# ---- floors (sim/toolchain.json) -------------------------------------------
NGSPICE_MIN="$(json_get "${REPO_DIR}/sim/toolchain.json" "d['ngspice_min']")"
NGSPICE_VER="$(ngspice --version 2>&1 | sed -n 's/.*ngspice-\([0-9][0-9]*\).*/\1/p' | head -1)"
[[ -n "${NGSPICE_VER}" ]] || die "cannot parse 'ngspice --version'" 3
(( NGSPICE_VER >= NGSPICE_MIN )) \
  || die "ngspice ${NGSPICE_VER} is below the floor ${NGSPICE_MIN} (sim/toolchain.json); not installing on a shared host -- record the gap." 3
python3 -I -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' \
  || die "python3 is below the 3.10 floor (sim/toolchain.json)" 3
echo "setup-env.sh: ngspice ${NGSPICE_VER} (floor ${NGSPICE_MIN}), $(python3 -I -V)"

# ---- PDK (sim/pdk.json) ----------------------------------------------------
PDK_URL="$(json_get "${REPO_DIR}/sim/pdk.json" "d['release_url']")"
PDK_SHA="$(json_get "${REPO_DIR}/sim/pdk.json" "d['tarball_sha256']")"
PDK_DIR_NAME="$(json_get "${REPO_DIR}/sim/pdk.json" "d['extracted_dir']")"
PDK_VARIANT="$(json_get "${REPO_DIR}/sim/pdk.json" "d['variant']")"
PDK_ROOT="${CACHE}/pdk/${PDK_DIR_NAME}"
TARBALL="${CACHE}/dl/${PDK_DIR_NAME}.tar.gz"

if [[ ${CHECK_ONLY} -eq 0 ]]; then
  mkdir -p "${CACHE}/dl" "${CACHE}/pdk"
  if [[ ! -f "${TARBALL}" ]]; then
    echo "setup-env.sh: fetching ${PDK_URL}"
    curl -fsSL -o "${TARBALL}.part" "${PDK_URL}"
    mv "${TARBALL}.part" "${TARBALL}"
  fi
  verify_or_remove "${TARBALL}" "${PDK_SHA}" "$(basename "${TARBALL}")"
  if [[ ! -d "${PDK_ROOT}/${PDK_VARIANT}/libs.tech/ngspice" ]]; then
    rm -rf "${PDK_ROOT}"
    tar -xzf "${TARBALL}" -C "${CACHE}/pdk"
  fi
fi
[[ -d "${PDK_ROOT}/${PDK_VARIANT}/libs.tech/ngspice" ]] \
  || die "PDK not installed at ${PDK_ROOT} -- run scripts/setup-env.sh (without --check)." 3
export PDK_ROOT PDK="${PDK_VARIANT}"

# ---- OSDI models (sim/tools/build-osdi.sh owns its own pins) ---------------
# Exit 5 = built fine, but this host's ngspice is too old to load OSDI v0.4.
# That is reported, not fatal: such hosts run simulations on the batch fleet
# (`klt sim`), and this script never installs a simulator on the host.
LOCAL_OSDI="loadable"
osdi_args=(); [[ ${CHECK_ONLY} -eq 1 ]] && osdi_args=(--check)
"${REPO_DIR}/sim/tools/build-osdi.sh" "${osdi_args[@]}" && osdi_rc=0 || osdi_rc=$?
case "${osdi_rc}" in
  0) ;;
  5) LOCAL_OSDI="NOT loadable by the host ngspice (use 'klt sim --backend batch')" ;;
  *) exit "${osdi_rc}" ;;
esac
echo "setup-env.sh: OSDI models built; local ngspice: ${LOCAL_OSDI}"

# ---- harness (reuse.lock.json, mode "fetched": never committed) ------------
HARNESS_DIR="${REPO_DIR}/sim/harness"
mapfile -t HARNESS_ROWS < <(python3 -I - "${REPO_DIR}/reuse.lock.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for imp in d.get("imports", []):
    for f in imp["files"]:
        print(imp["from"], imp["commit"], f["upstream"], f.get("local", f["upstream"]), f["sha256"])
PY
)
for row in "${HARNESS_ROWS[@]}"; do
  read -r from commit upstream local_path sha <<<"${row}"
  dest="${REPO_DIR}/${local_path}"
  if [[ ${CHECK_ONLY} -eq 0 && ! -f "${dest}" ]]; then
    mkdir -p "$(dirname "${dest}")"
    curl -fsSL -o "${dest}.part" "https://raw.githubusercontent.com/${from}/${commit}/${upstream}"
    mv "${dest}.part" "${dest}"
  fi
  [[ -f "${dest}" ]] || die "${local_path} missing -- run scripts/setup-env.sh (without --check)." 3
  verify_or_remove "${dest}" "${sha}" "${from}@${commit:0:7}:${upstream}"
done

# ---- klt (layout/toolchain.json): repo-local venv, never a host tool -------
KLT_INSTALL="$(json_get "${REPO_DIR}/layout/toolchain.json" "d['klt_install']")"
KLT_SHA="$(json_get "${REPO_DIR}/layout/toolchain.json" "d['klt_last_verified_commit']")"
if [[ ${CHECK_ONLY} -eq 0 && ! -x "${REPO_DIR}/.venv/bin/klt" ]]; then
  command -v uv >/dev/null 2>&1 || die "'uv' not found on PATH; needed to build the repo-local .venv (not installing it)." 3
  uv venv "${REPO_DIR}/.venv"
  uv pip install --python "${REPO_DIR}/.venv/bin/python" "${KLT_INSTALL}"
fi
[[ -x "${REPO_DIR}/.venv/bin/klt" ]] || die ".venv/bin/klt missing -- run scripts/setup-env.sh (without --check)." 3
KLT_ACTUAL="$(python3 -I - "${REPO_DIR}/.venv" <<'PY'
import glob, json, sys
for p in glob.glob(sys.argv[1] + "/lib/python*/site-packages/klayout_tools-*.dist-info/direct_url.json"):
    print(json.load(open(p)).get("vcs_info", {}).get("commit_id", ""))
PY
)"
[[ "${KLT_ACTUAL}" == "${KLT_SHA}" ]] \
  || die "klt in .venv is at '${KLT_ACTUAL:-unknown}', pin is ${KLT_SHA}; remove .venv and re-run." 4
echo "setup-env.sh: klt ${KLT_SHA:0:12} in .venv"

echo
echo "setup-env.sh: OK. Next:  source scripts/env.sh   then   sim/smoke/run_smoke.sh"
