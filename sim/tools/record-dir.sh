# record-dir.sh -- name and reserve an append-only sim record directory (sourced).
#
# The sim-side half of the reservation: it builds the record id
# `<UTC yyyymmdd-HHMMSS>-<short HEAD SHA>` plus the caller's optional set
# suffix, then delegates the exclusive creation of records/<id>/ to the one
# reserve_record_dir primitive in scripts/klt-lib.sh (#244) -- a python
# os.mkdir that reads the mkdir(2) result directly, so only the launch that
# won the creation proceeds even where uutils `mkdir` 0.10.0 reports success
# to both racers (sim/tools/record-dir-race-investigation.md). The `.reserved`
# marker this file used to create as a second, independent claim retired with
# the `mkdir(1)` call it guarded: it existed to catch exactly the uutils false
# success that the investigation's os.mkdir control measured at zero
# occurrences, so it added no exclusivity on top of the primitive.
# A same-second relaunch (or the retry of a failed run) therefore refuses
# instead of overwriting the stderr and exit logs already saved there
# (issue #202): records are append-only evidence. Callers exit 3 (this
# repo's preflight refusal) when reservation fails.
#
# Needs $REPO_DIR (the repo root, as set by the sourcing runner).
# shellcheck shell=bash
# shellcheck source=../../scripts/klt-lib.sh
. "${REPO_DIR}/scripts/klt-lib.sh"

reserve_sim_record_dir() { # reserve_sim_record_dir <records-root> [id-suffix]
  # Print the reserved directory path on stdout, or return 1 (nothing on
  # stdout) when it cannot be reserved -- a same-second launch already owns
  # the id, or the path is not creatable. The refusal diagnostic is
  # reserve_record_dir's, under the `record-dir:` prefix.
  local id out
  id="$(date -u +%Y%m%d-%H%M%S)-$(git -C "${REPO_DIR}" rev-parse --short HEAD)${2:-}"
  out="${1%/}/${id}"
  reserve_record_dir "${out}" "record-dir" || return 1
  printf '%s\n' "${out}"
}
