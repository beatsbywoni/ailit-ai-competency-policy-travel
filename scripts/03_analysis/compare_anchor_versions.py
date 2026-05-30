#!/usr/bin/env python3
"""compare_anchor_versions.py — side-by-side v1 vs v2 anchor result comparison.

Sprint 0.5 acceptance helper. Reads:
- data/validation/anchor_cohesion_v1.csv
- data/validation/anchor_cohesion_v2.csv
- data/adherence_matrix/pilot_5x12_pct_v1.csv
- data/adherence_matrix/pilot_5x12_pct_v2.csv

Produces:
- data/adherence_matrix/anchor_version_comparison.md
  including (i) cohesion diff table for S04/S05/S06 (and any other changed
  anchor), (ii) per-country bifurcation diff (which dominant aspect each
  country has, v1 vs v2), and (iii) a Path A pass/borderline/fail verdict.

Usage
-----
python scripts/03_analysis/compare_anchor_versions.py
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
VAL = REPO / "data" / "validation"
ADH = REPO / "data" / "adherence_matrix"
OUT = ADH / "anchor_version_comparison.md"

# UNESCO student aspects
ASPECT_OF = {
    "AILIT-S01": "A1 HCM", "AILIT-S02": "A1 HCM", "AILIT-S03": "A1 HCM",
    "AILIT-S04": "A2 Ethics", "AILIT-S05": "A2 Ethics", "AILIT-S06": "A2 Ethics",
    "AILIT-S07": "A3 Tech",   "AILIT-S08": "A3 Tech",   "AILIT-S09": "A3 Tech",
    "AILIT-S10": "A4 SysDes", "AILIT-S11": "A4 SysDes", "AILIT-S12": "A4 SysDes",
}
A2 = ["AILIT-S04", "AILIT-S05", "AILIT-S06"]
A3 = ["AILIT-S07", "AILIT-S08", "AILIT-S09"]


def load_cohesion(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    out = {}
    with path.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["framework"] != "UNESCO-student":
                continue
            out[r["anchor_id"]] = r
    return out


def load_pct(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def dominant_aspect(row: dict) -> tuple[str, float]:
    asums: dict[str, float] = {"A1 HCM": 0, "A2 Ethics": 0,
                                "A3 Tech": 0, "A4 SysDes": 0}
    for aid, a in ASPECT_OF.items():
        asums[a] += float(row.get(aid, 0))
    top = max(asums.items(), key=lambda kv: kv[1])
    return top[0], top[1]


def main() -> int:
    coh_v1 = load_cohesion(VAL / "anchor_cohesion_v1.csv")
    coh_v2 = load_cohesion(VAL / "anchor_cohesion_v2.csv")
    pct_v1 = load_pct(ADH / "pilot_5x12_pct_v1.csv")
    pct_v2 = load_pct(ADH / "pilot_5x12_pct_v2.csv")

    if not coh_v1 or not coh_v2:
        sys.stderr.write("[error] missing cohesion CSVs. Run anchor_distance_check.py for both v1 and v2.\n")
        return 1
    if not pct_v1 or not pct_v2:
        sys.stderr.write("[error] missing pct matrices. Run 07_embed_and_align.py + build_adherence_matrix.py for both v1 and v2.\n")
        return 1

    md = ["# Anchor v1 vs v2 — side-by-side comparison",
          "",
          f"Sprint 0.5 Path A verification. Generated from `data/validation/anchor_cohesion_v{{1,2}}.csv` and `data/adherence_matrix/pilot_5x12_pct_v{{1,2}}.csv`.",
          "",
          "## Cohesion change (UNESCO student anchors)",
          "",
          "| Anchor | Aspect | v1 ratio | v2 ratio | Δ | v2 flag |",
          "|---|---|---:|---:|---:|---|"]
    threshold_pass = 1.10
    s4_5_6_pass = 0
    s4_5_6_fail = 0
    for aid in sorted(coh_v1.keys()):
        v1 = coh_v1[aid]
        v2 = coh_v2.get(aid, {})
        r1 = float(v1["cohesion_ratio"])
        r2 = float(v2.get("cohesion_ratio", "nan"))
        delta = r2 - r1
        flag = "✓" if r2 >= threshold_pass else ("borderline" if r2 >= 1.0 else "OVER_RECRUIT")
        if aid in A2:
            if r2 >= threshold_pass:
                s4_5_6_pass += 1
            elif r2 < 1.0:
                s4_5_6_fail += 1
        md.append(f"| {aid} | {ASPECT_OF[aid]} | {r1:.3f} | {r2:.3f} | {delta:+.3f} | {flag} |")

    # Per-country bifurcation stability
    md += ["",
           "## Per-country bifurcation — dominant aspect v1 vs v2",
           "",
           "| Country | v1 dominant | v1 % | v2 dominant | v2 % | T÷E v1 | T÷E v2 |",
           "|---|---|---:|---|---:|---:|---:|"]
    v1_by_iso = {r["key"]: r for r in pct_v1}
    v2_by_iso = {r["key"]: r for r in pct_v2}
    countries = sorted(set(v1_by_iso) & set(v2_by_iso))
    n_cluster_flips = 0
    for c in countries:
        d1, p1 = dominant_aspect(v1_by_iso[c])
        d2, p2 = dominant_aspect(v2_by_iso[c])
        flipped = " ⚠ FLIP" if d1 != d2 else ""
        if d1 != d2:
            n_cluster_flips += 1
        t1 = sum(float(v1_by_iso[c][a]) for a in A3)
        e1 = sum(float(v1_by_iso[c][a]) for a in A2)
        t2 = sum(float(v2_by_iso[c][a]) for a in A3)
        e2 = sum(float(v2_by_iso[c][a]) for a in A2)
        r1 = (t1/e1) if e1 > 0 else float("inf")
        r2 = (t2/e2) if e2 > 0 else float("inf")
        md.append(f"| {c} | {d1} | {p1:.1f} | {d2}{flipped} | {p2:.1f} | {r1:.2f} | {r2:.2f} |")

    # Verdict
    if s4_5_6_fail > 0:
        verdict = "FAIL — Path A insufficient; escalate to Path B (split S04/S06 → 4 narrower anchors)"
    elif s4_5_6_pass == len(A2):
        verdict = "PASS — Path A succeeded for all three Ethics anchors. Enter Sprint 1 with v2 anchors active."
    else:
        verdict = "PARTIAL — Path A succeeded for some but not all Ethics anchors. Enter Sprint 1 with v2 anchors active; report borderline anchors in §4.6 robustness."

    md += ["",
           "## Verdict",
           "",
           verdict,
           "",
           f"- S04/S05/S06 cohesion-pass count (ratio ≥ {threshold_pass:.2f}): **{s4_5_6_pass} / 3**",
           f"- S04/S05/S06 still OVER_RECRUIT (ratio < 1.00): **{s4_5_6_fail} / 3**",
           f"- Country dominant-aspect flips between v1 and v2: **{n_cluster_flips} / {len(countries)}**",
           "",
           "Interpretation:",
           "- 0 cluster flips → 3-cluster bifurcation is robust to anchor revision (manuscript §4.6 robustness).",
           "- 1–2 flips → noteworthy but acceptable; describe which countries flip and why (likely anchor-cohesion-driven).",
           "- 3+ flips → unstable; reconsider both anchor wording AND cluster interpretation."]

    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"[out] {OUT}")
    print()
    # Console summary
    print("S04/S05/S06 cohesion (v1 → v2):")
    for aid in A2:
        r1 = float(coh_v1[aid]["cohesion_ratio"])
        r2 = float(coh_v2[aid]["cohesion_ratio"])
        marker = "✓" if r2 >= threshold_pass else ("?" if r2 >= 1.0 else "⚠")
        print(f"  {aid}  {r1:.3f} → {r2:.3f}  {marker}")
    print()
    print(f"Cluster flips across {len(countries)} countries: {n_cluster_flips}")
    print()
    print(f"Verdict: {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
