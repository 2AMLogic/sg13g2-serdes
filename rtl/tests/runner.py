"""Build one RTL module with Icarus and run its cocotb bench.

Usage: runner.py TEST_MODULE TOPLEVEL SOURCE[,SOURCE...] [NAME=VALUE ...]
(called by rtl/tests/run.sh; NAME=VALUE are Verilog parameters). A SOURCE is
relative to rtl/ unless absolute. Environment: BUILD_TAG suffixes the build
directory, RUN_DEFINES is a comma list of Verilog `define names (gate-level run).
"""
import os
import sys
from pathlib import Path

from cocotb_tools.runner import get_results, get_runner

here = Path(__file__).resolve().parent
root = here.parents[1]
test_module, top, srcs = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
params = {k: int(v) for k, v in (a.split("=") for a in sys.argv[4:])}

tag = os.environ.get("BUILD_TAG", "")
defines = {d: 1 for d in os.environ.get("RUN_DEFINES", "").split(",") if d}
build_dir = here / "sim_build" / (test_module + tag)
r = get_runner("icarus")
r.build(
    sources=[root / "rtl" / s for s in srcs],
    hdl_toplevel=top,
    parameters=params,
    defines=defines,
    build_args=["-g2005"],
    timescale=("1ns", "1ps"),
    build_dir=build_dir,
    always=True,
)
xml = r.test(
    hdl_toplevel=top,
    test_module=test_module,
    test_dir=here,
    build_dir=build_dir,
    results_xml=build_dir / "results.xml",
)
total, failed = get_results(xml)
print(f"runner: {test_module}: {total - failed}/{total} tests passed")
sys.exit(1 if failed else 0)
