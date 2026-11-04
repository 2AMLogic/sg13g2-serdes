"""Shared xschem symbol pin geometry for the design/ schematic generators.

One table of pin offsets (rot 0, from the symbol origin) for every library
symbol the TX and RX generators place. A symbol-geometry correction is made
here once. Imported by design/tx/gen_schematics.py and
design/rx/tools/gen_schematics.py (both run with `python3 -I`, so each puts
this directory on sys.path itself).
"""

PIN_OFFSETS = {
    "sg13g2_pr/npn13G2.sym": {"C": (20, -30), "B": (-20, 0), "E": (20, 30), "S": (20, 0)},
    "sg13g2_pr/sg13_lv_nmos.sym": {"D": (20, -30), "G": (-20, 0), "S": (20, 30), "B": (20, 0)},
    "sg13g2_pr/sg13_lv_pmos.sym": {"D": (20, 30), "G": (-20, 0), "S": (20, -30), "B": (20, 0)},
    "sg13g2_pr/rsil.sym": {"P": (0, -30), "M": (0, 30)},
    "sg13g2_pr/rppd.sym": {"P": (0, -30), "M": (0, 30)},
    "sg13g2_pr/cap_cmim.sym": {"c0": (0, -30), "c1": (0, 30)},
    "sg13g2_pr/diodevdd_2kv.sym": {"vdd": (0, -30), "pad": (0, 30), "vss": (-30, 0)},
    "sg13g2_pr/diodevss_2kv.sym": {"vdd": (-30, 0), "pad": (0, -30), "vss": (0, 30)},
    "sg13g2_pr/bondpad.sym": {"pad": (0, 40)},
    "devices/res.sym": {"P": (0, -30), "M": (0, 30)},
    "devices/capa.sym": {"p": (0, -30), "m": (0, 30)},
}


def stub(dx, dy):
    """Direction (sx, sy) a label stub leaves a pin at offset (dx, dy)."""
    if dy == 0:
        return (30 if dx > 0 else -30, 0)
    return (0, 20 if dy > 0 else -20)
