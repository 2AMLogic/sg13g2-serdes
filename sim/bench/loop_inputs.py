"""CDR loop inputs read from the repo, never re-typed, plus the loop's derived scalars.

The single implementation of the two parsers that give the CDR loop its
authoritative parameters, so no consumer has to copy them:

  * ``rtl_loop_params()`` -- KP / KI / FMAX / PHASE_INIT from the parameter
    defaults of ``rtl/serdes_cdr_filter.v``.
  * ``dr007_delays()``    -- the digital loop delay and the ASSUMED analog
    delay from the delay table of
    ``spec/decisions/DR-007-cdr-loop-analysis.md``, which names itself the
    single source of truth for both ("it must read this value and cite this
    record").

The module also exports the loop's four derived scalars, each defined here
exactly once so no consumer re-types them (issue #167):

  * ``UI``          -- 8192.0, phase LSB per UI (1 LSB = 1/16384 clock
    period, half-rate; DR-007's phase unit).
  * ``HALF_UI``     -- UI / 2, the slip threshold.
  * ``UI_PER_WORD`` -- 16, the 16:1 serialisation (ratified spec, via DR-007).
  * ``PPM_LSB``     -- LSB per word per ppm, DERIVED as
    ``UI_PER_WORD * 1e-6 * UI`` rather than typed: DR-007 states the value
    only to three decimals ("1 ppm = 0.131 LSB per word"), so the exact
    0.131072 cannot be parsed from the record.  DR-007 is cited for the
    unit; the arithmetic is the source of the value.

Consumers: ``sim/bench/linkcore.py`` (re-exports the parsers, so the link
benches and ``sim/bench/cdrmodel.py`` keep their existing call sites),
``sim/bench/cdrmodel.py`` and ``scripts/cdr-loop-analysis.py`` (which import
these scalars).

Stdlib only, deliberately: a consumer that wants nothing but these six
integers and four scalars must not have to import numpy, scipy, the channel
model or the statistical eye to get them.
"""
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[2]

RTL_SOURCE = "rtl/serdes_cdr_filter.v"
DR007_SOURCE = "spec/decisions/DR-007-cdr-loop-analysis.md"

# Derived scalars, defined exactly once here (issue #167).  PPM_LSB is derived,
# not typed: DR-007 states "1 ppm = 0.131 LSB per word" (3 dp), so the exact
# value cannot be parsed from the record -- DR-007 is the unit's source, the
# arithmetic the value's.
UI = 8192.0                          # phase LSB per UI (1 LSB = 1/16384 clock period, half-rate; DR-007)
HALF_UI = UI / 2                     # slip threshold (|e| >= 0.5 UI)
UI_PER_WORD = 16                     # 16:1 serialisation (ratified spec, via DR-007)
PPM_LSB = UI_PER_WORD * 1e-6 * UI    # LSB per word per ppm; == 0.131072, DR-007 states it as 0.131


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
