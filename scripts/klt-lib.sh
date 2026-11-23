# klt-lib.sh -- shared klt/PDK environment preflight (sourced).
# One copy of the jq/uvx preflight, the pinned klt runner
# (layout/toolchain.json via a throwaway uvx env), the $PDK_ROOT fallback
# (sim/pdk.json -> .cache/pdk), the PDK_ROOT/PDK exports, latest_record_dir
# (the newest dated record directory), and reserve_record_dir, the exclusive
# record-directory reservation every regen writer makes before its first record
# write (#208, #219). The per-flow checks -- which tool the flow runs and which
# PDK sentinel it needs -- stay with the caller through require_tool /
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

latest_record_dir() { # latest_record_dir <records-dir> -- newest dated record dir
  ls -d "$1"/*/ 2>/dev/null | sort | tail -1 | sed 's:/$::'
}

pdk_default_root() { # pdk_default_root <repo-root> -- the $PDK_ROOT fallback
  # return (not exit): env.sh sources this library and must survive the refusal.
  # Exit-code contract is unchanged: the caller turns the non-zero into exit 3.
  local v
  v="$(jq -r .extracted_dir "$1/sim/pdk.json")" || return 3
  [ -n "$v" ] && [ "$v" != null ] || return 3
  echo "$1/.cache/pdk/$v"
}

reserve_record_dir() { # reserve_record_dir <dest> <diag-prefix> [occupied-exit]
  # uutils mkdir can report success to both racing callers. Read the mkdir
  # syscall result directly so only the writer that created the record proceeds.
  # An occupied destination exits 1, or the caller's third argument when it
  # must keep another status (the analog writers' historical 2, #228); every
  # other filesystem error keeps the distinct mkdir diagnostic and exits 1.
  # A trailing-slash destination (the TX wrapper takes caller-supplied output
  # directories) reserves the final directory component; diagnostics print the
  # argument exactly as the caller passed it.
  python3 -I - "$1" "$2" "${3:-1}" <<'PY'
import os
import sys

dest, prefix, occupied = sys.argv[1], sys.argv[2], int(sys.argv[3])
target = dest.rstrip("/") or "/"
try:
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    try:
        os.mkdir(target)
    except FileExistsError:
        print(f"{prefix}: {dest} exists (records are append-only)", file=sys.stderr)
        sys.exit(occupied)
except OSError as error:
    sys.exit(f"{prefix}: mkdir: {error}")
PY
}
