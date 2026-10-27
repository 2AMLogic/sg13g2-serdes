"""Render record.md for a sim/rx/records/<id>/ directory from its klt sim reports.

Reads only that directory, the request files, sim/pdk.json and layout/toolchain.json.
Every number is sizing evidence from a simulation, never a measurement.
"""
import json
import pathlib
import re
import sys

out = pathlib.Path(sys.argv[1])
rx = out.parent.parent
repo = rx.parent.parent
pdk = json.load(open(repo / "sim" / "pdk.json"))
tool = json.load(open(repo / "layout" / "toolchain.json"))
codes = (out / "exit-codes.txt").read_text().strip().splitlines()

reports = {}
for name in ("ctle_ac", "ctle_op", "pad_ac", "latch_regen"):
    p = out / f"{name}.report.json"
    reports[name] = json.load(open(p)) if p.exists() else None


def val(c, n):
    for m in c.get("measurements", []):
        if m["name"] == n:
            return m.get("value")
    return None


def f(x, spec="{:.2f}", none="n/a"):
    return none if x is None else spec.format(x)


L = [f"# RX sizing record {out.name}", "",
     "**Sizing evidence, not a spec result.** Nothing here is measured. `spec/target-spec.md` is PROPOSED;",
     "rows R8-R10, R20 are used as draft targets only. Passives are ideal, the pad capacitance is a",
     "placeholder, the clock source is ideal, the CTLE load is a placeholder 80 fF, and the MOS level",
     "converter is not simulated. The grid is the HBT-family PVT set: hbt_typ/bcs/wcs x 1.08/1.2/1.32 V x -40/27/125 C (27 points).", "",
     "## Pins",
     f"- PDK: {pdk['source']} {pdk['release_tag']}, tarball sha256 `{pdk['tarball_sha256']}` (sim/pdk.json)",
     f"- klt: `{tool['klt_last_verified_commit']}` (layout/toolchain.json)",
     "- Schematics/netlists: design/rx/ at the commit named in the record id; netlist staleness gate `design/check-netlists.sh`",
     "", "## Runs"]
for name in reports:
    line = [l for l in codes if l.startswith(name)]
    r = reports[name]
    L += ["", f"### {name}", f"- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out records/{out.name}/{name}.report.json {name}.request.json`",
          f"- {line[0] if line else 'no exit code recorded'}"]
    if r is None:
        err = (out / f"{name}.stderr.txt").read_text() if (out / f"{name}.stderr.txt").exists() else ""
        L.append("- NO REPORT: " + (err.strip().splitlines()[-1][:300] if err.strip() else "no report written"))
        continue
    env = r["environment"]
    rem = env.get("remote") or {}
    L.append(f"- status: **{r['status']}** ({r['passed']}/{r['corner_count']} corners pass, {r['errored']} error); engine host {env.get('engine_host')}, ngspice {env.get('engine_version')}, backend job `{rem.get('job_id')}`")

ac = reports["ctle_ac"]
if ac:
    L += ["", "## CTLE AC response per setting (peaking = gain at 5 GHz minus gain at 0.1 GHz, differential, dB)", "",
          "Code = c2c1c0. First-look comparison with R10: 0-10 dB peaking at 5 GHz in >= 8 steps. `fail` limits are code 0 <= 1 dB and code 7 >= 10 dB.", "",
          "| corner | " + " | ".join(f"c{k}" for k in range(8)) + " | gain@0.1G c0 / c7 | gain@5G c7 |",
          "|---|" + "---|" * 10]
    for c in ac["corners"]:
        row = [f(val(c, f"ctle_c{k}_peak5g_db")) for k in range(8)]
        L.append(f"| {c['corner_id']} | " + " | ".join(row) + f" | {f(val(c,'ctle_c0_g0p1g_db'))} / {f(val(c,'ctle_c7_g0p1g_db'))} | {f(val(c,'ctle_c7_g5g_db'))} |")
op = reports["ctle_op"]
viol = []
if op:
    L += ["", "## CTLE output common mode (V, code 7)", "", "| corner | out CM |", "|---|---|"]
    for c in op["corners"]:
        L.append(f"| {c['corner_id']} | {f(val(c,'ctle_c7_outcm'), '{:.3f}')} |")
    for c in op["corners"]:
        for m in c["measurements"]:
            if m.get("status") == "fail":
                viol.append((c["corner_id"], m["name"], m["value"]))
lr = reports["latch_regen"]
if lr:
    L += ["", "## Latch regeneration at 5 GHz (clock buffer + latch, ps)", "",
          "Time from the clock edge that closes the sample phase to |q| = 0.25 V (about 85 % of the swing), +-10 mV differential input. First-look limit: 100 ps (half period).", "",
          "| corner | t_regen up | t_regen down | q swing (V) |", "|---|---|---|---|"]
    for c in lr["corners"]:
        up, dn = val(c, "latch_t_regen_up"), val(c, "latch_t_regen_dn")
        L.append(f"| {c['corner_id']} | {f(None if up is None else up*1e12,'{:.1f}')} | {f(None if dn is None else dn*1e12,'{:.1f}')} | {f(val(c,'latch_q_swing_v'))} |")
    for c in lr["corners"]:
        for m in c["measurements"]:
            if m.get("status") == "fail":
                viol.append((c["corner_id"], m["name"], m["value"]))
pad = reports["pad_ac"]
if pad:
    L += ["", "## Termination + pad first-look |Zdiff| (ohm, placeholder 50 fF pads)", "", "| corner | 0.1 GHz | 5 GHz |", "|---|---|---|"]
    for c in pad["corners"]:
        L.append(f"| {c['corner_id']} | {f(val(c,'zdiff_0p1g_ohm'),'{:.1f}')} | {f(val(c,'zdiff_5g_ohm'),'{:.1f}')} |")

L += ["", "## HBT node stress versus DR-003 (collector <= 1.32 V, reverse Vbe <= 1.0 V)", ""]
worst = {}
for rname in ("ctle_op", "latch_regen"):
    r = reports[rname]
    if not r:
        continue
    for c in r["corners"]:
        for m in c["measurements"]:
            n = m["name"]
            if n.endswith("_vc_max") or n.endswith("_vbe_rev_max"):
                v = m.get("value")
                if v is not None and (n not in worst or v > worst[n][0]):
                    worst[n] = (v, c["corner_id"])
vc = {n: w for n, w in worst.items() if n.endswith("_vc_max")}
vb = {n: w for n, w in worst.items() if n.endswith("_vbe_rev_max")}
if vc:
    top = max(vc.items(), key=lambda kv: kv[1][0])
    L.append(f"- Highest collector node: `{top[0]}` = {top[1][0]:.3f} V at {top[1][1]}.")
if vb:
    top = max(vb.items(), key=lambda kv: kv[1][0])
    L.append(f"- Largest reverse Vbe (Ve - Vb; negative = still forward biased): `{top[0]}` = {top[1][0]:.3f} V at {top[1][1]}.")
stress_fail = [v for v in viol if v[1].endswith("_vc_max") or v[1].endswith("_vbe_rev_max")]
L.append(f"- Nodes over a DR-003 limit: {len(stress_fail)}" + ("" if not stress_fail else " -- " + "; ".join(f"{a} {b}={c:.3f}" for a, b, c in stress_fail)))
L.append("- Per-node values for every HBT, corner and CTLE code are in the `*.report.json` files in this directory.")
other = [v for v in viol if v not in stress_fail]
L += ["", "## Limits missed (first-look comparisons)", ""]
L += [f"- {a}: `{b}` = {c}" for a, b, c in other] or ["- none"]
L += ["", "## Not simulated",
      "",
      "- `lvl_cml2cmos` (thin-oxide MOS, PSP103 via OSDI): not simulated; the host ngspice cannot load OSDI v0.4 and batch jobs staging `.osdi` inputs fail (klayout-tools#3818, #3819; sim/README.md; blocked on #3).",
      "- PDK resistors `rsil`/`rppd` (`r3_cmc` OSDI): not simulated; every resistor in design/rx is an ideal `res` for that reason, so resistor corners (`res_*`) are not exercised.",
      "- Pad/ESD capacitance at 5 GHz, SDD11 (R9) and the core-to-pad seam: not simulated beyond the placeholder |Zdiff| above; owned by #24/#28.",
      "- Sampler offset and noise (Monte Carlo, DR-002), CDR, link behaviour, clock duty/quadrature error (R20 +-1 %, +-2 deg) and mismatch: not simulated.",
      "- Full PVT-full grid (135 points): not run; only the 27-point HBT-family grid (MOS corners absent), `hbt_*` sections ganged with `cap_*` and `dio_*`. The spec's 7-point PVT-edge set is a subset of it.",
      "- Unconfirmed: the +-10 % supply tolerance is a proposal (DR-003); temperature -40/27/125 C is a proposal."]
(out / "record.md").write_text("\n".join(L) + "\n")
print(f"make_record.py: wrote {out / 'record.md'}")
