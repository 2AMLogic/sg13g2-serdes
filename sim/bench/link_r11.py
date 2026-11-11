#!/usr/bin/env python3
"""Cold-start entry for spec row R11 (issue #93): python3 -I sim/bench/link_r11.py [--quick] [--corners ...]
Thin wrapper so the inventory lists one file per bench; the model lives in link_bench.py."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import link_bench  # noqa: E402

if __name__ == "__main__":
    sys.exit(link_bench.main(["r11"] + sys.argv[1:]))
