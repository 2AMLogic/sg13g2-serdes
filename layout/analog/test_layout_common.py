#!/usr/bin/env python3
"""Validation tests for layout_common.scrub_host_paths (issue #289).

    python3 -I layout/analog/test_layout_common.py

The RX, TX and pad generators all hand their output tree to that one rewrite,
so the rewrite tests run it on a throwaway output tree inside a scratch
checkout (layout_common.REPO is swapped for the scratch root): no committed
record is touched.
"""
import ast
import json
import os
import pathlib
import runpy
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import layout_common as lc

HERE = pathlib.Path(__file__).resolve().parent
GENERATORS = ["rx/gen_rx_cells.py", "tx/gen_tx_core.py", "pads/gen_pad_cells.py"]
PR_GDS = "ihp-sg13g2/libs.ref/sg13g2_pr/gds/sg13g2_pr.gds"
NETLIST = "design/tx/netlists/tx_top.spice"
CACHE = ".cache/pdk/other-pdk/x.gds"             # a checkout path that no PDK_ROOT covers
RELEASE = ".cache/pdk/IHP-Open-PDK-0.3.0"        # where scripts/setup-env.sh puts the PDK
OUT_REL = "layout/analog/pads/records/2038-01-19-abc1234"
ENV = object()                                   # pdk_root=ENV: called without it, so $PDK_ROOT is read


def nested_text(gds, netlist, cache):
    """A JSON report in a format of the generators' own: indent 3, key order
    unsorted, no final newline."""
    return f'{{\n   "gds": "{gds}",\n   "netlist": "{netlist}",\n   "cache": "{cache}"\n}}'


def rewrite(tmp, pdk="checkout/" + RELEASE, out="checkout/" + OUT_REL, pdk_root="pdk", env=None):
    """Build the scratch tree, run the shared rewrite on it, check what every
    scenario must hold, and -> (compose request dict, nested report text).

    Scratch layout: <tmp>/checkout is the checkout and <tmp>/elsewhere a path
    no root covers; pdk and out locate the PDK the record cites and the output
    tree, relative to <tmp>. pdk_root is what the rewrite is told ("pdk": the
    cited PDK; "pdk/": the same with a trailing slash; ENV: called without it)
    and env the $PDK_ROOT exported for the call (None: unset; "pdk": the
    cited PDK).
    """
    scrub = lc.scrub_host_paths
    tmp, repo = pathlib.Path(tmp), pathlib.Path(tmp) / "checkout"
    pdk, out, elsewhere = tmp / pdk, tmp / out, tmp / "elsewhere/x.gds"
    cache = str(repo / CACHE)
    req_path = out / "pad_esd/compose.request.json"
    req_path.parent.mkdir(parents=True)
    with open(req_path, "w") as f:
        json.dump({"schema": "klt.gen_compose.request/1", "netlist": str(repo / NETLIST),
                   "blocks": [{"id": "Rsp", "generator_report": {"gds_path": str(out / "pad_esd/Rsp.gds")}},
                              {"id": "DHp", "cell": {"gds_path": str(pdk / PR_GDS), "cell_name": "diodevdd_2kv"}}],
                   "notes": [cache, str(elsewhere)],
                   "options": {"cell_name": "pad_esd", "output": str(out / "pad_esd.gds")}}, f, indent=1)
    nested_path = out / "pad_esd/deep/klt.report.json"
    nested_path.parent.mkdir(parents=True)
    nested_path.write_text(nested_text(pdk / PR_GDS, repo / NETLIST, cache))
    # records that must come back byte-identical: a binary and a text record
    # carrying the same host paths, and a JSON report with CRLF line endings
    # and no host path, so that only its formatting is at stake
    untouched = {out / "pad_esd.gds": b"\x00\x06\x00\x02" + str(out).encode() + b"\x00\x00",
                 out / "pad_esd/notes.txt": f"netlist {repo / NETLIST}\npdk {pdk / PR_GDS}\n".encode(),
                 out / "pad_esd/crlf.report.json": b'{\r\n   "gds": "libs.ref/x.gds"\r\n}'}
    for path, data in untouched.items():
        path.write_bytes(data)

    saved_env = os.environ.get("PDK_ROOT")
    if env is None:
        os.environ.pop("PDK_ROOT", None)
    else:
        os.environ["PDK_ROOT"] = "" if env == "" else str(pdk)
    saved_repo, lc.REPO = lc.REPO, str(repo)
    try:
        root = {ENV: None, "pdk": str(pdk), "pdk/": str(pdk) + "/"}.get(pdk_root, pdk_root)
        if root is None:
            scrub(str(out))
        else:
            scrub(str(out), root)
    finally:
        lc.REPO = saved_repo
        if saved_env is None:
            os.environ.pop("PDK_ROOT", None)
        else:
            os.environ["PDK_ROOT"] = saved_env

    for path, data in untouched.items():
        assert path.read_bytes() == data, f"{path.name} is not byte-identical"
    text = nested_path.read_text()
    assert text.startswith('{\n   "gds": "') and not text.endswith("\n"), f"nested JSON reformatted: {text!r}"
    return json.loads(req_path.read_text()), text


def assert_pad_convention(tmp, req, nested):
    """What a set PDK_ROOT yields, wherever the PDK lives and wherever the
    output tree sits: ./ for the output dir, $PDK_ROOT for the PDK, <repo>
    for the rest of the checkout, nothing for a path no root covers."""
    assert req["options"]["output"] == "./pad_esd.gds"
    assert req["blocks"][0]["generator_report"]["gds_path"] == "./pad_esd/Rsp.gds"
    assert req["blocks"][1]["cell"]["gds_path"] == "$PDK_ROOT/" + PR_GDS
    assert req["netlist"] == "<repo>/" + NETLIST
    assert req["notes"] == ["<repo>/" + CACHE, str(pathlib.Path(tmp) / "elsewhere/x.gds")]
    assert nested == nested_text("$PDK_ROOT/" + PR_GDS, "<repo>/" + NETLIST, "<repo>/" + CACHE)


def test_pdk_inside_the_checkout():
    """The worker layout (scripts/setup-env.sh): PDK_ROOT sits under the
    checkout, so it has to be rewritten before the checkout root."""
    with tempfile.TemporaryDirectory() as tmp:
        assert_pad_convention(tmp, *rewrite(tmp))


def test_external_pdk():
    with tempfile.TemporaryDirectory() as tmp:
        assert_pad_convention(tmp, *rewrite(tmp, pdk="ext-pdk"))


def test_output_dir_takes_precedence_over_pdk_root_and_checkout():
    """A path under all three roots (the output tree inside the PDK root)
    belongs to the output dir."""
    with tempfile.TemporaryDirectory() as tmp:
        assert_pad_convention(tmp, *rewrite(tmp, out="checkout/" + RELEASE + "/out"))


def test_unset_pdk_root():
    """No $PDK_ROOT exported: only the output dir and the checkout are rewritten."""
    with tempfile.TemporaryDirectory() as tmp:
        ext = pathlib.Path(tmp) / "ext-pdk"
        req, nested = rewrite(tmp, pdk="ext-pdk", pdk_root=ENV, env=None)
        assert req["options"]["output"] == "./pad_esd.gds"
        assert req["netlist"] == "<repo>/" + NETLIST
        assert req["blocks"][1]["cell"]["gds_path"] == str(ext / PR_GDS)
        assert nested == nested_text(ext / PR_GDS, "<repo>/" + NETLIST, "<repo>/" + CACHE)


def test_empty_pdk_root_is_ignored():
    """PDK_ROOT="" is not a root: an empty pattern puts $PDK_ROOT between every character."""
    with tempfile.TemporaryDirectory() as tmp:
        req, nested = rewrite(tmp, pdk="ext-pdk", pdk_root="", env="")
        assert "$PDK_ROOT" not in json.dumps(req) + nested
        assert req["options"]["output"] == "./pad_esd.gds"
        assert req["blocks"][1]["cell"]["gds_path"] == str(pathlib.Path(tmp) / "ext-pdk" / PR_GDS)


def test_pdk_root_is_read_from_the_environment():
    """The generators call scrub_host_paths(out) alone."""
    with tempfile.TemporaryDirectory() as tmp:
        req, _ = rewrite(tmp, pdk_root=ENV, env="pdk")
        assert req["blocks"][1]["cell"]["gds_path"] == "$PDK_ROOT/" + PR_GDS


def test_trailing_slash_on_the_pdk_root():
    """`export PDK_ROOT=/x/pdk/` must not give "$PDK_ROOTihp-sg13g2/..."."""
    with tempfile.TemporaryDirectory() as tmp:
        req, _ = rewrite(tmp, pdk_root="pdk/")
        assert req["blocks"][1]["cell"]["gds_path"] == "$PDK_ROOT/" + PR_GDS


def test_relative_pdk_root():
    with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"PDK_ROOT": "."}):
        # klt reports an absolute source_gds. The pad generator builds its own lib_block.
        pad = runpy.run_path(str(HERE / "pads/gen_pad_cells.py"))
        block = pad["lib_block"]("DHp", "diodevdd_2kv", [])
        record = pathlib.Path(tmp) / "compose.request.json"
        data = {"dbu_um": 0.001, "note": "v0.9.0", "output": "./pad.gds",
                "source_gds": str(pathlib.Path.cwd() / PR_GDS), "blocks": [block]}
        record.write_text(json.dumps(data))
        lc.scrub_host_paths(tmp)
        data["source_gds"] = block["cell"]["gds_path"] = "$PDK_ROOT/" + PR_GDS
        assert json.loads(record.read_text()) == data


def test_root_boundaries():
    with tempfile.TemporaryDirectory() as tmp:
        repo, pdk, out = (tmp + "/" + name for name in ("checkout", "pdk", "out"))
        os.mkdir(out)
        record = pathlib.Path(out) / "paths.json"
        siblings = [pdk + "-old/cell.gds", out + "-backup/rx.gds", repo + "2/design",
                    "/unrelated" + pdk + "/cell.gds"]
        record.write_text(json.dumps([out, pdk, repo, *siblings]))
        with patch.object(lc, "REPO", repo):
            lc.scrub_host_paths(out, pdk)
        assert json.loads(record.read_text()) == [".", "$PDK_ROOT", "<repo>", *siblings]


def test_json_escaped_roots_and_diagnostics():
    with tempfile.TemporaryDirectory() as tmp:
        pdk = tmp + '/fondería "A"'
        out = tmp + "/résultats🧪"
        os.mkdir(out)
        record = pathlib.Path(out) / "report.json"

        def report(source_root, output_root):
            data = {pdk: [source_root + "/cell.gds", output_root + "/cell.gds"],
                    "note": f"read from {source_root}/cell.gds; output {output_root}/cell.gds"}
            # Exercise both generator-default Unicode escapes and alternate legal
            # spellings in the path suffix. Keep the original key and CRLF layout.
            return (json.dumps(data, indent=3).replace("cell.gds", r"\u0063ell.gds")
                    .replace("/", r"\/").replace("\n", "\r\n").encode())

        record.write_bytes(report(pdk, out))
        lc.scrub_host_paths(out, pdk)
        assert record.read_bytes() == report("$PDK_ROOT", ".")


def test_filesystem_root_as_pdk():
    with tempfile.TemporaryDirectory() as tmp:
        record = pathlib.Path(tmp) / "paths.json"
        record.write_text(json.dumps([tmp, "/", "/cells/gds", "0.001"]))
        lc.scrub_host_paths(tmp, "/")
        assert json.loads(record.read_text()) == [".", "$PDK_ROOT", "$PDK_ROOT/cells/gds", "0.001"]


def test_repo_is_the_checkout_root():
    """The TX defect was a wrong number of parents: two give layout/, which
    holds no design/ netlist to rewrite."""
    repo = pathlib.Path(lc.REPO)
    assert (repo / "layout/analog/layout_common.py").is_file(), repo
    assert (repo / "design/tx/netlists/tx_top.spice").is_file(), repo


def test_every_generator_calls_the_shared_rewrite():
    """No generator keeps a private rewrite: each calls scrub_host_paths, and
    neither placeholder appears as a string outside layout_common."""
    for rel in GENERATORS:
        tree = ast.parse((HERE / rel).read_text(), rel)
        called = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                     and n.func.id == "scrub_host_paths" for n in ast.walk(tree))
        assert called, f"{rel} does not call scrub_host_paths"
        private = [n.value for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and n.value in ("<repo>", "$PDK_ROOT")]
        assert not private, f"{rel} rewrites host paths itself: {private}"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
