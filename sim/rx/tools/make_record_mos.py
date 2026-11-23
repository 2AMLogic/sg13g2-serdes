"""Render record.md for a sim/rx/records/<id>-mos/ directory from its klt sim report.

Covers the lvl_cml2cmos request (issue #241, evidence gate G3): the MOS level
converter driven by the latch it loads in design/rx/rx_top.spice. Reads only that
directory, sim/rx/lvl_cml2cmos.request.json, sim/pdk.json, layout/toolchain.json
and the exported netlists (for hashes); writes record.md beside the report.
Corners that fail, error or never reach a level are kept and listed.
Sizing evidence only.
"""
import json
import pathlib
import re
import sys

out = pathlib.Path(sys.argv[1])
rx = out.parent.parent
repo = rx.parent.parent
sys.path.insert(0, str(repo / "sim" / "tools"))
import record_common as rc  # noqa: E402

pdk, tool = rc.load_pins(repo)
val, sha = rc.val, rc.sha
NAME = "lvl_cml2cmos"
PS = 1e12
deck = (rx / f"{NAME}.sp").read_text()
req = json.loads((rx / f"{NAME}.request.json").read_text())
spec = {m["name"]: m for m in req["measurements"]}
LIM = spec["lvl_tck_lh90_s"]["limits"]["max"] * PS


def thres(node):
    """Fraction of vdd that threshold node `node` compares d0 against (deck B source)."""
    line = re.search(r"^B%s \S+ 0 V=v\(d0\)-([0-9.]+)\*v\(vdd\)$" % node, deck, re.M)
    return float(line.group(1))


HI, LO = thres("n90"), thres("n10")
LOAD = re.search(r"^Cd0 d0 0 (\S+)$", deck, re.M).group(1)


def pct(x):
    return f"{100 * x:.0f} %"


LOAD_F = LOAD.rstrip("f") + " fF"

L = [f"# RX MOS-cell sizing record {out.name}", "",
     rc.SIZING_BANNER + " Simulated at schematic level: no extracted parasitics (the cell has no",
     "layout), ideal clock and data sources. No `spec/` row is graded here. The limits in the request are",
     "first-look bounds that grade this record only; DR-008 item 3 leaves the converter unsized and",
     "unspecified.", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}` (layout/toolchain.json)",
     f"- `sim/rx/{NAME}.sp` sha256 `{sha(rx / (NAME + '.sp'))}`, `{NAME}.request.json` sha256 "
     f"`{sha(rx / (NAME + '.request.json'))}`",
     "- netlists, via `.include`: " + ", ".join(
         f"`design/rx/netlists/{c}.spice` sha256 "
         f"`{sha(repo / 'design' / 'rx' / 'netlists' / (c + '.spice'))}`"
         for c in ("latch_cml", "clk_buf_quad", "lvl_cml2cmos")),
     "- Circuit: the `latch_regen` deck (clock buffer + `latch_cml`) with one `lvl_cml2cmos` on `qp`/`qn`, "
     "as `Xlvl_d0` sits on `Xlat_d0` in `design/rx/netlists/rx_top.spice`. `Xlvl_d180`, `Xlvl_e90` and "
     "`Xlvl_e270` are the same cell on equivalent latch outputs (same clock amplitude and buffering), "
     "so this one instance stands for the four.",
     "- Input stimulus: ideal 5 GHz four-phase clock, +-150 mV per phase about 0.8333 vdd, ideal quadrature "
     "and 50 % duty; +-10 mV differential data toggling every 400 ps. The latch output `qp`/`qn` is "
     "therefore the 1010 stream of a 5 Gb/s per-wire sampler output (200 ps per bit, the fastest toggle "
     "the converter sees) at the latch's own swing and common mode, both read per corner in the table.",
     f"- Load: {LOAD_F} on `d0` to ground, an assumption (the CMOS deserializer behind the converter does "
     "not exist yet); the same lumped load as the TX clock-converter bench.",
     "- Corner set: 5 MOS process corners (tt/ff/ss/fs/sf) x 1.08/1.2/1.32 V x -40/27/125 C = 45 corners. "
     "Each MOS corner is ganged with an HBT / CAP / RES section as in `sim/tx/make_tb.py` "
     "(tt_typ, ff_bcs, ss_wcs, fs_typ, sf_typ), so the latch moves with the converter. Mismatch and "
     "Monte Carlo are not run.",
     "- Models: MOS is PSP103 through `osdi_preload` (psp103, psp103_nqs, r3_cmc, mosvar); the HBT is "
     "ngspice's built-in `npn13G2`; the latch and clock-buffer resistors are the ideal `res` of "
     "`design/rx` (the CAP / RES sections are ganged for the TX pairing and act on nothing here).",
     "- Parasitics source: none. Schematic netlists, lumped load, no extracted or estimated interconnect.",
     "- Applicable requirement: none is defined for this cell (DR-008 item 3; R2 leaves the level "
     f"conversion open, DR-014 gate G3). First-look bounds used instead: the output reaches {pct(HI)} of "
     f"vdd high and {pct(LO)} of vdd low, within {LIM:.0f} ps of the hold edge that regenerates the bit "
     "(half the 5 GHz clock period, the `latch_regen` limit: the time to the next sample phase).",
     ""]

rep, msg = rc.report_or_error(out, NAME)
codes = [l for l in rc.exit_codes(out) if l.startswith(NAME)]
L += ["## Run",
      f"- command: `cd sim/rx && klt sim --format json --wait-for-capacity 900 --report-out "
      f"records/{out.name}/{NAME}.report.json {NAME}.request.json`",
      f"- {codes[0] if codes else 'no exit code recorded'} (3 = a first-look limit failed; the report "
      "is complete)"]
if rep is None:
    L += [f"- NO REPORT: {msg}", ""]
    (out / "record.md").write_text("\n".join(L) + "\n")
    print(f"make_record_mos.py: wrote {out / 'record.md'} (no report)")
    sys.exit(0)

env = rep["environment"]
rem = env.get("remote") or {}
L += [f"- status **{rep['status']}** ({rep['passed']}/{rep['corner_count']} corners pass, {rep['failed']} "
      f"fail, {rep['errored']} error, {rep.get('not_reached', 0)} measurements `not_reached`); engine "
      f"{env.get('engine_host')}, ngspice {env.get('engine_version')}"
      + (f", backend job `{rem['job_id']}`" if rem.get("job_id") else ""), ""]

corners = sorted(rep["corners"], key=lambda k: k["corner_id"])


def ps(c, a, b=None):
    """(t_a - t_b) in ps over two absolute crossings, or None if either was not reached."""
    x, y = val(c, a), (0.0 if b is None else val(c, b))
    return None if x is None or y is None else (x - y) * PS


def f(x, fmt="{:.1f}", none="not reached"):
    return none if x is None else fmt.format(x)


rows = []
no_high, low_high, never10, slow_lh, slow_hl, clean = [], [], [], [], [], []
for c in corners:
    cid = c["corner_id"]
    vdd = c["supply_v"]["vdd"]
    hi, lo = val(c, "lvl_out_hi_v"), val(c, "lvl_out_lo_v")
    t_lh, t_hl = val(c, "lvl_tck_lh90_s"), val(c, "lvl_tck_hl10_s")
    if hi is not None and hi < 0.5 * vdd:
        why = f"no high level: out hi {hi:.3f} V < vdd/2"
        no_high.append(cid)
        t_hl = None
    else:
        why = []
        if t_lh is None:
            low_high.append(cid)
            why.append(f"LH edge stops at {hi:.3f} V, under {pct(HI)} of vdd")
        elif t_lh * PS > LIM:
            slow_lh.append(cid)
            why.append(f"hold edge to {pct(HI)} LH {t_lh * PS:.1f} ps > {LIM:.0f} ps")
        if t_hl is None:
            never10.append(cid)
            why.append(f"HL edge stops at {lo:.3f} V, over {pct(LO)} of vdd")
        elif t_hl * PS > LIM:
            slow_hl.append(cid)
            why.append(f"hold edge to {pct(LO)} HL {t_hl * PS:.1f} ps > {LIM:.0f} ps")
        if not why:
            clean.append(cid)
        why = "ok" if not why else "; ".join(why)
    rows.append((c, vdd, t_lh, t_hl, why))

L += [f"## lvl_cml2cmos (latch-driven, 5 Gb/s 1010 per wire, {LOAD_F} load)", "",
      "`tpd` is from the latch differential output `q = v(qp) - v(qn)` crossing zero (which happens "
      "during the latch's sample phase) to `d0` crossing vdd/2. `hold->` is from the clock edge that "
      "closes the sample phase (`ck` falling, the edge the `latch_regen` record measures from) to `d0` "
      f"reaching {pct(HI)} (LH) or {pct(LO)} (HL) of vdd; those two carry the {LIM:.0f} ps first-look limit. "
      f"`tr`/`tf` are the {pct(LO)}-{pct(HI)} output edges and `high`/`low` the time `d0` spends above and "
      "below vdd/2 for one bit (200 ps each at the input). `q swing` and `q CM` are the latch output the "
      "converter actually saw, its input gates being the only extra load on the latch. `Idd` is the "
      "converter's own supply current (through `Vddc`), averaged over 2-3 ns.", "",
      "| corner | q swing (V) | q CM (V) | out hi (V) | out lo (V) | tpd LH (ps) | tpd HL (ps) | "
      f"hold->{pct(HI)} LH (ps) | hold->{pct(LO)} HL (ps) | tr / tf (ps) | high / low (ps) | Idd (mA) | verdict |",
      "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for c, vdd, t_lh, t_hl, why in rows:
    qs = None if val(c, "lvl_q_max_v") is None or val(c, "lvl_q_min_v") is None else \
        val(c, "lvl_q_max_v") - val(c, "lvl_q_min_v")
    qc = None if val(c, "lvl_qp_hi_v") is None or val(c, "lvl_qp_lo_v") is None else \
        0.5 * (val(c, "lvl_qp_hi_v") + val(c, "lvl_qp_lo_v"))
    L.append(f"| {c['corner_id']} | {f(qs, '{:.2f}')} | {f(qc, '{:.3f}')} | "
             f"{f(val(c, 'lvl_out_hi_v'), '{:.3f}')} | {f(val(c, 'lvl_out_lo_v'), '{:.3f}')} | "
             f"{f(ps(c, 'lvl_t_out_rise_s', 'lvl_t_q_rise_s'))} | {f(ps(c, 'lvl_t_out_fall_s', 'lvl_t_q_fall_s'))} | "
             f"{f(None if t_lh is None else t_lh * PS)} | {f(None if t_hl is None else t_hl * PS, none='n/a')} | "
             f"{f(ps(c, 'lvl_t_out_hi90_s', 'lvl_t_out_rise10_s'))} / "
             f"{f(ps(c, 'lvl_t_out_lo10_s', 'lvl_t_out_fall90_s'))} | "
             f"{f(ps(c, 'lvl_t_out_fall_s', 'lvl_t_out_rise_s'))} / "
             f"{f(ps(c, 'lvl_t_out_rise2_s', 'lvl_t_out_fall_s'))} | "
             f"{f(None if val(c, 'lvl_idd_avg') is None else val(c, 'lvl_idd_avg') * 1e3, '{:.3f}')} | {why} |")
L.append("")


def span(items):
    return f"{min(items)[0]:.1f} ps ({min(items)[1]}) to {max(items)[0]:.1f} ps ({max(items)[1]})" if items else "none"


reached_lh = [(t * PS, c["corner_id"]) for c, _, t, _, _ in rows if t is not None]
reached_hl = [(t * PS, c["corner_id"]) for c, _, _, t, _ in rows if t is not None]
by_v = {}
for c, vdd, _, _, _ in rows:
    by_v.setdefault(vdd, []).append(c["corner_id"] in clean)
L += ["## Reading the grid", "",
      "- Corners where `d0` never rose above vdd/2 in the window (the converter did not switch high): "
      f"**{len(no_high)}**" + (" -- " + ", ".join(no_high) if no_high else "") + ".",
      f"- Corners where `d0` crossed vdd/2 but the LH edge stopped under {pct(HI)} of vdd: "
      f"**{len(low_high)}**" + (" -- " + ", ".join(low_high) if low_high else "") + ".",
      f"- Corners whose HL edge never came down to {pct(LO)} of vdd: "
      f"**{len(never10)}**" + (" -- " + ", ".join(never10) if never10 else "") + ".",
      f"- Corners over the {LIM:.0f} ps first-look limit, hold edge to {pct(HI)} LH: "
      f"**{len(slow_lh)}**" + (" -- " + ", ".join(slow_lh) if slow_lh else "") + ".",
      f"- Corners over the {LIM:.0f} ps first-look limit, hold edge to {pct(LO)} HL: "
      f"**{len(slow_hl)}**" + (" -- " + ", ".join(slow_hl) if slow_hl else "") + ".",
      f"- Corners inside both first-look limits with full levels: **{len(clean)} of {len(corners)}**"
      + (" -- " + ", ".join(clean) if clean else "") + ".",
      f"- Hold edge to {pct(HI)} LH, over the {len(reached_lh)} corners that reached it: {span(reached_lh)}.",
      f"- Hold edge to {pct(LO)} HL, over the {len(reached_hl)} corners that reached it: {span(reached_hl)}."]
for vdd in sorted(by_v):
    L.append(f"- At {vdd:.2f} V: {sum(by_v[vdd])} of {len(by_v[vdd])} corners inside both first-look limits.")
L.append("")

why_of = {c["corner_id"]: why for c, _, _, _, why in rows}
bad = [c for c in corners if c.get("status") not in ("pass", "ok")]
L += ["## Failing or erroring corners (kept, not dropped)", ""]
for c in bad:
    if c.get("status") == "error":
        d = (c.get("diagnostics") or [{}])[0]
        L.append(f"- {c['corner_id']}: error {d.get('code') or ''} "
                 f"{(d.get('message') or '')[:240]}".rstrip())
    else:
        L.append(f"- {c['corner_id']}: {c.get('status')} -- {why_of[c['corner_id']]}")
L.append(f"- {len(bad)} of {len(corners)} corners are graded other than `pass`; the per-corner cause is "
         "the `verdict` column above. Corners graded `pass`: "
         + (", ".join(c["corner_id"] for c in corners if c.get("status") in ("pass", "ok")) or "none") + ".")
L.append("")

L += ["## What this record does not establish", "",
      "- Post-layout timing. The cell has no layout; no extracted parasitics, no wire model, no supply "
      "or ground network, no supply isolation between the CML and CMOS rails.",
      "- The load the converter will actually drive. 20 fF is an assumption; the deserializer that "
      "follows `d0`, `d180`, `e90`, `e270` is not implemented, so its input capacitance, its setup time "
      "and the valid window it needs are unknown.",
      "- A pass against a requirement. The converter has none; the limits here are first-look bounds, and "
      "a corner inside them is not evidence that the converter meets R2 or any other row.",
      "- The latch's own limits. Where the latch does not regenerate enough swing (`latch_regen`, record "
      "20261114-050716-eb34d10: six 1.080 V corners under 0.25 V peak |q|) the converter sees that "
      "swing; `q swing` shows it per corner so the cause stays visible.",
      "- Mismatch, Monte Carlo, sampler offset, noise, jitter or data patterns other than 1010 per wire.",
      ""]
(out / "record.md").write_text("\n".join(L) + "\n")
print(f"make_record_mos.py: wrote {out / 'record.md'}")
