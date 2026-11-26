"""Render record.md for a sim/tx/records/<id>-vce/ directory from its klt sim reports.

The R3 per-device Vce pass (issue #242, gate G2 row R3 of tracker #238): the six
tx_sizing HBT requests plus the tx_mos_mux2to1_cml and tx_mos_ffe_en requests --
every TX bench with an HBT in it -- in one record with a per-device table against
the R3 limits (collector <= 1.32 V, Vce <= 1.4 V open-base BVCEO, reverse Vbe
<= 1.0 V). tx_lvl_cml2cmos is not run: it has no HBT, so R3 Vce is not
applicable to it. Reads the reports, the requests, sim/pdk.json and
design/tx/netlists/*.spice (for hashes); writes record.md beside the reports.
Failing, erroring and missing corners are kept and listed. Sizing evidence only.
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
sha = rc.sha

TAGS = ["ffe%d_%s" % (f, t) for f in (0, 1) for t in ("bcs", "typ", "wcs")]
MUX, FFE = "tx_mos_mux2to1_cml", "tx_mos_ffe_en"

# One row per HBT device in a TX bench: (device, request set, vc, vce, vbe_rev)
# measurement names. Collector nodes are shared where two devices hang on the
# same node (e.g. XQM2 and XQP0a both collect at cop), so vc repeats by design.
S = "tx_sizing"
ROWS = [
    ("bias.qref", S, "vc_max_bias_vbn", "vce_max_bias_ref", "vbe_rev_max_bias_ref"),
    ("pre_main.q1", S, "vc_max_pre_main_outn", "vce_max_pre_main_pair_n", "vbe_rev_max_pre_main_p"),
    ("pre_main.q2", S, "vc_max_pre_main_outp", "vce_max_pre_main_pair_p", "vbe_rev_max_pre_main_n"),
    ("pre_main.qt", S, "vc_max_pre_main_tail", "vce_max_pre_main_tail", "vbe_rev_max_pre_main_tail"),
    ("pre_post.q1", S, "vc_max_pre_post_outn", "vce_max_pre_post_pair_n", "vbe_rev_max_pre_post_p"),
    ("pre_post.q2", S, "vc_max_pre_post_outp", "vce_max_pre_post_pair_p", "vbe_rev_max_pre_post_n"),
    ("pre_post.qt", S, "vc_max_pre_post_tail", "vce_max_pre_post_tail", "vbe_rev_max_pre_post_tail"),
    ("driver_ffe.qm1", S, "vc_max_drv_out_n", "vce_max_drv_pair_n", "vbe_rev_max_drv_main_p"),
    ("driver_ffe.qm2", S, "vc_max_drv_out_p", "vce_max_drv_pair_p", "vbe_rev_max_drv_main_n"),
    ("driver_ffe.qtm", S, "vc_max_drv_tail_main", "vce_max_drv_tail_main", "vbe_rev_max_drv_tail_main"),
]
for i in range(3):
    ROWS += [
        ("driver_ffe.qp%da" % i, S, "vc_max_drv_out_p", "vce_max_drv_post%d_p" % i, "vbe_rev_max_drv_post%d_p" % i),
        ("driver_ffe.qp%db" % i, S, "vc_max_drv_out_n", "vce_max_drv_post%d_n" % i, "vbe_rev_max_drv_post%d_n" % i),
        ("driver_ffe.qtp%d" % i, S, "vc_max_drv_tail_post%d" % i, "vce_max_drv_tail_post%d" % i,
         "vbe_rev_max_drv_post%d_tail" % i),
    ]
ROWS += [
    ("mux2to1_cml.qa1", MUX, "vc_max_mux_outn", "vce_max_mux_a1", "vbe_rev_max_mux_a1"),
    ("mux2to1_cml.qa2", MUX, "vc_max_mux_outp", "vce_max_mux_a2", "vbe_rev_max_mux_a2"),
    ("mux2to1_cml.qb1", MUX, "vc_max_mux_outn", "vce_max_mux_b1", "vbe_rev_max_mux_b1"),
    ("mux2to1_cml.qb2", MUX, "vc_max_mux_outp", "vce_max_mux_b2", "vbe_rev_max_mux_b2"),
    ("bias.qref@ffe_en", FFE, "vc_max_ffe_bias", "vce_max_ffe_bias", "vbe_rev_max_ffe_bias"),
]

L = [f"# TX R3 per-device Vce record {out.name}", "",
     rc.SIZING_BANNER + " This is the R3 evidence pass of issue #242 (gate G2, row R3 "
     "of tracker #238): per-device Vce, collector and reverse-Vbe maxima, transient "
     "peaks included, over each bench family's full PVT grid including the +10 % "
     "supply (1.32 V). Nothing here is measured, and no `spec/` row is graded.", "",
     "## Pins and inputs",
     f"- PDK: {pdk['source']} {pdk['release_tag']} (sim/pdk.json), tarball sha256 `{pdk['tarball_sha256']}`",
     f"- klt: `{tool['klt_last_verified_commit']}`"]
for t in TAGS:
    L.append(f"- `tx_sizing_{t}.sp` sha256 `{sha(tx / f'tx_sizing_{t}.sp')}`, "
             f"`tx_sizing_{t}.request.json` sha256 `{sha(tx / f'tx_sizing_{t}.request.json')}`")
for c in (MUX, FFE):
    L.append(f"- `{c}.sp` sha256 `{sha(tx / (c + '.sp'))}`, "
             f"`{c}.request.json` sha256 `{sha(tx / (c + '.request.json'))}`")
for c in ("bias", "predriver", "driver_ffe", "mux2to1_cml", "ffe_en"):
    L.append(f"- netlist `design/tx/netlists/{c}.spice` sha256 "
             f"`{sha(repo / 'design' / 'tx' / 'netlists' / (c + '.spice'))}`")
L.append("- the mux bench also inlines `bias` + `predriver` (main); their HBTs are the "
         "tx_sizing / ffe_en rows above -- the same cells in a loaded context.")
L.append("")

exit_codes = "; ".join(rc.exit_codes(out))
L += ["## Run", f"- {exit_codes}"]
reps, missing = {}, []
for name in TAGS + [MUX, FFE]:
    rep, msg = rc.report_or_error(out, "tx_sizing_" + name if name in TAGS else name)
    if rep is not None:
        reps[name] = rep
    else:
        missing.append((name, msg))
for name, msg in missing:
    L.append(f"- {name}: NO REPORT: {msg}")
corners = {}
for name, rep in reps.items():
    rem = rep["environment"].get("remote") or {}
    L.append(f"- {name}: status **{rep['status']}** ({rep['passed']}/{rep['corner_count']} corners pass, "
             f"{rep.get('failed', 0)} fail, {rep['errored']} error), backend job `{rem.get('job_id')}`")
    corners[name] = rep["corners"]
L.append("")

bad = [(n, k) for n, cs in corners.items() for k in cs if k.get("status") not in ("pass", "ok")]
if bad:
    L += ["## Failing or erroring corners (kept, not dropped)", ""]
    for n, k in sorted(bad, key=lambda t: (t[0], t[1]["corner_id"])):
        d = (k.get("diagnostics") or [{}])[0]
        L.append(f"- {n}/{k['corner_id']}: {k.get('status')} {d.get('code') or ''} "
                 f"{(d.get('message') or '')[:240]}".rstrip())
    L.append("")

val = rc.val


def wmax(name_set, meas):
    """(worst value, corner id) of `meas` over all corners of the named requests."""
    vs = []
    for n in name_set:
        for c in corners.get(n, []):
            v = val(c, meas)
            if v is not None:
                vs.append((v, "%s/%s" % (n, c["corner_id"])))
    return max(vs, key=lambda t: t[0]) if vs else (None, None)


SET_OF = {S: TAGS, MUX: [MUX], FFE: [FFE]}

L += ["## HBT enumeration (design/tx/netlists/*.spice)", "",
      "| cell | HBT devices | instances in tx_top | R3 Vce covered by |",
      "|---|---|---|---|",
      "| `bias` | 1 | 1 | tx_sizing benches; ffe_en bench (re-measured there) |",
      "| `predriver` | 3 | 2 (6 HBTs) | tx_sizing benches (`pre_main`, `pre_post`) |",
      "| `driver_ffe` | 12 | 1 | tx_sizing benches |",
      "| `mux2to1_cml` | 4 | 2 (8 HBTs) | tx_mos_mux2to1_cml |",
      "| `ffe_en` | 0 | 1 | n/a -- MOS and resistors only |",
      "| `tx_lvl_cml2cmos` | 0 | 1 | n/a -- **no HBT, not applicable to R3 Vce**; CMOS-level evidence is G3-class, see `records/20261110-224611-4092fc2-mos/` (45/45 corners) |",
      "| `pad_esd` | 0 | 1 | n/a -- diodes only |",
      "", "- 20 unique HBT devices; 27 HBT instances in `tx_top`. The per-device table below "
      "has 24 rows: the 19 devices of the tx_sizing bench (1 bias + 3 + 3 predriver "
      "instances + 12 driver), the 4 mux HBTs, and the ffe_en bench's bias device.", ""]

L += ["## R3 per-device table (worst over each grid, transient peaks included)", "",
      "Limits: collector <= 1.32 V, Vce <= 1.4 V (open-base BVCEO, DR-003), reverse Vbe "
      "<= 1.0 V. A value over its limit keeps its row -- violations are marked, not "
      "dropped, and not fixed here (out of scope of #242).", "",
      "| device | vc max (V) @ corner | Vce max (V) @ corner | vbe rev max (V) @ corner |",
      "|---|---|---|---|"]
viol = 0
for dev, setname, vc, vce, vb in ROWS:
    row = [dev]
    for meas, lim in ((vc, 1.32), (vce, 1.4), (vb, 1.0)):
        v, cid = wmax(SET_OF[setname], meas)
        if v is None:
            row.append("n/a")
            continue
        over = v > lim
        viol += over
        flag = " **>%.4g**" % lim if over else ""
        row.append(f"{v:.4f}{flag} ({cid})")
    L.append("| " + " | ".join(row) + " |")
L += ["", f"- The per-device table has **{viol}** values above an R3 limit in the recorded grids.", ""]

L += ["## Grids and caveats", "",
      "- tx_sizing (HBT set): hbt typ/bcs/wcs ganged with cap + res and the matching "
      "resistor sheet scale, one process per deck, x 1.08/1.2/1.32 V x -40/27/125 C "
      "= 9 corners per deck, x 6 decks (3 processes x FFE off / all three post "
      "slices on) = 54 corners. tx_mos (mux, ffe_en): 5 MOS "
      "process pairings x 3 supplies x 3 temperatures = 45 corners. Both include the "
      "+10 % supply (1.32 V). Mismatch/Monte Carlo is not run.",
      "- The mux numbers cite the bench's assumed clock swing: 0.4 V per side "
      "(0.8 V differential peak-to-peak), an assumption, not a spec value (#98 is the "
      "open spec question). If #98 changes the swing, the mux rows are re-recorded "
      "after it lands, not before.",
      "- The HBT decks' `rsil` is the behavioural stand-in with the corner sheet scale "
      "(see sim/tx/README.md); the mux and ffe_en decks use the real `r3_cmc` resistors "
      "via `osdi_preload`.",
      "- Collector (`vc_max_*`) is per node, so devices sharing a collector node (e.g. "
      "`driver_ffe.qm2` and `driver_ffe.qp0a` at `cop`) repeat that node's value; Vce "
      "and reverse Vbe are per device.",
      "- Inputs are ideal sources at vdd-referenced CML levels (300 mV), not a real "
      "upstream eye; the pad network per TX leg is the 4 ohm stand-in + extracted "
      "70.66 fF pad-metal C + PDK ESD clamp diodes (issue #142).", ""]
(out / "record.md").write_text("\n".join(L))
print(f"make_record_vce.py: wrote {out / 'record.md'}")
