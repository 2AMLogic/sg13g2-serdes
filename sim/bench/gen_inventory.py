#!/usr/bin/env python3
"""Generate verification/testbench-inventory.json (T1 item 9) from sim/bench/benches.json.

    python3 -I sim/bench/gen_inventory.py            # rewrite the inventory
    python3 -I sim/bench/gen_inventory.py --check    # exit 1 if the committed file differs

The inventory is derived, never hand-edited, so it cannot drift from the bench files.
Each bench contributes one testbench entry per request file (analog) or per cocotb
test module (digital), each with its own cold-start command. Cold starts are
local_only: they need klt, jq, iverilog and a cocotb uvx environment, which the CI
runner does not provision, so `--attest 9 --check` in CI re-hashes the files and
carries the committed outcome (re-run with --attest 9 -o on a provisioned host).
test module (digital), each with its own cold-start command.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
OUT = REPO / "verification" / "testbench-inventory.json"


def build():
    man = json.loads((REPO / "sim/bench/benches.json").read_text())
    pdk = json.loads((REPO / man["pdk"]).read_text())
    tools = json.loads((REPO / "sim/toolchain.json").read_text())
    rtl = json.loads((REPO / "layout/tools.json").read_text())
    lock = json.loads((REPO / "reuse.lock.json").read_text())["imports"][0]
    klt = (REPO / "scripts/klt-pin.env").read_text().split("=")[1].strip()
    benches = []
    for b in man["benches"]:
        if b["partition"] == "digital":
            paths = [(f"rtl/tests/test_{b['rtl_bench']}.py", ["scripts/run-bench.sh", b["id"]])]
        else:
            paths = [(r, ["scripts/run-bench.sh", b["id"], "--request", r]) for r in b["requests"]]
        for path, argv in paths:
            benches.append({"path": path, "cold_start": {"argv": argv, "timeout_s": 300, "local_only": True}})
    benches.append({"path": "sim/bench/benches.json",
                    "cold_start": {"argv": ["scripts/run-bench.sh", "--list"], "local_only": True}})
    return {
        "schema_version": 1,
        "kind": "t1-attestation-inventory",
        "t1_item": 9,
        "description": (
            "Testbenches against the PROPOSED draft spec rows (#2, not ratified) and DR-001 to DR-004. "
            "Cold start = scripts/run-bench.sh <id>: analog benches validate the klt sim request and "
            "expand the declared corner set (no PDK, no fleet); digital benches run the cocotb bench. "
            "The full corner grid is scripts/run-bench.sh <id> --run (klt sim, batch fleet). "
            "No bench output is a measurement. Rows without a bench are listed in unbenched_rows."),
        "testbenches": benches,
        "pins": {
            "pdk": {"name": "ihp-sg13g2",
                    "revision": f"{pdk['source']} {pdk['release_tag']} sha256:{pdk['tarball_sha256']}"},
            "tools": {
                "klt": klt,
                "ngspice_min": tools["ngspice_min"],
                "harness": f"{lock['from']}@{lock['commit']}",
                "cocotb": rtl["cocotb"]["version"],
                "icarus": rtl["icarus"]["version_prefix"],
            },
        },
        "unbenched_rows": [{"row": r["row"], "issue": r["issue"]} for r in man["unbenched_rows"]],
    }


def main():
    text = json.dumps(build(), indent=2) + "\n"
    if "--check" in sys.argv:
        sys.exit(0 if OUT.exists() and OUT.read_text() == text else 1)
    OUT.write_text(text)


if __name__ == "__main__":
    main()
