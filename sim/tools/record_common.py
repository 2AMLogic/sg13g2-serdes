"""Shared helpers for the sim/*/make_record*.py renderers.

The renderers run as `python3 -I`, which drops the script directory from
sys.path, so each one inserts <repo>/sim/tools before importing this module.
Table rendering stays in the renderers; only the pin loading, the report /
error recovery and the evidence-labelling banner live here.
"""
import hashlib
import json
import pathlib

# Leading words of the evidence-labelling banner used by the TX records.
SIZING_BANNER = "**Sizing evidence, not a spec result and not a measurement.**"


def load_pins(repo):
    """Return (pdk, toolchain) dicts from sim/pdk.json and layout/toolchain.json."""
    repo = pathlib.Path(repo)
    return (json.loads((repo / "sim" / "pdk.json").read_text()),
            json.loads((repo / "layout" / "toolchain.json").read_text()))


def val(corner, name):
    """Value of the measurement `name` in a klt corner dict, or None."""
    for m in corner.get("measurements", []):
        if m["name"] == name:
            return m.get("value")
    return None


def sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def exit_codes(out):
    """Lines of <out>/exit-codes.txt, stripped of surrounding whitespace."""
    return (pathlib.Path(out) / "exit-codes.txt").read_text().strip().splitlines()


def report_or_error(out, name):
    """Return (report, None) for <out>/<name>.report.json, else (None, message).

    The message is the klt error recovered from <name>.stderr.txt, else the
    last stderr line, else "no report written". A missing stderr file is fine.
    """
    out = pathlib.Path(out)
    rp = out / f"{name}.report.json"
    if rp.exists():
        return json.loads(rp.read_text()), None
    errp = out / f"{name}.stderr.txt"
    err = errp.read_text() if errp.exists() else ""
    msg = "no report written"
    try:
        msg = json.loads(err[err.index("{"):])["error"]["message"]
    except Exception:
        msg = (err.strip().splitlines() or [msg])[-1]
    return None, msg
