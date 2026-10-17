"""Render the committed smoke record (record.md) from the klt sim reports in a
records/<id>/ directory. Reads only that directory plus sim/pdk.json,
layout/toolchain.json and the request files; writes record.md beside the reports."""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
smoke = out.parent.parent
repo = smoke.parent.parent
pdk = json.load(open(repo / "sim" / "pdk.json"))
tool = json.load(open(repo / "layout" / "toolchain.json"))

lines = [
    f"# Smoke record {out.name}",
    "",
    "Toolchain bring-up only (issue #3). Devices are placeholders, not design values.",
    "",
    "## Pins",
    f"- PDK: {pdk['source']} {pdk['release_tag']}, tarball sha256 `{pdk['tarball_sha256']}`",
    f"- OpenVAF-Reloaded {pdk['osdi_toolchain']['compiler_tag']} (sim/tools/build-osdi.sh)",
    f"- klt: `{tool['klt_last_verified_commit']}`",
    "",
    "## Runs",
]
exit_codes = (out / "exit-codes.txt").read_text().strip().splitlines()
for name in ("hbt_gummel", "mos_inv_dc", "mixed_tran"):
    req = json.load(open(smoke / f"{name}.request.json"))
    lines += ["", f"### {name}", f"- command: `cd sim/smoke && klt sim --format json --wait-for-capacity 900 --report-out records/{out.name}/{name}.report.json {name}.request.json`"]
    lines.append(f"- {[l for l in exit_codes if l.startswith(name)][0]}")
    rp = out / f"{name}.report.json"
    if not rp.exists():
        err = (out / f"{name}.stderr.txt").read_text()
        msg = "no report written"
        try:
            msg = json.loads(err[err.index("{"):])["error"]["message"]
        except Exception:
            pass
        lines.append(f"- NO REPORT: {msg}")
        continue
    rep = json.load(open(rp))
    env = rep["environment"]
    rem = env.get("remote") or {}
    sim = (rem.get("worker_environment") or {}).get("simulator") or {}
    banner = (sim.get("version_banner") or "").split("\n")[1:2]
    lines += [
        f"- status: **{rep['status']}** ({rep['passed']}/{rep['corner_count']} corners pass, {rep['errored']} error)",
        f"- engine host: {env.get('engine_host')}, ngspice {env.get('engine_version')} {banner}, backend job `{rem.get('job_id')}`, runner klt {rem.get('runner_klt_version')}",
        "",
        "| corner | status | runtime_s | notes |",
        "|---|---|---|---|",
    ]
    for c in rep["corners"]:
        note = "; ".join(f"{m['name']}={m['value']}" for m in c.get("measurements", []) if m.get("value") is not None)
        if c.get("diagnostics"):
            note = (c["diagnostics"][0]["code"] + ": " + c["diagnostics"][0]["message"])[:160]
        lines.append(f"| {c['corner_id']} | {c['status']} | {c.get('runtime_s')} | {note} |")
    secs = sorted({s["section"] if isinstance(s, dict) else s
                   for p in req["corners"]["process"] for s in p["sections"]})
    lines.append(f"- model sections exercised: {', '.join(secs)}")

hbt_sections = sorted(
    l.split()[1] for l in open(
        pathlib.Path(__import__("os").environ["PDK_ROOT"]) / "ihp-sg13g2/libs.tech/ngspice/models/cornerHBT.lib",
        errors="replace").read().replace("\r", "\n").splitlines()
    if l.upper().startswith(".LIB "))
lines += ["", "## HBT corner sections found in cornerHBT.lib", "- " + ", ".join(hbt_sections),
          "- smoke grid uses the deterministic ones: hbt_typ, hbt_bcs, hbt_wcs (the _mismatch/_stat sections are Monte Carlo variants, out of scope)"]
(out / "record.md").write_text("\n".join(lines) + "\n")
print(f"make_record.py: wrote {out / 'record.md'}")
