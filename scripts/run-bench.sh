#!/usr/bin/env bash
# run-bench.sh -- cold-start entry point for every shipped testbench (T1 item 9).
#
#   scripts/run-bench.sh --list            bench ids, rows graded, corner set
#   scripts/run-bench.sh <id>              CHECK (default): validate the bench's requests,
#                                          expand the corner set, assert the declared
#                                          measurements exist (analog); run the cocotb
#                                          bench for real (digital). No PDK, no fleet.
#   scripts/run-bench.sh <id> [--run] [--request <path>]
#                                          --request restricts to one of the bench's requests
#   scripts/run-bench.sh link-<row>-*      behavioural DR-002 benches (R8 R11 R12 R13 R15): run for real, locally,
#                                          numpy only; add --quick for a short configuration
#   scripts/run-bench.sh <id> --run        analog only: submit the full corner grid with
#                                          `klt sim --wait-for-capacity 600` (batch fleet
#                                          when KLT_SIM_BACKEND=batch). Needs
#                                          `scripts/setup-env.sh` then `source scripts/env.sh`.
#
# Outputs are simulated figures, never measurements. Multi-corner grids are never
# looped over ngspice by hand: --run goes through `klt sim` only.
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAN="${REPO}/sim/bench/benches.json"
die() { echo "run-bench.sh: $*" >&2; exit "${2:-2}"; }
command -v jq >/dev/null 2>&1 || die "jq not on PATH" 3
[[ $# -ge 1 ]] || die "usage: run-bench.sh --list | <id> [--run]"
if [[ "$1" == "--list" ]]; then
  jq -r '.benches[] | "\(.id)\t\(.partition)\t\(.rows|join(","))\t\(.corner_set)"' "${MAN}"; exit 0
fi
ID="$1"; shift; MODE=check; ONLY=""; QUICK=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --run) MODE="--run" ;;
    --quick) QUICK+=(--quick) ;;
    --strict) QUICK+=(--strict) ;;
    --request) ONLY="${2:-}"; [[ -n "${ONLY}" ]] || die "--request needs a path"; shift ;;
    *) die "unknown argument '$1'" ;;
  esac
  shift
done
B="$(jq -c --arg id "${ID}" '.benches[] | select(.id==$id)' "${MAN}")"
[[ -n "${B}" ]] || die "unknown bench '${ID}' (see --list)"

if [[ "$(jq -r .partition <<<"${B}")" == "behavioural" ]]; then
  # DR-002 behavioural/statistical benches: numpy only, one local process, no fleet. --strict (passed through) exits 3 when a
  # proposed spec threshold is not met (reported, never relaxed).
  command -v python3 >/dev/null 2>&1 || die "python3 not on PATH" 3
  mapfile -t BARGS < <(jq -r '.args[]' <<<"${B}")
  exec python3 -I "${REPO}/$(jq -r .entry <<<"${B}")" "${BARGS[@]}" "${QUICK[@]}"
fi
if [[ "$(jq -r .partition <<<"${B}")" == "digital" ]]; then
  [[ "${MODE}" == "check" ]] || die "--run applies to analog benches; the digital bench always runs"
  exec "${REPO}/rtl/tests/run.sh" "$(jq -r .rtl_bench <<<"${B}")"
fi

command -v klt >/dev/null 2>&1 || die "klt not on PATH (source scripts/env.sh)" 3
want_units="$(jq -r .units_per_request <<<"${B}")"
rc=0
seen=0
while IFS= read -r req; do
  [[ -z "${ONLY}" || "${req}" == "${ONLY}" ]] || continue
  seen=1
  dir="$(dirname "${REPO}/${req}")"; base="$(basename "${req}")"
  if [[ "${MODE}" == "--run" ]]; then
    [[ -n "${PDK_ROOT:-}" ]] || die "PDK_ROOT unset: run scripts/setup-env.sh, then source scripts/env.sh" 3
    ( cd "${dir}" && klt sim --wait-for-capacity 600 "${base}" ); e=$?
    [[ ${e} -eq 0 || ${e} -eq 3 ]] || rc=1   # 3 = a declared limit failed; the report is still complete
    continue
  fi
  out="$(cd "${dir}" && klt sim --dry-run --format json "${base}")" || { echo "run-bench.sh: ${req}: dry-run failed" >&2; rc=1; continue; }
  got="$(jq -r .unit_count <<<"${out}")"
  [[ "${got}" == "${want_units}" ]] || { echo "run-bench.sh: ${req}: expands to ${got} units, bench declares ${want_units}" >&2; rc=1; }
  while IFS= read -r m; do
    jq -e --arg m "${m}" '.measurements[] | select(.name==$m)' "${REPO}/${req}" >/dev/null \
      || { echo "run-bench.sh: ${req}: declared measurement '${m}' missing" >&2; rc=1; }
  done < <(jq -r '.required_measurements[]' <<<"${B}")
  echo "run-bench.sh: ${ID}: ${req} ok (${got} corner units, check only; simulated figures need --run)"
done < <(jq -r '.requests[]' <<<"${B}")
[[ -z "${ONLY}" || ${seen} -eq 1 ]] || die "bench '${ID}' has no request '${ONLY}'"
exit ${rc}
