"""Before/after comparison for issue #266: RX collector-ceiling fix.

    python3 -I sim/rx/tools/compare_records.py <baseline-record> <new-record>

Reads only the two records' klt sim reports and writes <new-record>/comparison.md.
Simulated sizing evidence, never a measurement.
"""
import json
import pathlib
import sys

base, new = (pathlib.Path(a) for a in sys.argv[1:3])


def load(d, n):
    p = d / n
    return json.load(open(p)) if p.exists() else None


def corners(rep):
    return {c["corner_id"]: {m["name"]: m for m in c["measurements"]} for c in rep["corners"]}


def worst(rep, suffix, fn=max):
    best = None
    for cid, ms in corners(rep).items():
        for n, m in ms.items():
            if n.endswith(suffix) and m.get("value") is not None:
                if best is None or fn(m["value"], best[0]) == m["value"] and m["value"] != best[0]:
                    best = (m["value"], cid, n)
    return best


L = ["# Comparison for issue #266: RX collector ceiling", "",
     f"Baseline: `{base.name}`; revised: `{new.name}`. Simulated sizing evidence, not measured.", ""]
L += ["## Worst collector-to-ground (R3 limit 1.32 V) and reverse Vbe (limit 1.0 V), 27 corners", "",
      "| bench | quantity | baseline | revised |", "|---|---|---|---|"]
for bench in ("latch_regen", "ctle_op", "ctle_tran"):
    a, b = load(base, bench + ".report.json"), load(new, bench + ".report.json")
    for suf in ("_vc_max", "_vbe_rev_max", "_vce_max"):
        wa, wb = worst(a, suf), worst(b, suf)
        if wa and wb:
            L.append("| %s | max %s | %.4f V (%s, %s) | %.4f V (%s, %s) |" % (
                bench, suf[1:], wa[0], wa[2], wa[1], wb[0], wb[2], wb[1]))
L += ["", "Per-node worst `vc_max` in the revised latch_regen record (V):", ""]
b = load(new, "latch_regen.report.json")
nodes = {}
for cid, ms in corners(b).items():
    for n, m in ms.items():
        if n.endswith("_vc_max") and m["value"] is not None and m["value"] > nodes.get(n, (0, ""))[0]:
            nodes[n] = (m["value"], cid)
for n, (v, cid) in sorted(nodes.items(), key=lambda x: -x[1][0])[:10]:
    L.append("- `%s` %.4f (%s)" % (n, v, cid))

L += ["", "## Latch regeneration time (ps), baseline -> revised; floor level 0.10 V, decision level 0.25 V", "",
      "| corner | up_lo | dn_lo | up@0.25 | dn@0.25 | q max V |", "|---|---|---|---|---|---|"]
ca, cb = corners(load(base, "latch_regen.report.json")), corners(load(new, "latch_regen.report.json"))
miss_a = miss_b = 0
slow = []


def f(m, s=1e12):
    return "NR" if m["value"] is None else "%.1f" % (m["value"] * s)


for cid in ca:
    a, b = ca[cid], cb[cid]
    miss_a += a["latch_t_regen_up"]["value"] is None
    miss_b += b["latch_t_regen_up"]["value"] is None
    for k in ("latch_t_regen_up_lo", "latch_t_regen_dn_lo"):
        if b[k]["value"] is None or b[k]["value"] > 100e-12:
            slow.append((cid, k))
    L.append("| %s | %s -> %s | %s -> %s | %s -> %s | %s -> %s | %.3f -> %.3f |" % (
        cid, f(a["latch_t_regen_up_lo"]), f(b["latch_t_regen_up_lo"]),
        f(a["latch_t_regen_dn_lo"]), f(b["latch_t_regen_dn_lo"]),
        f(a["latch_t_regen_up"]), f(b["latch_t_regen_up"]),
        f(a["latch_t_regen_dn"]), f(b["latch_t_regen_dn"]),
        a["latch_q_max_v"]["value"], b["latch_q_max_v"]["value"]))
L += ["", "Corners missing the 0.25 V decision level (up edge): baseline %d, revised %d (NR = not reached)." % (miss_a, miss_b),
      "Corners missing the 100 ps floor-level limit in the revised run: %s." % (slow or "none"), ""]

L += ["## R20 clock quality (clk_buf_quad, identical ideal source and 20 fF loads), baseline -> revised", ""]
ra, rb = load(new, "r20_original.report.json"), load(new, "r20_revised.report.json")
oa, ob = corners(ra), corners(rb)
names = sorted(next(iter(oa.values())).keys())
L += ["Measurements: " + ", ".join("`%s`" % n for n in names), ""]
dut = lambda h, p: 100 * abs(h) / p
L += ["| corner | duty A % | duty B % | swing A pp V | swing B pp V |", "|---|---|---|---|---|"]
sw = [n for n in names if "swing" in n or "pp" in n]
for cid in oa:
    a, b = oa[cid], ob[cid]
    def d(x, ha, pa):
        return dut(abs(x[ha]["value"]), x[pa]["value"])
    row = "| %s | %.2f -> %.2f | %.2f -> %.2f |" % (cid, d(a, "r20_high_a_s", "r20_period_a_s"), d(b, "r20_high_a_s", "r20_period_a_s"),
                                                    d(a, "r20_high_b_s", "r20_period_b_s"), d(b, "r20_high_b_s", "r20_period_b_s"))
    row += " " + " | ".join("%s: %.3f -> %.3f" % (n, a[n]["value"], b[n]["value"]) for n in sw[:2]) + " |"
    L.append(row)
open(new / "comparison.md", "w").write("\n".join(L) + "\n")
