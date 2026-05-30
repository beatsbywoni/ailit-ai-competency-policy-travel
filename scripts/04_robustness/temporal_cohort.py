#!/usr/bin/env python3
"""temporal_cohort.py — Phase 2 robustness module 5 (C&E IV.6).

Pre-UNESCO (published before 2024-09) vs post-UNESCO (after) cohort split.

Why this matters
----------------
A reviewer might argue that the {KR, IE} Tool-use cluster is an artefact of
*timing* — countries with policies drafted before the UNESCO 2024 release
cannot reference the framework's competency vocabulary. We test whether
the K = 2 partition holds inside each temporal cohort taken in isolation,
ruling out the timing-artefact alternative.

Method
------
For each cohort (pre, post):
  1. Build the country × 12-anchor matrix from only that cohort's
     documents (per the inventory `unesco_cohort` column).
  2. Compute Hellinger distances on countries with ≥ 50 cohort-restricted
     aligned sentences.
  3. Compute K = 2 assignment using {KR, IE} as the deviating-cluster
     centroid (using the full-data K = 2 partition as the reference
     ground truth).
  4. Report which countries change cluster between cohorts.

Outputs
-------
data/robustness/cohort_pre_25x12_pct_v{tag}.csv      pre-only matrix
data/robustness/cohort_post_25x12_pct_v{tag}.csv     post-only matrix
data/robustness/cohort_summary_v{tag}.csv             per-country comparison
data/robustness/cohort_report_v{tag}.md               interpretation

Usage
-----
python scripts/04_robustness/temporal_cohort.py --tag v2
python scripts/04_robustness/temporal_cohort.py --tag v1
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ALIGN_DIR = REPO / "data" / "adherence_matrix"
ROBUST_DIR = REPO / "data" / "robustness"
ANCHOR_CSV = REPO / "anchors" / "unesco_ai_student_2024.csv"
INVENTORY = REPO / "data" / "corpus_inventory" / "sprint1_urls.csv"

DEVIATING_ISO = {"KR", "IE"}
MIN_N = 50

ASPECT_OF = {
    **{f"AILIT-S0{i}": "A1 HCM" for i in [1, 2, 3]},
    **{f"AILIT-S0{i}": "A2 Ethics" for i in [4, 5, 6]},
    **{f"AILIT-S0{i}": "A3 Tech" for i in [7, 8, 9]},
    **{f"AILIT-S{i:02d}": "A4 SysDes" for i in [10, 11, 12]},
}


def hellinger(p: np.ndarray, q: np.ndarray) -> float:
    p = p / max(p.sum(), 1e-12)
    q = q / max(q.sum(), 1e-12)
    return float(np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v2", choices=["v1", "v2"])
    args = parser.parse_args()

    suffix = f"_{args.tag}"
    align_path = ALIGN_DIR / f"sprint1_alignment_full{suffix}.jsonl"
    if not align_path.exists():
        sys.stderr.write(f"[error] {align_path} not found.\n")
        return 1

    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchor_ids = [r["anchor_id"] for r in csv.DictReader(f)]
    anchor_idx = {a: i for i, a in enumerate(anchor_ids)}
    n_anchors = len(anchor_ids)

    # Inventory: doc_id → cohort
    doc_cohort: dict[str, str] = {}
    with INVENTORY.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["url"].startswith("DROP:"):
                continue
            doc_cohort[r["doc_id"]] = r["unesco_cohort"]
    print(f"[inventory] doc-cohort mapping for {len(doc_cohort)} docs")

    # Build per-(country, cohort, anchor) counts
    counts: dict[tuple[str, str, str], int] = defaultdict(int)  # (iso, cohort, anchor) -> n
    country_cohort_total: dict[tuple[str, str], int] = defaultdict(int)
    cohort_country: dict[str, set] = defaultdict(set)
    with align_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            doc = r["doc_id"]
            iso = r["iso2"]
            if doc not in doc_cohort:
                continue
            ch = doc_cohort[doc]
            counts[(iso, ch, r["anchor_id"])] += 1
            country_cohort_total[(iso, ch)] += 1
            cohort_country[ch].add(iso)

    # Build cohort matrices
    matrices: dict[str, dict[str, np.ndarray]] = {}
    for ch in ["pre", "post"]:
        isos = sorted(cohort_country[ch])
        M = {}
        for iso in isos:
            tot = country_cohort_total[(iso, ch)] or 1
            row = np.zeros(n_anchors)
            for j, a in enumerate(anchor_ids):
                row[j] = counts[(iso, ch, a)] / tot
            M[iso] = (row, country_cohort_total[(iso, ch)])
        matrices[ch] = M

    # Determine centroids per cohort (KR/IE = deviating, others ≥ MIN_N = canonical)
    def centroids(mat: dict[str, tuple[np.ndarray, int]]) -> tuple[np.ndarray, np.ndarray, list, list]:
        eligible = [(iso, row) for iso, (row, n) in mat.items() if n >= MIN_N]
        dev = [row for iso, row in eligible if iso in DEVIATING_ISO]
        can = [row for iso, row in eligible if iso not in DEVIATING_ISO]
        dev_c = np.mean(dev, axis=0) if dev else np.zeros(n_anchors)
        can_c = np.mean(can, axis=0) if can else np.zeros(n_anchors)
        return dev_c, can_c, [iso for iso, _ in eligible if iso in DEVIATING_ISO], [iso for iso, _ in eligible if iso not in DEVIATING_ISO]

    # Full-data reference (from the existing matrix)
    full_path = ALIGN_DIR / f"sprint1_25x12_pct{suffix}.csv"
    full_pct = {}
    with full_path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row = np.array([float(r[a]) / 100.0 for a in anchor_ids])
            full_pct[r["key"]] = (row, int(r["total_aligned"]))
    full_dev_c, full_can_c, full_dev_isos, full_can_isos = centroids(full_pct)

    def cluster(row: np.ndarray, dev_c: np.ndarray, can_c: np.ndarray) -> int:
        return 1 if hellinger(row, dev_c) < hellinger(row, can_c) else 2
    full_cluster = {iso: cluster(row, full_dev_c, full_can_c) for iso, (row, _) in full_pct.items()}

    # Cohort centroids + assignments
    print(f"\n[cohort PRE]  countries with ≥ 1 pre-doc: {len(matrices['pre'])}; "
          f"≥ {MIN_N} aligned: {len([iso for iso, (_, n) in matrices['pre'].items() if n >= MIN_N])}")
    print(f"[cohort POST] countries with ≥ 1 post-doc: {len(matrices['post'])}; "
          f"≥ {MIN_N} aligned: {len([iso for iso, (_, n) in matrices['post'].items() if n >= MIN_N])}")
    print()

    cohort_clusters: dict[str, dict[str, int]] = {}
    for ch in ["pre", "post"]:
        dev_c, can_c, dev_isos, can_isos = centroids(matrices[ch])
        print(f"[centroids {ch}] dev cluster anchored by: {dev_isos}; canonical n={len(can_isos)}")
        cohort_clusters[ch] = {}
        for iso, (row, n) in matrices[ch].items():
            if n < MIN_N:
                continue
            cohort_clusters[ch][iso] = cluster(row, dev_c, can_c)

    # Per-country comparison
    all_isos = sorted(set(matrices["pre"]) | set(matrices["post"]) | set(full_pct))
    rows = []
    print(f"\n{'iso':<4s} {'pre_n':>6s} {'pre_cl':>7s} {'post_n':>7s} {'post_cl':>8s} {'full_cl':>8s}  {'note':<20s}")
    for iso in all_isos:
        pre_n = matrices["pre"].get(iso, (None, 0))[1]
        post_n = matrices["post"].get(iso, (None, 0))[1]
        pre_cl = cohort_clusters["pre"].get(iso, "-")
        post_cl = cohort_clusters["post"].get(iso, "-")
        full_cl = full_cluster.get(iso, "-")
        # Note: only countries with n ≥ MIN_N in BOTH cohorts get a real comparison
        if isinstance(pre_cl, int) and isinstance(post_cl, int):
            note = "agree" if pre_cl == post_cl else "DISAGREE"
        else:
            missing = []
            if pre_n < MIN_N: missing.append(f"pre n={pre_n}<50")
            if post_n < MIN_N: missing.append(f"post n={post_n}<50")
            note = "; ".join(missing)
        rows.append({
            "iso": iso,
            "pre_n": pre_n,
            "pre_cluster": pre_cl,
            "post_n": post_n,
            "post_cluster": post_cl,
            "full_cluster": full_cl,
            "note": note,
        })
        print(f"{iso:<4s} {pre_n:>6d} {str(pre_cl):>7s} {post_n:>7d} {str(post_cl):>8s} {str(full_cl):>8s}  {note:<20s}")

    # Summary: focal countries
    print(f"\n[focal] KR: pre={cohort_clusters['pre'].get('KR', '—')}, post={cohort_clusters['post'].get('KR', '—')}, full={full_cluster.get('KR')}")
    print(f"        IE: pre={cohort_clusters['pre'].get('IE', '—')}, post={cohort_clusters['post'].get('IE', '—')}, full={full_cluster.get('IE')}")
    both_eligible = [iso for iso in all_isos
                     if matrices['pre'].get(iso, (None, 0))[1] >= MIN_N
                     and matrices['post'].get(iso, (None, 0))[1] >= MIN_N]
    agree = sum(1 for iso in both_eligible if cohort_clusters['pre'].get(iso) == cohort_clusters['post'].get(iso))
    print(f"\n[summary] countries with ≥ {MIN_N} sents in BOTH cohorts: {len(both_eligible)}; "
          f"pre-cohort cluster matches post-cohort cluster for {agree}/{len(both_eligible)} ({agree/max(len(both_eligible),1)*100:.0f}%)")

    # Persist matrices and summary
    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    for ch in ["pre", "post"]:
        out_csv = ROBUST_DIR / f"cohort_{ch}_25x12_pct{suffix}.csv"
        with out_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["key"] + anchor_ids + ["total_aligned"])
            for iso, (row, n) in matrices[ch].items():
                w.writerow([iso] + [round(row[j] * 100, 2) for j in range(n_anchors)] + [n])

    summary_path = ROBUST_DIR / f"cohort_summary{suffix}.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n[out] {summary_path}")

    md = [f"# Temporal cohort split (pre/post UNESCO 2024-09) — Module 5",
          "",
          f"Source: `{align_path.name}` ({args.tag}). Cohort assigned per `data/corpus_inventory/sprint1_urls.csv` `unesco_cohort` column. Country-level matrices built separately for each cohort; Hellinger clustering with K = 2 reference centroids (KR + IE vs canonical, with `--min-aligned {MIN_N}` filter).",
          "",
          "## Per-country pre vs post cohort cluster",
          "",
          "| iso | pre n | pre cluster | post n | post cluster | full cluster | note |",
          "|---|---:|---:|---:|---:|---:|---|"]
    for r in rows:
        md.append(f"| {r['iso']} | {r['pre_n']} | {r['pre_cluster']} | {r['post_n']} | "
                  f"{r['post_cluster']} | {r['full_cluster']} | {r['note']} |")
    md += ["",
           "## Summary",
           "",
           f"- KR pre-cohort = Cluster {cohort_clusters['pre'].get('KR', '—')}, post-cohort = Cluster {cohort_clusters['post'].get('KR', '—')}",
           f"- IE pre-cohort = Cluster {cohort_clusters['pre'].get('IE', '—')}, post-cohort = Cluster {cohort_clusters['post'].get('IE', '—')}",
           f"- {agree}/{len(both_eligible)} countries with ≥ {MIN_N} sentences in both cohorts preserve their cluster assignment across the temporal split.",
           "",
           "## Interpretation",
           "",
           "If KR and IE preserve Cluster 1 in *both* the pre and post sub-corpora, the K = 2 partition is not a timing artefact. Countries whose policy texts predate UNESCO 2024-09 cannot reference the framework's vocabulary, so any signal that survives the pre cohort comes from independent national choices — and likewise for the post cohort. Agreement in both directions is the test we want."]
    (ROBUST_DIR / f"cohort_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
