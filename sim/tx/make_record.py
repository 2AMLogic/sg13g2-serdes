"""Render record.md for a sim/tx/records/<id>/ directory from its klt sim report.

Reads the report, the request, sim/pdk.json and design/tx/netlists/*.spice (for
hashes); writes record.md beside the report. Sizing evidence only.
"""
import hashlib
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
tx = out.parent.parent
repo = tx.parent.parent
pdk = json.load(open(repo / "sim" / "pdk.json"))
tool = json.load(open(repo / "layout" / "toolchain.json"))
TAGS = ["ffe%d_%s" % (f, t) for f in (0, 1) for t in ("typ", "bcs", "wcs")]
reqs = {t: json.load(open(tx / f"tx_sizing_{t}.request.json")) for t in TAGS}
req = reqs[TAGS[0]]  # all six share the measurement names
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

L = [f"# TX sizing record {out.name}", "",
     "**Sizing evidence, not a spec result and not a measurement.** Simulated, "
     "first-cut sizes, ideal-source drive, lumped pad stand-in.", "",
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
exit_codes = (out / "exit-codes.txt").read_text().strip()
L += ["## Run", f"- {exit_codes}"]
reps, missing = {}, []
for t in TAGS:
    rp = out / f"tx_sizing_{t}.report.json"
    if rp.exists():
        reps[t] = json.load(open(rp))
    else:
        err = (out / f"tx_sizing_{t}.stderr.txt").read_text()
        msg = "no report written"
        try:
            msg = json.loads(err[err.index("{"):])["error"]["message"]
        except Exception:
            pass
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
def val(c, n):
    for m in c.get("measurements", []):
        if m["name"] == n:
            return m.get("value")
    return None

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
L += ["", "Differential output `v(padp)-v(padn)` into 100 ohm differential, 4 ohm + 100 fF per "
      "leg. R7 is NOT a conforming 20-80 % measurement: the thresholds are fixed absolute "
      "levels (+-0.06 V FFE off, +-0.04 V FFE on), chosen below the smallest steady half-swing "
      "so every corner crosses them, so the time is that of the central part of the edge and "
      "understates 20-80 % at large swing. The inputs are ideal 20 ps ramps. 'n/a' = no crossing.", ""]

L += ["## Not simulated", "",
      "- `mux2to1_cml`, `ffe_en`, `lvl_cml2cmos`: contain PSP103 MOS, which needs OSDI; "
      "the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` fail "
      "(sim/README.md known gaps, klayout-tools#3818/#3819; owner #3). Their R3 status is "
      "unknown beyond the argument in design/README.md.",
      "- `pad_esd`: the PDK ESD diode models are not loaded in this deck; a lumped stand-in "
      "loads each output. R18, R19 and R6 are not assessed (#24).",
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
