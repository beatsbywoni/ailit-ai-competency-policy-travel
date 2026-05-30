#!/usr/bin/env python3
"""sprint0_gate.py — evaluate planning §10.1 decision gate.

Decision criterion (planning v1 §10.1):
- *Green* (scale immediately): tool-use anchors (Aspect 3, especially S08)
  attract >= 3x the share of ethics anchors (Aspect 2) in 4 of 5 pilot
  countries.
- *Yellow* (investigate): pattern present but heterogeneous.
- *Red*: no clear asymmetry; revisit anchors or threshold.

Reads pilot_5x12_pct.csv produced by build_adherence_matrix.py. Writes
docs/sprint0_decision.md with the per-country asymmetry table and a
verdict.

Usage
-----
python scripts/03_analysis/sprint0_gate.py
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PCT = REPO / "data" / "adherence_matrix" / "pilot_5x12_pct.csv"
OUT = REPO / "docs" / "sprint0_decision.md"

ASPECT_3_TOOL_USE = ["AILIT-S07", "AILIT-S08", "AILIT-S09"]  # AI techniques and applications
ASPECT_2_ETHICS = ["AILIT-S04", "AILIT-S05", "AILIT-S06"]    # Ethics of AI
HEADLINE_S08 = "AILIT-S08"                                    # Apply tools — headline indicator


def main() -> int:
    if not PCT.exists():
        print(f"[error] {PCT} not found")
        return 1
    rows = []
    with PCT.open(newline="", encoding="utf-8") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append(r)

    table_rows = []
    n_meet_3x = 0
    n_meet_strong = 0
    for r in rows:
        iso = r["key"]
        tool = sum(float(r[a]) for a in ASPECT_3_TOOL_USE)
        ethics = sum(float(r[a]) for a in ASPECT_2_ETHICS)
        s08 = float(r[HEADLINE_S08])
        ratio_tool_ethics = (tool / ethics) if ethics > 0 else float("inf")
        ratio_s08_ethics = (s08 / ethics) if ethics > 0 else float("inf")
        if ratio_tool_ethics >= 3:
            n_meet_3x += 1
        if ratio_s08_ethics >= 3:
            n_meet_strong += 1
        table_rows.append({
            "iso": iso,
            "tool_pct": tool,
            "ethics_pct": ethics,
            "s08_pct": s08,
            "ratio_tool_ethics": ratio_tool_ethics,
            "ratio_s08_ethics": ratio_s08_ethics,
            "total_aligned": int(r["total_aligned"]),
        })

    if n_meet_3x >= 4:
        verdict = "GREEN"
        verdict_long = "Scale to Sprint 1. Tool-use anchors attract ≥ 3× ethics anchors in 4+ countries; asymmetry hypothesis (planning §3 RQ2) provisionally confirmed at pilot scale."
    elif n_meet_3x >= 2:
        verdict = "YELLOW"
        verdict_long = "Investigate before scaling. Asymmetry pattern present but heterogeneous. Check threshold sensitivity (0.30 / 0.40), country-specific outliers, and corpus depth (esp. UK and SG landing-page extraction)."
    else:
        verdict = "RED"
        verdict_long = "Revisit anchors before scaling. No clear asymmetry signal at threshold 0.35. Check anchor distance matrix, threshold sweep, and whether short landing-page documents (GB-01..04, SG-02, SG-03) are starving the signal."

    today = datetime.utcnow().strftime("%Y-%m-%d")
    md = [
        "# Sprint 0 decision memo",
        "",
        f"**Date**: {today}",
        f"**Threshold**: 0.35 (planning §7.3 default)",
        f"**Pilot scope**: 5 countries × 12 UNESCO student anchors",
        f"**Source**: `data/adherence_matrix/pilot_5x12_pct.csv`",
        "",
        "## Per-country asymmetry table",
        "",
        "| Country | Tool-use share (S07–S09, %) | Ethics share (S04–S06, %) | Tool ÷ Ethics | S08 only ÷ Ethics | Total aligned |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in table_rows:
        md.append(
            f"| {r['iso']} | {r['tool_pct']:.1f} | {r['ethics_pct']:.1f} | "
            f"{r['ratio_tool_ethics']:.2f} | {r['ratio_s08_ethics']:.2f} | {r['total_aligned']:,} |"
        )
    md += [
        "",
        f"**Countries with tool ÷ ethics ≥ 3.0**: {n_meet_3x} / {len(table_rows)}",
        f"**Countries with S08 alone ÷ ethics ≥ 3.0**: {n_meet_strong} / {len(table_rows)}",
        "",
        f"## Verdict — **{verdict}**",
        "",
        verdict_long,
        "",
        "## Next actions",
        "",
        "1. Update `docs/sprint0_progress.md` with this verdict.",
        "2. If GREEN: begin Sprint 1 — full 25-country corpus harvest (§10.2).",
        "3. If YELLOW: run threshold sweep (`04_robustness/threshold_sensitivity.py`), strengthen GB and SG corpora by fetching attached PDFs from landing pages.",
        "4. If RED: revisit anchor wording (consider lifting the OECD 'Managing AI' framing into the primary set, or splitting S08 into separate Application-vs-Workforce sub-anchors).",
        "",
        "## Caveat",
        "",
        "Sprint 0 pilot uses thin landing-page extraction for several UK and Singapore documents (GB-01..04 each ≤ 1.3KB extracted; SG-02..03 ≤ 4.5KB). Per-country signal for these documents is correspondingly weak and may overstate or understate true alignment patterns. Sprint 1 corpus harvest will fetch attached PDFs from landing pages, which is expected to roughly 10× the per-country sentence count for UK and SG and reduce noise in the asymmetry ratios.",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"[out] {OUT}")
    print()
    print(f"Verdict: {verdict}")
    print(f"  Countries meeting tool ÷ ethics ≥ 3×: {n_meet_3x} / {len(table_rows)}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
