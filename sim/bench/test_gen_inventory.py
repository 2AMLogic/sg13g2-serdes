#!/usr/bin/env python3
"""Validation tests for sim/bench/gen_inventory.py (issue #271).

    python3 -I sim/bench/test_gen_inventory.py

Each test runs build() against a scratch copy of the manifest inputs, so the
committed verification/testbench-inventory.json is never rewritten.
"""
import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gen_inventory as gi  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
INPUTS = ["sim/bench/benches.json", "sim/pdk.json", "sim/toolchain.json",
          "layout/tools.json", "layout/toolchain.json", "reuse.lock.json"]
SOURCES = [src["path"] for src in
           json.loads((REPO / "sim/bench/benches.json").read_text())["behavioural_sources"]]


def build_with(man=None):
    """build() against a scratch copy of the inputs; returns its dict."""
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for rel in INPUTS + SOURCES:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(REPO / rel, root / rel)
        if man is not None:
            (root / "sim/bench/benches.json").write_text(json.dumps(man))
        saved, gi.REPO = gi.REPO, root
        try:
            return gi.build()
        finally:
            gi.REPO = saved


def manifest():
    return json.loads((REPO / "sim/bench/benches.json").read_text())


def expect_exit(man, *needles):
    try:
        build_with(man)
    except SystemExit as e:
        for needle in needles:
            assert needle in str(e.code), f"{needle!r} not in exit message: {e.code!r}"
        return
    raise AssertionError(f"build() did not exit; expected {needles!r} in the message")


def test_committed_manifest_builds_and_matches_the_inventory():
    got = json.dumps(build_with(), indent=2) + "\n"
    assert got == (REPO / "verification/testbench-inventory.json").read_text()


def test_unknown_bench_id_is_named_and_exits():
    man = manifest()
    man["behavioural_sources"][0]["bench"] = "link-r99-bogus"
    expect_exit(man, "link-r99-bogus", "not a benches[].id")


def test_missing_source_path_is_named_and_exits():
    man = manifest()
    man["behavioural_sources"][1]["path"] = "sim/bench/nope.py"
    expect_exit(man, "sim/bench/nope.py", "does not exist")


def test_non_behavioural_partition_is_rejected():
    man = manifest()
    man["behavioural_sources"][2]["bench"] = "tx-link"
    expect_exit(man, "tx-link", "not 'behavioural'")


def test_empty_behavioural_sources_still_builds():
    man = manifest()
    man["behavioural_sources"] = []
    inv = build_with(man)
    starts = [tb["cold_start"]["argv"] for tb in inv["testbenches"]]
    assert ["scripts/run-bench.sh", "--list"] in starts


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
