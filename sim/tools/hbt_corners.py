"""HBT process, voltage and temperature axes for SG13G2 bench requests."""

HBT_LIB = "libs.tech/ngspice/models/cornerHBT.lib"
CAP_LIB = "libs.tech/ngspice/models/cornerCAP.lib"
DIO_LIB = "libs.tech/ngspice/models/cornerDIO.lib"

# The benches gang HBT, CAP and DIO sections as proposed in spec/target-spec.md.
PROCESS_SECTIONS = (
    ("hbt_typ", "cap_typ", "dio_tt"),
    ("hbt_bcs", "cap_bcs", "dio_ff"),
    ("hbt_wcs", "cap_wcs", "dio_ss"),
)


def corner_axes(debug=False):
    """Build the 27-point crossed grid, or its single typical debug point."""
    # klt 0.7.0 silently ignores corners.units, so use crossed axes in both modes.
    sections = PROCESS_SECTIONS[:1] if debug else PROCESS_SECTIONS
    return {
        "process": [
            {
                "name": hbt,
                "sections": [
                    {"lib": HBT_LIB, "section": hbt},
                    {"lib": CAP_LIB, "section": cap},
                    {"lib": DIO_LIB, "section": dio},
                ],
            }
            for hbt, cap, dio in sections
        ],
        "temperature_c": [27] if debug else [-40, 27, 125],
        "supply_v": {"vdd": [1.2] if debug else [1.08, 1.2, 1.32]},
    }
