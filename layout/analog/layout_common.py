"""Shared helpers for the analog layout generators under layout/analog/.

One `.subckt` netlist parser, one `klt` subprocess runner and one SPICE
length-to-micrometre converter, used by rx/gen_rx_cells.py, tx/gen_tx_core.py
and pads/gen_pad_cells.py. The device-to-`klt gen` mapping stays in each
generator (it legitimately differs). The generators run under `python3 -I`, so
each puts this directory on sys.path itself before importing.
"""
import json
import re
import subprocess
import sys

_UM = re.compile(r"([0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?)([unm]?)")
_UM_SCALE = {"u": 1.0, "n": 1e-3, "m": 1e3, "": 1e6}   # suffix -> um per unit; bare = metres


def um(v):
    """SPICE length -> micrometres. Suffix u (micro), n (nano), m (milli), or a
    bare number in metres (exponent form allowed). Anything else raises."""
    m = _UM.fullmatch(v)
    if not m:
        raise ValueError(f"unsupported SPICE length {v!r}")
    return float(m.group(1)) * _UM_SCALE[m.group(2)]


def parse_subckts(path):
    """-> {subckt: {"ports": [net, ...], "devs": [[token, ...], ...]}}.
    Comment (`*`) and continuation (`+`) lines are skipped; every other line
    inside a subckt is one device token list."""
    cells, cur = {}, None
    for line in open(path):
        t = line.split()
        if not t or t[0].startswith(("*", "+")):
            continue
        d = t[0].lower()
        if d == ".subckt":
            cur = {"ports": t[2:], "devs": []}
            cells[t[1]] = cur
        elif d == ".ends":
            cur = None
        elif cur is not None:
            cur["devs"].append(t)
    return cells


def run_klt(args, **kw):
    """Run a klt command, parse its JSON stdout. Exit 0 or 3 is OK, else exit."""
    r = subprocess.run(args, capture_output=True, text=True, **kw)
    if r.returncode not in (0, 3):
        sys.exit(f"{' '.join(args)} failed ({r.returncode}):\n{r.stderr}{r.stdout}")
    return json.loads(r.stdout)
