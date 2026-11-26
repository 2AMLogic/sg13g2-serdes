"""Render record.md for a sim/tx/records/<id>-r4sweep-<proc>*/ directory (issue #286).

Reads the per-candidate klt sim reports written by run_r4sweep.sh (<out>/batch/<stem>/
report.json, stem r4sweep_<cand>_<proc>), the candidate table and, as the control
cross-check, the main-baseline FFE-off / all-slices-on reports of the issue #242 record.
Failing, erroring and missing corners are kept and listed. Sizing evidence only: the
tables report what was simulated and make no claim beyond the tested range. Exit 2
after writing the record when a report, corner or measurement is incomplete.
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
candidates = {c["id"]: c for c in json.loads((tx / "r4sweep_candidates.json").read_text())}
manifest_path = out / "batch" / "set-manifest.json"
if manifest_path.is_file():
    filenames = [item["request"] for item in json.loads(manifest_path.read_text())["requests"]]
else:
    # klt can stop before writing its manifest. The runner saves its exact input list.
    filenames = (out / "requests.txt").read_text().splitlines()
if not filenames:
    sys.exit("Empty R4 sweep manifest")

CANDS = []
reports = {}
requests = {}
for filename in filenames:
    name = pathlib.Path(filename).name
    cand = name.removeprefix("r4sweep_").removesuffix(f"_{proc}.request.json")
    CANDS.append(candidates[cand])
    requests[cand] = json.loads((tx / name).read_text())
    path = out / "batch" / name.removesuffix(".request.json") / "report.json"
    if path.is_file():
        reports[cand] = json.loads(path.read_text())


def corner(rep, cid):
    for c in rep.get("corners", []):
        if c["corner_id"] == cid:
            return c
    return None


def number(value, scale=1, digits=3):
    return "n/a" if value is None else f"{scale * value:.{digits}f}"


def mv(value):
    return number(value, 1000, 1)


def difference(cc, high, low):
    hi, lo = rc.val(cc, high), rc.val(cc, low)
    return None if hi is None or lo is None else hi - lo


def static(cc):
    return difference(cc, "r4_steady_hi", "r4_steady_lo")


def stress_text(worst):
    return "n/a" if worst is None else f"{worst[0]:.3f} ({worst[1]}, {worst[2]})"



def r3_worst(c, driver):
    """Smallest R3 margin (limit - value) over the driver_ffe cards (driver=True) or the
    predriver / bias cards (driver=False) in the corner, with its name."""
    best = None
    for m in c.get("measurements", []):
        if m["name"].startswith(("vc_max_", "vce_max_", "vbe_rev_max_")) and m.get("value") is not None and m.get("margin") is not None:
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
     f"- Repository klt pin: `{tool['klt_last_verified_commit']}`. Executed versions are in report provenance.",
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
      "XQTM Ic / Ie mA | tail Vce min mV | pair Vce min V | R7 rise/fall ps | vs 500 mV | vs 300 mV |",
      "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for c in CANDS:
    cc = corner(reports.get(c["id"], {}), PLIM) or {}
    st = static(cc)
    pr = difference(cc, "r4_prbs_run_hi", "r4_prbs_run_lo")
    pp = difference(cc, "r4_prbs_max_v", "r4_prbs_min_v")
    ic = rc.val(cc, "tail_ic_main_a")
    ie = rc.val(cc, "tail_ie_main_a")
    if ie is None:
        ie = rc.val(cc, "tail_i_main_a")  # Historical REM sense card measured emitter current.
    pair = [rc.val(cc, f"vce_min_drv_pair_{leg}") for leg in ("p", "n")]
    pv = min(pair) if None not in pair else None
    rise = number(rc.val(cc, "r7_rise_20_80_s"), 1e12, 1)
    fall = number(rc.val(cc, "r7_fall_80_20_s"), 1e12, 1)
    L.append(f"| {c['id']} | {1000*c['dvb_v']:+.0f} | {c['rt_length_scale']:.2f} | {mv(st)} | {mv(pr)} | "
             f"{mv(pp)} | {number(ic, 1000, 2)} / {number(ie, 1000, 2)} | "
             f"{mv(rc.val(cc, 'vce_min_drv_tail_main'))} | {number(pv)} | {rise}/{fall} | "
             f"{mv(None if st is None else st - 0.5)} | {mv(None if st is None else st - 0.3)} |")
L.append("")

# ---- R3 over all corners
L += [f"## R3 stress over the {proc} corners (3 supplies x 3 temperatures, includes 1.32 V)", "",
      "Extrema use available measurements. Gaps are listed below.", "",
      "| candidate | corners pass/fail/error/missing | smallest driver_ffe R3 margin V (card, corner) | "
      "smallest predriver/bias R3 margin V (card, corner) | min static mVppd (corner) | "
      f"{proc} 1.20 V / 27 C static mVppd |", "|---|---|---|---|---|---|"]
failed = []
incomplete = False
for c in CANDS:
    cand = c["id"]
    req = requests[cand]
    grid = req["corners"]
    expected = [f"{proc}/{v:.3f}V/{temp}C" for v in grid["supply_v"]["vdd"] for temp in grid["temperature_c"]]
    rep = reports.get(cand)
    if rep is None:
        incomplete = True
        failed.append(f"- {cand}: missing report for all {len(expected)} requested corners.")
        L.append(f"| {cand} | 0/0/0/{len(expected)} (missing report) | n/a | n/a | n/a | n/a |")
        continue

    cards = {m["name"] for m in req["measurements"]}
    if any(m["name"] == "tail_i_main_a" for m in rep.get("measurements", [])):
        cards -= {"tail_ic_main_a", "tail_ie_main_a"}
        cards.add("tail_i_main_a")
    worst, worstp, mn = None, None, None
    counts = {"pass": 0, "fail": 0, "error": 0, "missing": 0}
    for cid in expected:
        cc = corner(rep, cid)
        if cc is None:
            counts["missing"] += 1
            failed.append(f"- {cand} {cid}: missing corner.")
            incomplete = True
            continue
        status = cc["status"]
        counts[status] = counts.get(status, 0) + 1
        ms = cc.get("measurements", [])
        if status == "error":
            codes = sorted({d["code"] for d in cc.get("diagnostics", []) if d["code"] != "measurement"})
            failed.append(f"- {cand} {cid}: error ({', '.join(codes) or 'see report'}).")
            incomplete = True
        else:
            if status != "pass":
                bad = [m["name"] for m in ms if m.get("status") not in ("pass", None)]
                failed.append(f"- {cand} {cid}: {status} ({', '.join(bad) or 'see report'}).")
            missing = cards - {m["name"] for m in ms if m.get("value") is not None}
            if missing:
                failed.append(f"- {cand} {cid}: missing measurements: {', '.join(sorted(missing))}.")
                incomplete = True
        w = r3_worst(cc, True)
        if w and (worst is None or w[0] < worst[0]):
            worst = (*w, cid)
        w = r3_worst(cc, False)
        if w and (worstp is None or w[0] < worstp[0]):
            worstp = (*w, cid)
        st = static(cc)
        if st is not None and (mn is None or st < mn[0]):
            mn = (st, cid)
    count_text = "/".join(str(counts[k]) for k in ("pass", "fail", "error", "missing"))
    for status in sorted(counts.keys() - {"pass", "fail", "error", "missing"}):
        count_text += f" + {counts[status]} {status}"
        incomplete = True
    ref = static(corner(rep, f"{proc}/1.200V/27C") or {})
    min_text = f"{mv(mn[0])} ({mn[1]})" if mn else "n/a"
    L.append(f"| {cand} | {count_text} | {stress_text(worst)} | {stress_text(worstp)} | {min_text} | {mv(ref)} |")
L += ["", "## Failing, errored or missing data", ""] + (failed or ["- none"]) + [""]

# ---- control cross-check against the main-baseline record
L += [f"## Control cross-check against `records/{CONTROL_REC}` (main `5c4eac5`)", "",
      "| set | corner | recorded static mVppd (hi - lo) | this record, `ctl` |", "|---|---|---:|---:|"]
for tag, cid in (("tx_sizing_ffe0_wcs", LIM), ("tx_sizing_ffe1_wcs", LIM),
                 ("tx_sizing_ffe0_typ", "typ/1.200V/27C"), ("tx_sizing_ffe1_typ", "typ/1.200V/27C")):
    p = tx / "records" / CONTROL_REC / f"{tag}.report.json"
    ctl = None
    if p.exists():
        cc = corner(json.loads(p.read_text()), cid)
        ctl = static(cc or {})
    mine = None
    rep = reports.get("ctl")
    if rep and tag.startswith("tx_sizing_ffe0") and tag.endswith(proc):
        cc = corner(rep, cid)
        mine = static(cc or {})
    L.append(f"| {tag} | {cid} | {mv(ctl)} | {mv(mine)} |")
L += ["", "## Run", "- " + "; ".join(rc.exit_codes(out)), ""]
(out / "record.md").write_text("\n".join(L) + "\n")
print(f"wrote {out / 'record.md'}")
if incomplete:
    sys.exit(2)  # record.md was written, but some requested data is unavailable.
