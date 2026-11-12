"""Render record.md for a sim/tx/records/<id>/ directory from its klt sim report.

Reads the report, the request, sim/pdk.json and design/tx/netlists/*.spice (for
hashes); writes record.md beside the report. Sizing evidence only.
"""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
tx = out.parent.parent
repo = tx.parent.parent
sys.path.insert(0, str(repo / "sim" / "tools"))
import record_common as rc  # noqa: E402
pdk, tool = rc.load_pins(repo)
TAGS = ["ffe%d_%s" % (f, t) for f in (0, 1) for t in ("typ", "bcs", "wcs")]
reqs = {t: json.load(open(tx / f"tx_sizing_{t}.request.json")) for t in TAGS}
req = reqs[TAGS[0]]  # all six share the measurement names
sha = rc.sha

L = [f"# TX sizing record {out.name}", "",
     rc.SIZING_BANNER + " Simulated, "
     "first-cut sizes, ideal-source drive, extracted pad-metal C + PDK ESD diodes (issue #142).", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}`",
     ]
for t in TAGS:
    L.append(f"- `tx_sizing_{t}.sp` sha256 `{sha(tx / f'tx_sizing_{t}.sp')}`, "
             f"`tx_sizing_{t}.request.json` sha256 `{sha(tx / f'tx_sizing_{t}.request.json')}`")
for c in ("bias", "predriver", "driver_ffe"):
    L.append(f"- netlist `design/tx/netlists/{c}.spice` sha256 `{sha(repo / 'design' / 'tx' / 'netlists' / (c + '.spice'))}`")
L.append("")
exit_codes = "\n".join(rc.exit_codes(out))
L += ["## Run", f"- {exit_codes}"]
reps, missing = {}, []
for t in TAGS:
    rep, msg = rc.report_or_error(out, f"tx_sizing_{t}")
    if rep is not None:
        reps[t] = rep
    else:
        missing.append((t, msg))
for t, msg in missing:
    L.append(f"- {t}: NO REPORT: {msg}")
if not reps:
    (out / "record.md").write_text("\n".join(L) + "\n")
    sys.exit(0)
corners = []
for t, rep in reps.items():
    rem = rep["environment"].get("remote") or {}
    L.append(f"- {t}: status **{rep['status']}** ({rep['passed']}/{rep['corner_count']} corners pass, "
             f"{rep.get('failed', 0)} fail, {rep['errored']} error), backend job `{rem.get('job_id')}`")
    for c in rep["corners"]:
        c = dict(c, corner_id=f"{t}/{c['corner_id']}")
        corners.append(c)
L.append("")
names = [m["name"] for m in req["measurements"]]
val = rc.val

def worst(prefix, fn):
    rows = []
    for n in names:
        if n.startswith(prefix):
            vs = [(val(c, n), c["corner_id"]) for c in corners if val(c, n) is not None]
            if vs:
                v, cid = fn(vs, key=lambda t: t[0])
                rows.append((n, v, cid))
    return rows

L += ["## R3 check (DR-003): collector <= 1.32 V, reverse Vbe <= 1.0 V",
      "", "Worst case over all corners per HBT node.", "",
      "| check | worst value (V) | limit (V) | corner |", "|---|---|---|---|"]
viol = 0
for prefix, lim in (("vc_max_", 1.32), ("vbe_rev_max_", 1.0)):
    for n, v, cid in worst(prefix, max):
        flag = "" if v <= lim else " **VIOLATION**"
        viol += v > lim
        L.append(f"| {n} | {v:.4f}{flag} | {lim} | {cid} |")
L += ["", f"- nodes beyond the R3 limits in this grid: **{viol}**", "",
      "## Informational headroom (not R3 limits)", "",
      "| measure | worst value | corner |", "|---|---|---|"]
for prefix, fn in (("vce_min_", min), ("vcb_min_", min), ("vce_max_", max)):
    for n, v, cid in worst(prefix, fn):
        L.append(f"| {n} | {v:.4f} V | {cid} |")

L += ["", "## First look at R4 and R7 (sizing evidence, not a spec result)", "",
      "| corner | r4 steady hi (V) | r4 steady lo (V) | r4 peak max/min (V) | r7 rise (ps) | r7 fall (ps) | Idd (mA) |",
      "|---|---|---|---|---|---|---|"]
for c in sorted(corners, key=lambda c: c["corner_id"]):
    g = lambda n, s=1.0: (f"{val(c, n) * s:.4g}" if val(c, n) is not None and val(c, n) * s > 0
                          or (val(c, n) is not None and not n.startswith("r7")) else "n/a")
    L.append(f"| {c['corner_id']} | {g('r4_steady_hi')} | {g('r4_steady_lo')} | "
             f"{g('r4_peak_max_vppd')} / {g('r4_peak_min_vppd')} | {g('r7_rise_20_80_s', 1e12)} | "
             f"{g('r7_fall_80_20_s', 1e12)} | {g('idd_avg', 1e3)} |")
L += ["", "Differential output `v(padp)-v(padn)` into 100 ohm differential, 4 ohm series + extracted "
      "70.66 fF pad-metal C + PDK ESD clamp diodes per leg (issue #142; was 4 ohm + 100 fF). R7 is NOT a conforming 20-80 % measurement: the thresholds are fixed absolute "
      "levels (+-0.06 V FFE off, +-0.04 V FFE on), chosen below the smallest steady half-swing "
      "so every corner crosses them, so the time is that of the central part of the edge and "
      "understates 20-80 % at large swing. The inputs are ideal 20 ps ramps. 'n/a' = no crossing.", ""]

L += ["## Not simulated", "",
      "- `mux2to1_cml`, `ffe_en`, `lvl_cml2cmos`: contain PSP103 MOS, which needs OSDI; "
      "the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` fail "
      "(sim/README.md known gaps, klayout-tools#3818/#3819; owner #3). Their R3 status is "
      "unknown beyond the argument in design/README.md.",
      "- `pad_esd` cell: not inlined; each output sees a 4 ohm series stand-in, the extracted "
      "70.66 fF pad-metal C (layout/analog/pads/records/2026-11-12-fc8a7fa, quasi-static, no bondwire/package) "
      "and the PDK clamp diodes. PDK dantenna/dpantenna equivalence to the diodevdd_2kv clamp is not "
      "established (LVS #27, DR-013); only the TX padp leg is covered. R6 is in sim/bench/.",
      "- PDK `rsil` is an OSDI (`r3_cmc`) model, so the deck uses a behavioural resistor "
      "from the PDK symbol's own value formula, with the corner's sheet-resistance scale "
      "(6.02/7.0/7.98 ohm/sq) and tc1 = 3.1e-3. Resistor current-density limits are not checked.",
      "- Corners: HBT, capacitor and resistor corners move together (typ/typ/typ, bcs/bcs/bcs, "
      "wcs/wcs/wcs), x supply 1.08/1.2/1.32 V x -40/27/125 C x FFE off / all three post slices on. "
      "Mismatch/Monte Carlo is not run.",
      "- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not the mux output.",
      "- Supply and bias: Rref is a placeholder resistor reference, so tail current tracks "
      "the supply; the bias block is not a supply-independent reference.", ""]
(out / "record.md").write_text("\n".join(L))
print(f"make_record.py: wrote {out / 'record.md'}")
