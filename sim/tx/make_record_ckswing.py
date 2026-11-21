"""Render record.md for a sim/tx/records/<id>-ckswing/ directory (issue #98).

The mux2to1_cml clock-swing sweep: one request per per-side clock swing
(tx_mosck_mux2to1_cml_sw<mV>), 45 corners each. Failing, erroring and missing
corners are kept. Sizing evidence only; the 0.4 V point is the existing
records/*-mos/ record, not repeated here.
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
reqs = sorted(tx.glob("tx_mosck_*.request.json"))
L = [f"# mux2to1_cml clock-swing sweep record {out.name}", "",
     rc.SIZING_BANNER + " Per-side clock swing swept at a fixed 0.6 V centre; no `spec/` row is graded here.", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}`",
     f"- `design/tx/netlists/mux2to1_cml.spice` sha256 `{rc.sha(repo / 'design/tx/netlists/mux2to1_cml.spice')}`"]
for r in reqs:
    t = r.name[:-len(".request.json")]
    L.append(f"- `{t}.sp` sha256 `{rc.sha(tx / (t + '.sp'))}`, request sha256 `{rc.sha(r)}`")
L += ["", "## Run", "- " + "; ".join(rc.exit_codes(out)), ""]
L += ["## Output differential swing per corner (V, min of out_diff_min / max of out_diff_max)", ""]
swings = []
for r in reqs:
    t = r.name[:-len(".request.json")]
    rep, msg = rc.report_or_error(out, t)
    sw = int(t.rsplit("_sw", 1)[1]) / 1000
    if rep is None:
        L.append(f"- swing {sw} V per side: NO REPORT: {msg}")
        continue
    rem = rep["environment"].get("remote") or {}
    L.append(f"- swing {sw} V per side: **{rep['status']}**, {rep['passed']}/{rep['corner_count']} pass, "
             f"{rep.get('failed', 0)} fail, {rep['errored']} error, job `{rem.get('job_id')}`")
    swings.append((sw, rep))
L.append("")
for sw, rep in swings:
    L += [f"### {sw} V per side ({2 * sw} V differential peak-to-peak)", "",
          "| corner | status | out max (V) | out min (V) | peak-peak (V) |", "|---|---|---|---|---|"]
    for k in sorted(rep["corners"], key=lambda k: k["corner_id"]):
        mx, mn = rc.val(k, "out_diff_max"), rc.val(k, "out_diff_min")
        pp = None if mx is None or mn is None else mx - mn
        f = lambda v: "n/a" if v is None else f"{v:.4g}"
        L.append(f"| {k['corner_id']} | {k.get('status')} | {f(mx)} | {f(mn)} | {f(pp)} |")
    L.append("")
(out / "record.md").write_text("\n".join(L))
print(f"make_record_ckswing.py: wrote {out / 'record.md'}")
