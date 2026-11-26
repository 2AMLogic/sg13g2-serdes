"""Render record.md for a sim/tx/records/<id>-r4sweep-<proc>*/ directory (issue #286).

Reads the per-candidate klt sim reports written by run_r4sweep.sh (<out>/batch/<stem>/
report.json, stem r4sweep_<cand>_<proc>), the candidate table and, as the control
cross-check, the main-baseline FFE-off / all-slices-on reports of the issue #242 record.
Failing, erroring and missing corners are kept and listed. Sizing evidence only: the
tables report what was simulated and make no claim beyond the tested range.
"""
import json
import pathlib
import sys

out = pathlib.Path(sys.argv[1])
proc = sys.argv[2]
tx = out.parent.parent
repo = tx.parent.parent
sys.path.insert(0, str(repo / "sim" / "tools"))
import record_common as rc  # noqa: E402
pdk, tool = rc.load_pins(repo)
sha = rc.sha

CONTROL_REC = "20261123-022802-fedf656-vce"
LIM = "wcs/1.080V/-40C"   # control cross-check row (wcs process)
PLIM = f"{proc}/1.080V/-40C"  # limiting-corner row for this record's process
CANDS = [c for c in json.loads((tx / "r4sweep_candidates.json").read_text())
         if (out / "batch" / f"r4sweep_{c['id']}_{proc}").exists()]
R3 = (("vc_max_", 1.32), ("vce_max_", 1.4), ("vbe_rev_max_", 1.0))


def report(cand):
    p = out / "batch" / f"r4sweep_{cand}_{proc}" / "report.json"
    return json.loads(p.read_text()) if p.exists() else None


def corner(rep, cid):
    for c in rep.get("corners", []):
        if c["corner_id"] == cid:
            return c
    return None


def mv(x):
    return "n/a" if x is None else f"{1000 * x:.1f}"


def r3_worst(c, driver):
    """Smallest R3 margin (limit - value) over the driver_ffe cards (driver=True) or the
    predriver / bias cards (driver=False) in the corner, with its name."""
    best = None
    for m in c.get("measurements", []):
        if m["name"].startswith(("vc_max_", "vce_max_", "vbe_rev_max_")) and m.get("margin") is not None:
            if ("_drv_" in m["name"]) != driver:
                continue
            if best is None or m["margin"] < best[0]:
                best = (m["margin"], m["name"])
    return best


L = [f"# TX R4 swing-shortfall sweep record {out.name}", "",
     rc.SIZING_BANNER + " Issue #286. Nothing here is measured, no `spec/` row is graded "
     "and R3/R4 are not edited. The tested range bounds the tested designs only.", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}`",
     "- circuit revision: this commit's `design/tx/netlists/{bias,predriver,driver_ffe}.spice` "
     "(main `5c4eac5` driver, back-termination RT1/RT2 = 50 ohm typical). The revised load "
     "return of PR #270 is NOT in this record; see the scope note below.",
     f"- generator `sim/tx/make_sweep_r4.py` sha256 `{sha(tx / 'make_sweep_r4.py')}`, "
     f"candidates `sim/tx/r4sweep_candidates.json` sha256 `{sha(tx / 'r4sweep_candidates.json')}`"]
for c in CANDS:
    n = f"r4sweep_{c['id']}_{proc}"
    if (tx / (n + ".sp")).exists():
        L.append(f"- `{n}.sp` sha256 `{sha(tx / (n + '.sp'))}`, request sha256 "
                 f"`{sha(tx / (n + '.request.json'))}`")
for cell in ("bias", "predriver", "driver_ffe"):
    L.append(f"- netlist `design/tx/netlists/{cell}.spice` sha256 "
             f"`{sha(repo / 'design' / 'tx' / 'netlists' / (cell + '.spice'))}`")
L += ["", "## Swing quantity", "",
      "`swing = v(padp) - v(padn)` across the fixed external 100 ohm differential load "
      "(`Rload`), behind the R18 pad stand-in per leg (4 ohm series + 70.66 fF extracted pad "
      "C + PDK ESD clamp diodes; not the pad_esd cell). Stimulus: the issue #21 stream, a "
      "static 12-one preamble, a 12-zero run, a 12-one run, then a 48-bit PRBS-7 slice at "
      "100 ps/bit. FFE off (post-cursor slice bias 0 V).", "",
      "- `static` = `r4_steady_hi - r4_steady_lo`: v(vd) sampled at 1.35 ns (end of the first "
      "12-one run, ~1.13 ns settled) and 2.55 ns (end of the 12-zero run).",
      "- `PRBS run` = `r4_prbs_run_hi - r4_prbs_run_lo`: v(vd) 10 ps before the end of the "
      "longest one run (4 bits, 6.59 ns) and longest zero run (6 bits, 4.39 ns) of the PRBS-7 slice.",
      "- `PRBS p-p` = `r4_prbs_max_v - r4_prbs_min_v` over 3.9..8.8 ns (peak excursion incl. "
      "overshoot; an upper bound on a settled level).",
      "- With FFE off the static and PRBS-run levels are the VOD-style quantity comparable "
      "with R4. The de-emphasised level (all three slices on) is reported separately in the "
      "control table; it is a de-emphasis measurement, not a VOD figure.", ""]

# ---- sweep table at the limiting corner
L += [f"## Sweep at the low-supply cold corner `{PLIM}` (process {proc}), FFE off", "",
      "| candidate | dvb mV | RT scale | static mVppd | PRBS run mVppd | PRBS p-p mVppd | "
      "main tail mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
rows = []
for c in CANDS:
    rep = report(c["id"])
    cc = corner(rep, PLIM) if rep else None
    if cc is None:
        L.append(f"| {c['id']} | {1000*c['dvb_v']:+.0f} | {c['rt_length_scale']:.2f} | missing | | | | | | | | |")
        continue
    v = lambda n: rc.val(cc, n)
    if v("r4_steady_hi") is None:
        L.append(f"| {c['id']} | {1000*c['dvb_v']:+.0f} | {c['rt_length_scale']:.2f} | errored | | | | | | | | |")
        continue
    st = v("r4_steady_hi") - v("r4_steady_lo")
    pr = v("r4_prbs_run_hi") - v("r4_prbs_run_lo")
    pp = v("r4_prbs_max_v") - v("r4_prbs_min_v")
    ti = v("tail_i_main_a")
    pv = min(v("vce_min_drv_pair_p"), v("vce_min_drv_pair_n"))
    rows.append((c["id"], st))
    L.append(f"| {c['id']} | {1000*c['dvb_v']:+.0f} | {c['rt_length_scale']:.2f} | {mv(st)} | {mv(pr)} | "
             f"{mv(pp)} | {1000*ti:.2f} | {mv(v('vce_min_drv_tail_main'))} | {pv:.3f} | "
             f"{1e12*v('r7_rise_20_80_s'):.0f}/{1e12*v('r7_fall_80_20_s'):.0f} | {mv(st - 0.5)} | {mv(st - 0.3)} |")
L.append("")

# ---- R3 over all corners
L += [f"## R3 stress over the {proc} corners (3 supplies x 3 temperatures, includes 1.32 V)", "",
      "| candidate | corners pass/fail/error | smallest driver_ffe R3 margin V (card, corner) | "
      "smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | "
      f"{proc} 1.20 V / 27 C static mVppd |", "|---|---|---|---|---|---|"]
for c in CANDS:
    rep = report(c["id"])
    if rep is None:
        L.append(f"| {c['id']} | missing | | | |")
        continue
    worst, worstp, mn = None, None, None
    for cc in rep["corners"]:
        w = r3_worst(cc, True)
        if w and (worst is None or w[0] < worst[0]):
            worst = (w[0], w[1], cc["corner_id"])
        w = r3_worst(cc, False)
        if w and (worstp is None or w[0] < worstp[0]):
            worstp = (w[0], w[1], cc["corner_id"])
        hi, lo = rc.val(cc, "r4_steady_hi"), rc.val(cc, "r4_steady_lo")
        if hi is not None and lo is not None and (mn is None or hi - lo < mn[0]):
            mn = (hi - lo, cc["corner_id"])
    ref = corner(rep, f"{proc}/1.200V/27C")
    refv = None if ref is None or rc.val(ref, "r4_steady_hi") is None else \
        rc.val(ref, "r4_steady_hi") - rc.val(ref, "r4_steady_lo")
    L.append(f"| {c['id']} | {rep['passed']}/{rep['failed']}/{rep['errored']} | "
             f"{worst[0]:.3f} ({worst[1]}, {worst[2]}) | {worstp[0]:.3f} ({worstp[1]}, {worstp[2]}) | {mv(mn[0] if mn else None)} ({mn[1] if mn else ''}) | {mv(refv)} |")
L.append("")
failed = []
for c in CANDS:
    rep = report(c["id"])
    for cc in (rep or {}).get("corners", []):
        if cc["status"] != "pass":
            bad = [m["name"] for m in cc["measurements"] if m.get("status") not in ("pass", None)]
            codes = sorted({d["code"] for d in cc.get("diagnostics", []) if d["code"] != "measurement"})
            what = f"diagnostics {', '.join(codes)} (no measurement values)" if cc["status"] == "error" \
                else ", ".join(bad[:6])
            failed.append(f"- {c['id']} {cc['corner_id']}: {cc['status']} {what}")
L += ["## Failing / erroring corners (kept)", ""] + (failed or ["- none"]) + [""]

# ---- control cross-check against the main-baseline record
L += [f"## Control cross-check against `records/{CONTROL_REC}` (main `5c4eac5`)", "",
      "| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |", "|---|---|---:|---:|"]
for tag, cid in (("tx_sizing_ffe0_wcs", LIM), ("tx_sizing_ffe1_wcs", LIM),
                 ("tx_sizing_ffe0_typ", "typ/1.200V/27C"), ("tx_sizing_ffe1_typ", "typ/1.200V/27C")):
    p = tx / "records" / CONTROL_REC / f"{tag}.report.json"
    ctl = None
    if p.exists():
        cc = corner(json.loads(p.read_text()), cid)
        ctl = None if cc is None else rc.val(cc, "r4_steady_hi") - rc.val(cc, "r4_steady_lo")
    mine = None
    rep = report("ctl")
    if rep and tag.startswith("tx_sizing_ffe0") and tag.endswith(proc):
        cc = corner(rep, cid)
        mine = None if cc is None else rc.val(cc, "r4_steady_hi") - rc.val(cc, "r4_steady_lo")
    L.append(f"| {tag} | {cid} | {mv(ctl)} | {mv(mine)} |")
L += ["", "## Run", "- " + "; ".join(rc.exit_codes(out)), ""]
(out / "record.md").write_text("\n".join(L) + "\n")
print(f"wrote {out / 'record.md'}")
