"""CDR loop inputs read from the repo, never re-typed.

The single implementation of the two parsers that give the CDR loop its
authoritative parameters, so no consumer has to copy them:

  * ``rtl_loop_params()`` -- KP / KI / FMAX / PHASE_INIT from the parameter
    defaults of ``rtl/serdes_cdr_filter.v``.
  * ``dr007_delays()``    -- the digital loop delay and the ASSUMED analog
    delay from the delay table of
    ``spec/decisions/DR-007-cdr-loop-analysis.md``, which names itself the
    single source of truth for both ("it must read this value and cite this
    record").

Consumers: ``sim/bench/linkcore.py`` (re-exported, so the link benches and
``sim/bench/cdrmodel.py`` keep their existing call sites) and
``scripts/cdr-loop-analysis.py`` (the DR-007 / DR-010 loop analysis).

Stdlib only, deliberately: a consumer that wants nothing but these six
integers must not have to import numpy, scipy, the channel model or the
statistical eye to get them.
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]

RTL_SOURCE = "rtl/serdes_cdr_filter.v"
DR007_SOURCE = "spec/decisions/DR-007-cdr-loop-analysis.md"


def rtl_loop_params():
    """KP/KI/FMAX/PHASE_INIT defaults of rtl/serdes_cdr_filter.v."""
    src = (REPO / RTL_SOURCE).read_text()

    def num(name):
        m = re.search(rf"parameter\s+(?:signed\s+)?(?:\[[^\]]*\]\s+)?{name}\s*=\s*(?:\d+'s?([dh]))?([0-9a-fA-F]+)", src)
        if not m:
            raise SystemExit(f"loop_inputs: cannot read {name} from {RTL_SOURCE}")
        return int(m.group(2), 16 if m.group(1) == "h" else 10)
    return {"KP": num("KP"), "KI": num("KI"), "FMAX": num("FMAX"), "PHASE_INIT": num("PHASE_INIT")}


def dr007_delays():
    """Digital delay (clocks) from DR-007's table; analog delay is the ASSUMED value stated there."""
    src = (REPO / DR007_SOURCE).read_text()
    d = re.search(r"\|\s*Digital\s*\|\s*\*\*(\d+)\*\*", src)
    a = re.search(r"\|\s*Analog[^|]*\|\s*\*\*(\d+)\*\*\s*\|\s*\*\*ASSUMED", src)
    if not (d and a):
        raise SystemExit(f"loop_inputs: cannot read the delay table of {DR007_SOURCE}")
    return {"digital": int(d.group(1)), "analog_assumed": int(a.group(1))}
