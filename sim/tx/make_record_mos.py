"""Render record.md for a sim/tx/records/<id>-mos/ directory from its klt sim reports.

Covers the three MOS-cell requests (tx_mos_*, issue #80). Reads the reports, the
requests, sim/pdk.json and design/tx/netlists/*.spice (for hashes); writes record.md
beside the reports. Failing, erroring and missing corners are kept and listed.
Sizing evidence only.
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
CELLS = ["mux2to1_cml", "tx_lvl_cml2cmos", "ffe_en"]
sha = lambda p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

L = [f"# TX MOS-cell sizing record {out.name}", "",
     "**Sizing evidence, not a spec result and not a measurement.** Simulated, first-cut "
     "sizes, ideal-source drive. No `spec/` row is graded here.", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}`"]
for c in CELLS:
    L.append(f"- `tx_mos_{c}.sp` sha256 `{sha(tx / f'tx_mos_{c}.sp')}`, "
             f"`tx_mos_{c}.request.json` sha256 `{sha(tx / f'tx_mos_{c}.request.json')}`")
    L.append(f"- netlist `design/tx/netlists/{c}.spice` sha256 "
             f"`{sha(repo / 'design' / 'tx' / 'netlists' / (c + '.spice'))}`")
L.append("- bias cell netlists also inlined: `bias`, `predriver` (mux bench), `bias` (ffe_en bench)")
L.append("")

exit_codes = (out / "exit-codes.txt").read_text().strip().replace("\n", "; ")
L += ["## Run", f"- {exit_codes}"]
reps, missing = {}, []
for c in CELLS:
    rp = out / f"tx_mos_{c}.report.json"
    if rp.exists():
        reps[c] = json.load(open(rp))
    else:
        errp = out / f"tx_mos_{c}.stderr.txt"
        err = errp.read_text() if errp.exists() else ""
        msg = "no report written"
        try:
            msg = json.loads(err[err.index("{"):])["error"]["message"]
        except Exception:
            msg = (err.strip().splitlines() or [msg])[-1]
        missing.append((c, msg))
for c, msg in missing:
    L.append(f"- {c}: NO REPORT: {msg}")
corners = {}
for c, rep in reps.items():
    rem = rep["environment"].get("remote") or {}
    L.append(f"- {c}: status **{rep['status']}** ({rep['passed']}/{rep['corner_count']} corners pass, "
             f"{rep.get('failed', 0)} fail, {rep['errored']} error), backend job `{rem.get('job_id')}`")
    corners[c] = rep["corners"]
L.append("")

bad = [(c, k) for c, cs in corners.items() for k in cs if k.get("status") not in ("pass", "ok")]
if bad:
    L += ["## Failing or erroring corners (kept, not dropped)", ""]
    for c, k in bad:
        d = (k.get("diagnostics") or [{}])[0]
        L.append(f"- {c}/{k['corner_id']}: {k.get('status')} {d.get('code') or ''} "
                 f"{(d.get('message') or '')[:240]}".rstrip())
    L.append("")


def val(k, n):
    for m in k.get("measurements", []):
        if m["name"] == n:
            return m.get("value")
    return None


def fmt(v, scale=1.0, nd=4):
    return "n/a" if v is None else f"{v * scale:.{nd}g}"


if "mux2to1_cml" in corners:
    ks = sorted(corners["mux2to1_cml"], key=lambda k: k["corner_id"])
    L += ["## mux2to1_cml (5 GHz clock, A=1/B=0, 10 Gb/s 1010 output)", "",
          "| corner | out max (V) | out min (V) | cm (V) | rise (ps) | fall (ps) | Idd (mA) | sq_a hi/lo (V) |",
          "|---|---|---|---|---|---|---|---|"]
    for k in ks:
        L.append(f"| {k['corner_id']} | {fmt(val(k, 'out_diff_max'))} | {fmt(val(k, 'out_diff_min'))} | "
                 f"{fmt(val(k, 'out_cm_avg'))} | {fmt(val(k, 'rise_pm30mv_s'), 1e12)} | "
                 f"{fmt(val(k, 'fall_pm30mv_s'), 1e12)} | {fmt(val(k, 'idd_avg'), 1e3)} | "
                 f"{fmt(val(k, 'sq_a_max'))} / {fmt(val(k, 'sq_a_min'))} |")
    L += ["", "Rise/fall are the time between the fixed +-30 mV differential crossings, NOT a "
          "conforming 20-80 % figure (ngspice cannot reference an earlier `.meas` as a threshold). "
          "'n/a' = no crossing in the window (swing under 30 mV or no edge).", "",
          "### Node stress (R3: collector <= 1.32 V, reverse Vbe <= 1.0 V)", "",
          "| check | worst value (V) | limit (V) | corner |", "|---|---|---|---|"]
    names = sorted({m["name"] for k in ks for m in k.get("measurements", [])
                    if m["name"].startswith(("vc_max_", "vbe_rev_max_"))})
    viol = 0
    for n in names:
        vs = [(val(k, n), k["corner_id"]) for k in ks if val(k, n) is not None]
        if not vs:
            continue
        v, cid = max(vs, key=lambda t: t[0])
        lim = 1.32 if n.startswith("vc_") else 1.0
        flag = "" if v <= lim else " **VIOLATION**"
        viol += v > lim
        L.append(f"| {n} | {v:.4f}{flag} | {lim} | {cid} |")
    L += ["", f"- nodes beyond the R3 limits in this grid: **{viol}**", "",
          "Informational Vce max per mux HBT (open-base BVCEO is 1.4 V):", ""]
    for n in sorted(m for m in {m["name"] for k in ks for m in k.get("measurements", [])}
                    if m.startswith("vce_max_")):
        vs = [(val(k, n), k["corner_id"]) for k in ks if val(k, n) is not None]
        if vs:
            v, cid = max(vs, key=lambda t: t[0])
            L.append(f"- {n}: {v:.4f} V ({cid})")
    L.append("")

if "tx_lvl_cml2cmos" in corners:
    ks = sorted(corners["tx_lvl_cml2cmos"], key=lambda k: k["corner_id"])
    L += ["## tx_lvl_cml2cmos (2.5 GHz input, 20 fF load)", "",
          "| corner | out hi (V) | out lo (V) | duty (%) | tpd LH (ps) | tpd HL (ps) | Idd (mA) |",
          "|---|---|---|---|---|---|---|"]
    for k in ks:
        th, tp = val(k, "t_high_s"), val(k, "t_period_s")
        duty = None if th is None or not tp else 100.0 * th / tp
        L.append(f"| {k['corner_id']} | {fmt(val(k, 'out_hi'))} | {fmt(val(k, 'out_lo'))} | "
                 f"{fmt(duty)} | {fmt(val(k, 'tpd_lh_s'), 1e12)} | {fmt(val(k, 'tpd_hl_s'), 1e12)} | "
                 f"{fmt(val(k, 'idd_avg'), 1e3)} |")
    L += ["", "Duty = time above vdd/2 over the period (`t_high_s` / `t_period_s`). Delay is from the "
          "differential input zero crossing to the output vdd/2 crossing. 'n/a' = no crossing.", ""]

if "ffe_en" in corners:
    ks = sorted(corners["ffe_en"], key=lambda k: k["corner_id"])
    L += ["## ffe_en (vbp0..2 minus vbn at each enable code; slices enabled = 0..3)", "",
          "| corner | code | vbn (V) | vbp0-vbn (V) | vbp1-vbn (V) | vbp2-vbn (V) |",
          "|---|---|---|---|---|---|"]
    for k in ks:
        for code in range(4):
            L.append(f"| {k['corner_id']} | {code} | {fmt(val(k, f'vbn_code{code}'))} | " +
                     " | ".join(fmt(val(k, f"vbp{i}_minus_vbn_code{code}")) for i in range(3)) + " |")
    L += ["", "An enabled slice has vbp = vbn (difference near 0); a disabled one is pulled low "
          "through the 1 kohm series resistor. vbp is unloaded.", ""]

L += ["## Corners and what is simulated", "",
      "- Process pairing (MOS / HBT / CAP / RES sections ganged): tt/typ, ff/bcs, ss/wcs, and "
      "fs and sf both with the typical HBT/CAP/RES (no HBT skew exists for them), x supply "
      "1.08/1.2/1.32 V x -40/27/125 C = 45 corners per cell. Mismatch/Monte Carlo is not run.",
      "- MOS is PSP103 and the PDK `rsil`/`rppd` are the real `r3_cmc` models, loaded via "
      "`osdi_preload` as in `sim/smoke/`. No behavioural resistor is used in these benches "
      "(the six HBT-bench decks still use the stand-in).",
      "- Inputs are ideal sources: a 0.4 V-swing 5 GHz clock (an assumption, not a spec value) "
      "and 300 mV vdd-referenced CML levels. Loads are lumped (predriver input, 20 fF). "
      "Resistor current-density limits are not checked.", ""]
(out / "record.md").write_text("\n".join(L))
print(f"make_record_mos.py: wrote {out / 'record.md'}")
