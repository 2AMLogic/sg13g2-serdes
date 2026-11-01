#!/usr/bin/env bash
# The CI gate. .github/workflows/ci.yml and package.json (check:ci, test, lint)
# both run this script, so local and CI checks cannot diverge.
#   scripts/check-ci.sh [json|links|harness|signoff|all]   (default: all)
#   scripts/check-ci.sh --regen    re-attest item 10, regenerate the committed signoff record
set -uo pipefail
cd "$(dirname "$0")/.."
# shellcheck source=scripts/klt-pin.env
. scripts/klt-pin.env

MANIFEST=manifests/sg13g2-serdes.json
TIERS=manifests/design-evidence-tiers.md
RECORD=manifests/sg13g2-serdes.signoff.json
ITEM10_INVENTORY=manifests/evidence/item10.inventory.json
ITEM10_ENVELOPE=manifests/evidence/item10.json

klt_signoff() {
  uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
    --manifest "$MANIFEST" --tiers-doc "$TIERS" --format json
}

check_json() {
  local rc=0 f n=0
  while IFS= read -r f; do
    n=$((n + 1))
    jq empty "$f" 2>/dev/null || { echo "::error file=$f::invalid JSON"; rc=1; }
  done < <(git ls-files 'sim/*.json' 'sim/**/*.json' 'manifests/*.json' \
             reuse.lock.json layout/toolchain.json 2>/dev/null | sort -u)
  echo "json: validated $n file(s)"
  # The klt version is pinned in two places (this script's klt-pin.env and the
  # layout/sim flows' toolchain.json); a bump that touches only one must fail here.
  local layout_pin
  layout_pin=$(jq -r '.klt_install // empty' layout/toolchain.json 2>/dev/null)
  if [ "$layout_pin" != "klayout-tools==${KLT_VERSION}" ]; then
    echo "::error file=layout/toolchain.json::klt_install '${layout_pin}' != klayout-tools==${KLT_VERSION} (scripts/klt-pin.env)"
    rc=1
  fi
  return $rc
}

check_links() {
  local rc=0 link target
  while IFS= read -r link; do
    target=${link%%#*}
    [ -z "$target" ] && continue
    [ -e "$target" ] || { echo "::error file=README.md::broken relative link: $link"; rc=1; }
  done < <(grep -oE '\]\([^)]+\)' README.md | sed -E 's/^\]\((.*)\)$/\1/' \
             | grep -vE '^(https?:|mailto:|#)')
  echo "links: README relative links checked"
  return $rc
}

check_harness() {
  echo "harness not present: nothing to self-test yet"
}

check_signoff() {
  local fresh rc=0
  fresh=$(mktemp)
  uvx --from "klayout-tools==${KLT_VERSION}" klt --version || return 1
  klt_signoff > "$fresh" || rc=$?
  # 0 = all T1 items met; 3 = grader ran clean with unmet items. Anything else is a hard error.
  if [ "$rc" -ne 0 ] && [ "$rc" -ne 3 ]; then
    echo "::error::klt signoff exited $rc: manifest or vendored tiers doc is broken"
    return 1
  fi
  if ! cmp -s "$fresh" "$RECORD"; then
    echo "::error::fresh klt signoff differs from $RECORD (klt pinned at ${KLT_VERSION} in scripts/klt-pin.env)"
    echo "Regenerate in the same PR: scripts/check-ci.sh --regen"
    diff <(python3 -m json.tool "$fresh") <(python3 -m json.tool "$RECORD") || true
    return 1
  fi
  echo "signoff: committed record matches klt ${KLT_VERSION}"
  # Item 10 re-attests the hygiene inventory, which lists this script. Its checks
  # must therefore not call `signoff` or `all` (that would recurse).
  uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
    --attest 10 --inventory "$ITEM10_INVENTORY" --check "$ITEM10_ENVELOPE" --format json >/dev/null \
    || { echo "::error::item 10 attestation drifted or failed: re-attest with scripts/check-ci.sh --regen"; return 1; }
  echo "signoff: item 10 attestation holds"
}

case "${1:-all}" in
  --regen)
    uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
      --attest 10 --inventory "$ITEM10_INVENTORY" -o "$ITEM10_ENVELOPE" --format json >/dev/null \
      || { echo "item 10 attestation failed" >&2; exit 1; }
    out=$(mktemp); rc=0; klt_signoff > "$out" || rc=$?
    [ "$rc" -eq 0 ] || [ "$rc" -eq 3 ] || { echo "klt signoff exited $rc" >&2; exit 1; }
    mv "$out" "$RECORD" ;;
  json) check_json ;;
  links) check_links ;;
  harness) check_harness ;;
  signoff) check_signoff ;;
  all)
    rc=0
    check_json || rc=1
    check_links || rc=1
    check_harness
    check_signoff || rc=1
    exit $rc ;;
  *) echo "usage: $0 [json|links|harness|signoff|all|--regen]" >&2; exit 2 ;;
esac
