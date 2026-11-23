# shellcheck shell=bash
# Shared PDK-free checks. Call from the repository root with repo-relative paths.
erc_check_hash() {
  local file=$1 expected=$2 digest
  if ! digest=$(sha256sum < "$file") || [[ "sha256:${digest%% *}" != "$expected" ]]; then
    echo "ERC input drift: $file does not match the recorded hash $expected" >&2
    return 3
  fi
}

erc_check_inputs() {
  local report=$1 gds=$2 gds_hash spec_hash
  if ! jq -e '.erc_status == "clean"' "$report" >/dev/null; then
    echo "ERC report $report must have erc_status clean" >&2
    return 1
  fi
  if ! jq -e --arg gds "$gds" '.file.scope == "repo" and .file.path == $gds' "$report" >/dev/null; then
    echo "ERC input drift: $report must name the newest routed GDS at $gds" >&2
    return 3
  fi
  if ! jq -e '.spec == "erc.spec.json"' "$report" >/dev/null; then
    echo "ERC input drift: $report must name the archived erc.spec.json" >&2
    return 3
  fi
  gds_hash=$(jq -er '.provenance.input.content_hash' "$report") || return 1
  spec_hash=$(jq -er '.provenance.spec.content_hash' "$report") || return 1
  erc_check_hash "$gds" "$gds_hash" || return $?
  erc_check_hash layout/erc/digital.erc.json "$spec_hash" || return $?
  erc_check_hash "${report%/*}/erc.spec.json" "$spec_hash"
}
