#!/usr/bin/env bash
# The CI gate. .github/workflows/ci.yml and package.json (check:ci, test, lint)
# both run this script, so local and CI checks cannot diverge.
#   scripts/check-ci.sh [json|links|fresh|harness|signoff|all]   (default: all)
#   scripts/check-ci.sh --regen    re-attest items 1, 9 and 10, refresh their manifest
#                                  content_hash pins, regenerate the committed signoff record
set -uo pipefail
cd "$(dirname "$0")/.." || exit 1
# shellcheck source=scripts/erc-fresh-lib.sh
. scripts/erc-fresh-lib.sh
# The klt pin lives in exactly one place: layout/toolchain.json's klt_install.
KLT_VERSION=$(jq -r '.klt_install // empty' layout/toolchain.json)
KLT_VERSION=${KLT_VERSION#klayout-tools==}
[ -n "$KLT_VERSION" ] \
  || { echo "::error file=layout/toolchain.json::klt_install missing or empty" >&2; exit 1; }

MANIFEST=manifests/sg13g2-serdes.json
TIERS=manifests/design-evidence-tiers.md
RECORD=manifests/sg13g2-serdes.signoff.json
ITEM10_INVENTORY=manifests/evidence/item10.inventory.json
ITEM10_ENVELOPE=manifests/evidence/item10.json
ITEM9_INVENTORY=verification/testbench-inventory.json
ITEM9_ENVELOPE=manifests/evidence/item9.json
ITEM1_INVENTORY=design/inventory.item1.json
ITEM1_ENVELOPE=manifests/evidence/item1.json

klt_signoff() {
  uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
    --manifest "$MANIFEST" --tiers-doc "$TIERS" --format json
}

# refresh_pin <t1-item-id> <envelope> -- rewrite evidence[<id>].content_hash in
# $MANIFEST to the value the grader hash_checks it against.
#
# That value is the envelope's own provenance.input.content_hash, which is NOT
# always the sha256 of the envelope's `source` file: for an inventory that
# declares `sources` (item 1 does), klt 0.9.0 renders a multi-input provenance
# whose content_hash is an aggregate over every declared path. Reading the pin
# back out of the envelope therefore keeps items 1, 9 and 10 on one code path
# and cannot go stale when an inventory gains or loses entries.
refresh_pin() {
  local id=$1 envelope=$2 want tmp
  want=$(jq -er '.provenance.input.content_hash' "$envelope") || {
    echo "::error file=$envelope::no provenance.input.content_hash to pin" >&2; return 1; }
  jq -e --arg id "$id" '(.evidence // {}) | has($id)' "$MANIFEST" >/dev/null || {
    echo "::error file=$MANIFEST::no evidence[\"$id\"] entry to pin" >&2; return 1; }
  tmp=$(mktemp)
  if jq --arg id "$id" --arg h "$want" '.evidence[$id].content_hash = $h' "$MANIFEST" > "$tmp"; then
    mv "$tmp" "$MANIFEST"
  else
    rm -f "$tmp"; echo "::error file=$MANIFEST::could not rewrite evidence[\"$id\"].content_hash" >&2; return 1
  fi
}

check_json() {
  local rc=0 f n=0
  while IFS= read -r f; do
    n=$((n + 1))
    jq empty "$f" 2>/dev/null || { echo "::error file=$f::invalid JSON"; rc=1; }
  done < <(git ls-files 'sim/*.json' 'sim/**/*.json' 'manifests/*.json' \
             reuse.lock.json layout/toolchain.json 2>/dev/null | sort -u)
  echo "json: validated $n file(s)"
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
  local bench_install
  bench_install=$(python3 -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["bench_install"])' \
                    layout/toolchain.json) || {
    echo "::error file=layout/toolchain.json::cannot read bench_install" >&2; return 1; }
  [[ -n "${bench_install}" ]] || {
    echo "::error file=layout/toolchain.json::bench_install is empty" >&2; return 1; }
  echo "harness: sim/bench/test_link_bench.py under ${bench_install}"
  uv run --no-project --with "${bench_install}" -- \
    python -I sim/bench/test_link_bench.py || {
    echo "::error file=sim/bench/test_link_bench.py::bench self-test failed" >&2; return 1; }
}

# check_fresh -- the committed evidence records still describe the committed
# artifacts they name, on six axes that need only jq, sha256sum, cmp and
# python3 (no klt, no openroad, no yosys, nothing under PDK_ROOT):
#   1. rtl/synth/<top>.synth.json .netlist_sha256 == sha256sum of the committed
#      gate-level netlist (the want/got block check-synth-fresh.sh runs behind
#      synth_env).
#   2. newest layout/digital/records/*/report.json
#      .provenance.input.content_hash (sha256: prefix stripped) == that same
#      .netlist_sha256. This is the seam issue #151 slipped through: klt
#      signoff grades each envelope against its own cited artifact, so a
#      record built from a superseded netlist still graded met.
#   3. newest layout/digital/lvs-records/*/lvs.report.json
#      .environment.reference_sha256 == sha256sum of the newest P&R record's
#      post-route netlist -- mirrors check-lvs-fresh.sh, which compares
#      against the newest place-and-route record, not the path the LVS
#      report's own reference field names (a newer P&R record makes LVS stale).
#   4. same report's .environment.layout_sha256 == sha256sum of
#      <top>.gate.spice committed in that same lvs-record dir.
#   5. every committed sim deck and `klt sim` request under the sim/rx and
#      sim/bench r6_*/r20_* patterns is byte-identical to what its generator
#      emits (fresh_sim_decks below). A parsed JSON compare is not enough:
#      record manifests pin *.request.json by sha256, so key order and
#      indentation are part of the contract.
#   6. item 11.digital cites the newest clean ERC report. Its GDS path and
#      hash match the newest P&R record, and its spec hash matches both the
#      canonical supply spec and the archived copy that signoff reads.
# This is the PDK-free subset of check-pnr-fresh.sh / check-lvs-fresh.sh /
# check-erc-fresh.sh; they stay the full local gates (the liberty/deck axis
# hashes a file under PDK_ROOT and remains local-only; the ERC local gate
# additionally re-runs klt erc --check over the pinned klt).
# A missing record or artifact fails rather than passes: records are
# committed, so their absence is a repo defect -- exit 0 means verified,
# never skipped (.loom/docs/ci-principles.md rule 6).
# Newest-record selection uses git ls-files (committed state, not worktree
# residue) and is spelled locally because pnr_latest_record reads $PNR_RECORDS
# from pnr_env, whose require_tool openroad exits 3 on this runner.
# CHECK_FRESH_PNR_RECORD / CHECK_FRESH_LVS_RECORD / CHECK_FRESH_ERC_RECORD
# override the newest-record selection for negative testing only; CI never
# sets them.
#
# fresh_sim_decks -- axis 5 of check_fresh (issue #204): the committed sim
# decks and `klt sim` requests are generated artifacts -- sim/rx/{ctle_ac,
# ctle_op,pad_ac,latch_regen} and sim/bench/r{6,20}_*, 14 files from
# sim/rx/tools/gen_requests.py and sim/bench/gen_r6_r20.py -- and nothing
# else in CI re-derives them, so a generator edit could land green with the
# committed decks stale. Stage working-tree copies of both generators, the
# sim/tools Python support modules and both exported netlist directories in a
# scratch tree at repository-relative paths (the generators locate their
# inputs relative to their own script), leave the generated outputs absent,
# run each default entry point with python3 -I (sim/rx's --debug changes the
# grid), and compare the generated and checked-in path sets, then each
# matching pair, with cmp. The whole body runs in a subshell so the EXIT trap
# removes the scratch tree on success and failure alike; the checkout itself
# is only ever read, so locally edited generated files survive the check.
fresh_sim_decks() (
  local scratch gen f rc=0 committed generated
  scratch=$(mktemp -d) \
    || { echo "::error::fresh axis 5 (sim decks): cannot create scratch tree"; return 1; }
  trap 'rm -rf "$scratch"' EXIT
  mkdir -p "$scratch/sim/rx/tools" "$scratch/sim/bench" "$scratch/sim/tools" \
           "$scratch/design/rx/netlists" "$scratch/design/tx/netlists" \
    || { echo "::error::fresh axis 5 (sim decks): cannot populate scratch tree"; return 1; }
  cp sim/rx/tools/gen_requests.py "$scratch/sim/rx/tools/" \
    && cp sim/bench/gen_r6_r20.py "$scratch/sim/bench/" \
    && cp design/rx/netlists/*.spice "$scratch/design/rx/netlists/" \
    && cp design/tx/netlists/*.spice "$scratch/design/tx/netlists/" \
    || { echo "::error::fresh axis 5 (sim decks): cannot stage generator inputs"; return 1; }
  for f in sim/tools/*.py; do          # shared support modules; none is fine
    [ -f "$f" ] && cp "$f" "$scratch/sim/tools/"
  done
  for gen in sim/rx/tools/gen_requests.py sim/bench/gen_r6_r20.py; do
    (cd "$scratch" && python3 -I "$gen") \
      || { echo "::error file=$gen::fresh axis 5 (sim decks): generator failed (run it from the repo root for the traceback)"; rc=1; }
  done
  committed=$(git ls-files -- ':(glob)sim/rx/*.sp' ':(glob)sim/rx/*.request.json' \
                          ':(glob)sim/bench/r6_*.sp' ':(glob)sim/bench/r6_*.request.json' \
                          ':(glob)sim/bench/r20_*.sp' ':(glob)sim/bench/r20_*.request.json' | sort)
  generated=$(cd "$scratch" && shopt -s nullglob && for f in sim/rx/*.sp sim/rx/*.request.json \
      sim/bench/r6_*.sp sim/bench/r6_*.request.json \
      sim/bench/r20_*.sp sim/bench/r20_*.request.json; do echo "$f"; done | sort)
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    echo "::error file=$f::fresh axis 5 (sim decks): generator emitted nothing for committed $f"
    rc=1
  done < <(comm -23 <(printf '%s\n' "$committed") <(printf '%s\n' "$generated"))
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    echo "::error file=$f::fresh axis 5 (sim decks): generator output $f has no committed counterpart"
    rc=1
  done < <(comm -13 <(printf '%s\n' "$committed") <(printf '%s\n' "$generated"))
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if [ ! -f "$f" ]; then
      echo "::error file=$f::fresh axis 5 (sim decks): committed $f missing from the checkout"
      rc=1
    elif ! cmp -s "$f" "$scratch/$f"; then
      echo "::error file=$f::fresh axis 5 (sim decks): $f differs from its generator output (regenerate: python3 -I <generator> from the repo root)"
      rc=1
    fi
  done < <(comm -12 <(printf '%s\n' "$committed") <(printf '%s\n' "$generated"))
  return "$rc"
)

check_fresh() {
  local rc=0 top ok synth_report synth_netlist want got
  local prec prec_report rec_hash lrec lvs_report postroute layout_netlist ref_hash
  local erec erc_report
  [ -f rtl/synth/request.json ] || { echo "::error file=rtl/synth/request.json::missing"; return 1; }
  top=$(jq -er '.hdl_toplevel' rtl/synth/request.json 2>/dev/null) \
    || { echo "::error file=rtl/synth/request.json::cannot read .hdl_toplevel"; return 1; }

  # Axis 1: the synthesized netlist is the one its own report describes.
  synth_report="rtl/synth/${top}.synth.json"
  synth_netlist="rtl/synth/${top}_synth.v"
  [ -f "$synth_report" ] || { echo "::error file=$synth_report::missing (run scripts/synth-regen.sh)"; return 1; }
  [ -f "$synth_netlist" ] || { echo "::error file=$synth_netlist::missing (run scripts/synth-regen.sh)"; return 1; }
  want=$(jq -er '.netlist_sha256' "$synth_report" 2>/dev/null) \
    || { echo "::error file=$synth_report::cannot read .netlist_sha256"; return 1; }
  got=$(sha256sum "$synth_netlist" | awk '{print $1}')
  if [ "$want" != "$got" ]; then
    echo "::error file=$synth_netlist::fresh axis 1 (synth): ${top}_synth.v hash $got != $synth_report .netlist_sha256 $want"
    rc=1
  fi

  # Axis 2: the newest place-and-route record was built from that netlist.
  if [ -n "${CHECK_FRESH_PNR_RECORD:-}" ]; then
    prec=$(CDPATH='' cd -- "$CHECK_FRESH_PNR_RECORD" && pwd) || return 1
    prec=${prec#"$PWD"/}
  else
    prec=$(git ls-files 'layout/digital/records/*/report.json' | sed 's:/report\.json$::' | sort | tail -1)
  fi
  prec_report="$prec/report.json"
  [ -n "$prec" ] && [ -f "$prec_report" ] \
    || { echo "::error file=$prec_report::no committed place-and-route record (run scripts/pnr-regen.sh)"; return 1; }
  ok=1
  if rec_hash=$(jq -er '.provenance.input.content_hash' "$prec_report" 2>/dev/null); then
    case $rec_hash in
      sha256:*) rec_hash=${rec_hash#sha256:} ;;
      *)
        echo "::error file=$prec_report::fresh axis 2 (pnr): .provenance.input.content_hash '$rec_hash' has no sha256: prefix"
        ok=0 ;;
    esac
  else
    echo "::error file=$prec_report::fresh axis 2 (pnr): cannot read .provenance.input.content_hash"
    ok=0
  fi
  if [ "$ok" = 1 ] && [ "$rec_hash" != "$want" ]; then
    echo "::error file=$prec_report::fresh axis 2 (pnr): .provenance.input.content_hash $rec_hash != $synth_report .netlist_sha256 $want"
    ok=0
  fi
  [ "$ok" = 1 ] || rc=1

  # Axes 3-4: the newest LVS record against that P&R record and its own
  # committed extraction.
  if [ -n "${CHECK_FRESH_LVS_RECORD:-}" ]; then
    lrec=$CHECK_FRESH_LVS_RECORD
  else
    lrec=$(git ls-files 'layout/digital/lvs-records/*/lvs.report.json' | sed 's:/lvs\.report\.json$::' | sort | tail -1)
  fi
  lvs_report="$lrec/lvs.report.json"
  [ -n "$lrec" ] && [ -f "$lvs_report" ] \
    || { echo "::error file=$lvs_report::no committed LVS record (run scripts/lvs-regen.sh)"; return 1; }

  # Axis 3: the LVS record compared the newest P&R record's post-route netlist.
  postroute="$prec/${top}_postroute.v"
  ok=1
  if ref_hash=$(jq -er '.environment.reference_sha256' "$lvs_report" 2>/dev/null); then
    if [ -f "$postroute" ]; then
      got=$(sha256sum "$postroute" | awk '{print $1}')
      if [ "$ref_hash" != "$got" ]; then
        echo "::error file=$lvs_report::fresh axis 3 (lvs): newest place-and-route record's ${top}_postroute.v hash $got != $lvs_report .environment.reference_sha256 $ref_hash"
        ok=0
      fi
    else
      echo "::error file=$postroute::fresh axis 3 (lvs): newest place-and-route record's post-route netlist missing"
      ok=0
    fi
  else
    echo "::error file=$lvs_report::fresh axis 3 (lvs): cannot read .environment.reference_sha256"
    ok=0
  fi
  [ "$ok" = 1 ] || rc=1

  # Axis 4: the LVS extraction is of the netlist committed beside it.
  layout_netlist="$lrec/${top}.gate.spice"
  ok=1
  if ref_hash=$(jq -er '.environment.layout_sha256' "$lvs_report" 2>/dev/null); then
    if [ -f "$layout_netlist" ]; then
      got=$(sha256sum "$layout_netlist" | awk '{print $1}')
      if [ "$ref_hash" != "$got" ]; then
        echo "::error file=$lvs_report::fresh axis 4 (lvs): $layout_netlist hash $got != $lvs_report .environment.layout_sha256 $ref_hash"
        ok=0
      fi
    else
      echo "::error file=$layout_netlist::fresh axis 4 (lvs): extracted netlist missing from the LVS record dir"
      ok=0
    fi
  else
    echo "::error file=$lvs_report::fresh axis 4 (lvs): cannot read .environment.layout_sha256"
    ok=0
  fi
  [ "$ok" = 1 ] || rc=1

  # Axis 5: the committed sim decks and requests match their generators.
  fresh_sim_decks || rc=1

  # Axis 6: the ERC evidence cited by signoff is clean and current.
  if [ -n "${CHECK_FRESH_ERC_RECORD:-}" ]; then
    erec=$(CDPATH='' cd -- "$CHECK_FRESH_ERC_RECORD" && pwd) || return 1
    erec=${erec#"$PWD"/}
  else
    erec=$(git ls-files 'layout/digital/erc-records/*/erc.report.json' | sed 's:/erc\.report\.json$::' | sort | tail -1)
  fi
  erc_report="$erec/erc.report.json"
  [ -n "$erec" ] && [ -f "$erc_report" ] \
    || { echo "::error file=$erc_report::no committed ERC record (run scripts/erc-regen.sh)"; return 1; }
  erc_check_inputs "$erc_report" "$prec/$top.gds" || rc=1
  if ! jq -e --arg file "$erc_report" --slurpfile report "$erc_report" '
      .evidence["11.digital"] | map(select(.file | startswith("layout/digital/erc-records/"))) |
      length == 1 and .[0].file == $file and
      .[0].content_hash == $report[0].provenance.input.content_hash
    ' "$MANIFEST" >/dev/null; then
    echo "::error file=$MANIFEST::fresh axis 6 (erc): 11.digital must cite $erc_report with its recorded input hash"
    rc=1
  fi

  if [ "$rc" = 0 ]; then
    echo "fresh: 6 axis(es) verified (pnr=$prec lvs=$lrec erc=$erec; sim decks match generators)"
  else
    echo "fresh: FAILED (pnr=$prec lvs=$lrec erc=$erec)" >&2
  fi
  return $rc
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
    echo "::error::fresh klt signoff differs from $RECORD (klt pinned at ${KLT_VERSION} in layout/toolchain.json)"
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
  # Item 9: the inventory is generated from sim/bench/benches.json, and its cold starts
  # are local_only (need klt/jq/iverilog/cocotb), so --check re-hashes and carries them.
  python3 -I sim/bench/gen_inventory.py --check \
    || { echo "::error::$ITEM9_INVENTORY differs from sim/bench/benches.json: python3 -I sim/bench/gen_inventory.py"; return 1; }
  uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
    --attest 9 --inventory "$ITEM9_INVENTORY" --check "$ITEM9_ENVELOPE" --format json >/dev/null \
    || { echo "::error::item 9 attestation drifted or failed: re-attest with scripts/check-ci.sh --regen"; return 1; }
  echo "signoff: item 9 attestation holds"
  # Item 1: the inventory's netlist/synth freshness commands are local_only
  # (they need PDK_ROOT and xschem), so --check re-hashes the sources and
  # carries those command results instead of re-running them.
  uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
    --attest 1 --inventory "$ITEM1_INVENTORY" --check "$ITEM1_ENVELOPE" --format json >/dev/null \
    || { echo "::error::item 1 attestation drifted or failed: re-attest with scripts/check-ci.sh --regen"; return 1; }
  echo "signoff: item 1 attestation holds"
}

case "${1:-all}" in
  --regen)
    # Item 10 first: its hygiene inventory lists this script, so re-attesting it
    # last would miss an edit made in the same change.
    uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
      --attest 10 --inventory "$ITEM10_INVENTORY" -o "$ITEM10_ENVELOPE" --format json >/dev/null \
      || { echo "item 10 attestation failed" >&2; exit 1; }
    python3 -I sim/bench/gen_inventory.py
    uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
      --attest 9 --inventory "$ITEM9_INVENTORY" -o "$ITEM9_ENVELOPE" --format json >/dev/null \
      || { echo "item 9 attestation failed" >&2; exit 1; }
    # Item 1 runs the netlist/synth freshness commands its inventory declares,
    # so this step needs a provisioned local tree (source scripts/env.sh).
    uvx --from "klayout-tools==${KLT_VERSION}" klt signoff \
      --attest 1 --inventory "$ITEM1_INVENTORY" -o "$ITEM1_ENVELOPE" --format json >/dev/null \
      || { echo "item 1 attestation failed (provisioned tree needed: source scripts/env.sh)" >&2; exit 1; }
    # Pins BEFORE the record: the grader reads evidence[*].content_hash, so
    # regenerating the verdict first and pinning second commits a record that
    # still grades the items just re-attested stale_evidence.
    refresh_pin 10 "$ITEM10_ENVELOPE" || exit 1
    refresh_pin 9 "$ITEM9_ENVELOPE" || exit 1
    refresh_pin 1 "$ITEM1_ENVELOPE" || exit 1
    out=$(mktemp); rc=0; klt_signoff > "$out" || rc=$?
    [ "$rc" -eq 0 ] || [ "$rc" -eq 3 ] || { echo "klt signoff exited $rc" >&2; exit 1; }
    mv "$out" "$RECORD" ;;
  json) check_json ;;
  links) check_links ;;
  fresh) check_fresh ;;
  harness) check_harness ;;
  signoff) check_signoff ;;
  all)
    rc=0
    check_json || rc=1
    check_links || rc=1
    check_fresh || rc=1
    check_harness || rc=1
    check_signoff || rc=1
    exit $rc ;;
  *) echo "usage: $0 [json|links|fresh|harness|signoff|all|--regen]" >&2; exit 2 ;;
esac
