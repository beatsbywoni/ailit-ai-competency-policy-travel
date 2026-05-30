#!/usr/bin/env python3
"""anchor_distance_check.py — 21×21 anchor cosine matrix + cohesion report.

Planning §7.10 construct-validity step, executed for the Sprint 0 anchor set.
For each anchor we compute:
- mean_within = mean cosine similarity to other anchors in the same aspect
  (student) or in the same framework (teacher, OECD)
- mean_between = mean cosine similarity to anchors in *other* aspects within
  the same framework
- cohesion_ratio = mean_within / mean_between

Convention: ratio > 1.0 means the anchor sits inside its aspect cluster more
tightly than it relates to outside-aspect anchors — i.e., it is cohesive.
Ratio < 1.0 flags an anchor that semantically blurs into other aspects and
will over-recruit foreign-aspect sentences in the alignment step.

Outputs
-------
data/validation/anchor_distance_matrix_21x21.csv  full matrix
data/validation/anchor_cohesion.csv                per-anchor metrics
data/validation/anchor_cohesion_report.md          human-readable summary

Usage
-----
python scripts/05_validation/anchor_distance_check.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    sys.stderr.write("[error] sentence-transformers not installed.\n")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
ANCHOR_DIR = REPO / "anchors"
OUT_DIR = REPO / "data" / "validation"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

DEFAULT_STUDENT_CSV = ANCHOR_DIR / "unesco_ai_student_2024.csv"


def load_all_anchors(student_csv: Path | None = None) -> list[dict]:
    rows: list[dict] = []
    sp = student_csv or DEFAULT_STUDENT_CSV
    with sp.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "anchor_id": r["anchor_id"],
                "framework": "UNESCO-student",
                "group": r["aspect"],
                "level": r["level"],
                "sentence": r["anchor_sentence"],
            })
    with (ANCHOR_DIR / "unesco_ai_teacher_2024.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "anchor_id": r["anchor_id"],
                "framework": "UNESCO-teacher",
                "group": r["aspect"],
                "level": "",
                "sentence": r["anchor_sentence"],
            })
    with (ANCHOR_DIR / "oecd_ai_literacy_2025.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "anchor_id": r["anchor_id"],
                "framework": "OECD",
                "group": r["domain"],
                "level": "",
                "sentence": r["anchor_sentence"],
            })
    return rows


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--student-csv", type=Path, default=None,
                        help="override student-anchor CSV path")
    parser.add_argument("--tag", default="",
                        help="suffix appended to outputs (e.g. 'v1', 'v2')")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.tag}" if args.tag else ""
    anchors = load_all_anchors(args.student_csv)
    n = len(anchors)
    print(f"[load] {n} anchors  (student_csv={args.student_csv or DEFAULT_STUDENT_CSV.name})")

    print(f"[init] {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    emb = model.encode(
        [a["sentence"] for a in anchors],
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    sim = emb @ emb.T  # (n, n), values in [-1, 1]

    # Write the full matrix
    matrix_path = OUT_DIR / f"anchor_distance_matrix_21x21{suffix}.csv"
    with matrix_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + [a["anchor_id"] for a in anchors])
        for i, a in enumerate(anchors):
            w.writerow([a["anchor_id"]] + [f"{sim[i, j]:.4f}" for j in range(n)])

    # Per-anchor cohesion
    coh_rows = []
    for i, a in enumerate(anchors):
        same_group_idx = [j for j, b in enumerate(anchors)
                          if j != i
                          and b["framework"] == a["framework"]
                          and b["group"] == a["group"]]
        diff_group_idx = [j for j, b in enumerate(anchors)
                          if j != i
                          and b["framework"] == a["framework"]
                          and b["group"] != a["group"]]
        within = float(np.mean(sim[i, same_group_idx])) if same_group_idx else float("nan")
        between = float(np.mean(sim[i, diff_group_idx])) if diff_group_idx else float("nan")
        ratio = (within / between) if between and not np.isnan(between) else float("nan")
        worst_match = None
        if diff_group_idx:
            worst_j = diff_group_idx[int(np.argmax(sim[i, diff_group_idx]))]
            worst_match = (anchors[worst_j]["anchor_id"], float(sim[i, worst_j]))
        flag = ""
        if not np.isnan(ratio):
            if ratio < 1.0:
                flag = "OVER_RECRUIT"
            elif ratio < 1.1:
                flag = "borderline"
        coh_rows.append({
            "anchor_id": a["anchor_id"],
            "framework": a["framework"],
            "group": a["group"],
            "mean_within_group": round(within, 4),
            "mean_between_group": round(between, 4),
            "cohesion_ratio": round(ratio, 3) if not np.isnan(ratio) else "nan",
            "worst_cross_group_match": worst_match[0] if worst_match else "",
            "worst_cross_group_score": round(worst_match[1], 4) if worst_match else "",
            "flag": flag,
        })

    coh_path = OUT_DIR / f"anchor_cohesion{suffix}.csv"
    with coh_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(coh_rows[0].keys()))
        w.writeheader()
        w.writerows(coh_rows)

    # Markdown report
    md = [
        "# Anchor cohesion report",
        "",
        f"21 anchors across 3 frameworks. Cosine similarity from `{MODEL_NAME}`, L2-normalised.",
        "",
        "**Interpretation rules**:",
        "- `cohesion_ratio = mean_within_group / mean_between_group`",
        "- `> 1.10`: cohesive anchor — sits closer to in-group anchors than out-group",
        "- `1.00–1.10`: borderline",
        "- `< 1.00`: **OVER_RECRUIT** — anchor blurs into other groups; expect alignment to over-attract foreign-group sentences",
        "",
        "## Per-anchor cohesion (UNESCO student aspects)",
        "",
        "| Anchor | Group | within | between | ratio | worst cross-group match | flag |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for r in coh_rows:
        if r["framework"] == "UNESCO-student":
            md.append(
                f"| {r['anchor_id']} | {r['group']} | {r['mean_within_group']} | "
                f"{r['mean_between_group']} | {r['cohesion_ratio']} | "
                f"{r['worst_cross_group_match']} ({r['worst_cross_group_score']}) | {r['flag']} |"
            )
    md += [
        "",
        "## Per-anchor cohesion (UNESCO teacher aspects)",
        "",
        "| Anchor | Group | within | between | ratio | worst cross-group match | flag |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for r in coh_rows:
        if r["framework"] == "UNESCO-teacher":
            md.append(
                f"| {r['anchor_id']} | {r['group']} | {r['mean_within_group']} | "
                f"{r['mean_between_group']} | {r['cohesion_ratio']} | "
                f"{r['worst_cross_group_match']} ({r['worst_cross_group_score']}) | {r['flag']} |"
            )
    md += [
        "",
        "## Per-anchor cohesion (OECD/EC domains)",
        "",
        "| Anchor | Group | within | between | ratio | worst cross-group match | flag |",
        "|---|---|---:|---:|---:|---|---|",
    ]
    for r in coh_rows:
        if r["framework"] == "OECD":
            md.append(
                f"| {r['anchor_id']} | {r['group']} | {r['mean_within_group']} | "
                f"{r['mean_between_group']} | {r['cohesion_ratio']} | "
                f"{r['worst_cross_group_match']} ({r['worst_cross_group_score']}) | {r['flag']} |"
            )

    flagged = [r["anchor_id"] for r in coh_rows if r["flag"] == "OVER_RECRUIT"]
    borderline = [r["anchor_id"] for r in coh_rows if r["flag"] == "borderline"]
    md += [
        "",
        "## Summary",
        "",
        f"- **Cohesive** (ratio ≥ 1.10): {len([r for r in coh_rows if isinstance(r['cohesion_ratio'], float) and r['cohesion_ratio'] >= 1.10])}",
        f"- **Borderline** (1.00 ≤ ratio < 1.10): {len(borderline)} → {', '.join(borderline) if borderline else 'none'}",
        f"- **Over-recruiting** (ratio < 1.00): {len(flagged)} → {', '.join(flagged) if flagged else 'none'}",
        "",
        "## Action",
        "",
        ("If any UNESCO student anchor is OVER_RECRUIT, that anchor needs rewording or "
         "splitting before Sprint 1. Inflated A2 (Ethics) share in the §10.1 verdict is "
         "the most likely artefact." if flagged or borderline else
         "All anchors cohesive. Sprint 0 §10.1 verdict reflects substantive policy patterns, "
         "not anchor-cohesion artefacts."),
    ]
    md_path = OUT_DIR / f"anchor_cohesion_report{suffix}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")

    # Console summary
    print()
    print(f"[out] {matrix_path}")
    print(f"[out] {coh_path}")
    print(f"[out] {md_path}")
    print()
    print("Per-anchor ratio (sorted ascending — bottom = most problematic):")
    sortable = [r for r in coh_rows if isinstance(r["cohesion_ratio"], float)]
    sortable.sort(key=lambda r: r["cohesion_ratio"])
    for r in sortable:
        marker = "  ⚠" if r["flag"] == "OVER_RECRUIT" else ("  ?" if r["flag"] == "borderline" else "")
        print(f"  {r['anchor_id']:<10s}  {r['group'][:28]:<28s}  ratio={r['cohesion_ratio']:5.2f}{marker}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
