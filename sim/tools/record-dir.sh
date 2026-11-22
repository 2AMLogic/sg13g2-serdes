# record-dir.sh -- name and reserve an append-only sim record directory (sourced).
#
# One copy of what sim/rx, sim/tx and sim/smoke each used to build: the record
# id `<UTC yyyymmdd-HHMMSS>-<short HEAD SHA>` plus the caller's optional set
# suffix, and the creation of records/<id>/. The record directory is created by
# a single exclusive `mkdir`, so the first launch of a given second owns the
# record and a same-second relaunch (or the retry of a failed run) refuses
# instead of overwriting the stderr and exit logs already saved there
# (issue #202): records are append-only evidence. Callers exit 3 (this repo's
# preflight refusal) when reservation fails.
#
# Needs $REPO_DIR (the repo root, as set by the sourcing runner).
# shellcheck shell=bash

reserve_record_dir() { # reserve_record_dir <records-root> [id-suffix]
  # Print the reserved directory path on stdout, or return 1 (nothing on
  # stdout) when it cannot be reserved -- a same-second launch already owns
  # the id, or the path is not creatable.
  local id out
  id="$(date -u +%Y%m%d-%H%M%S)-$(git -C "${REPO_DIR}" rev-parse --short HEAD)${2:-}"
  out="${1%/}/${id}"
  mkdir -p -- "$1" || { echo "record-dir: cannot create records root '${1}'" >&2; return 1; }
  if ! mkdir -- "${out}" 2>/dev/null; then
    if [ -e "${out}" ]; then
      echo "record-dir: '${out}' already exists -- a same-second launch owns this id; records are append-only, nothing was changed (rerun in a later second)" >&2
    else
      echo "record-dir: cannot create '${out}'" >&2
    fi
    return 1
  fi
  # Second, independent exclusive claim inside the directory (noclobber `>`
  # is O_EXCL): if two launches ever both get past the mkdir above, only the
  # one that creates .reserved proceeds; the other refuses before `klt sim`.
  if ! ( set -C; printf '%s\n' "$$" > "${out}/.reserved" ) 2>/dev/null; then
    echo "record-dir: '${out}' is already claimed by another launch (.reserved exists); records are append-only, nothing was changed" >&2
    return 1
  fi
  printf '%s\n' "${out}"
}
