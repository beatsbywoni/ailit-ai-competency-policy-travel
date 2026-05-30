#!/usr/bin/env python3
"""leave_one_out.py — Phase 2 robustness module 2 (planning §7.10).

Hypothesis under test
---------------------
The Hellinger K=2 cluster {KR, IE} (Tool-use deviating signature) versus
{everyone else} (canonical System-Design signature) is robust to dropping
the largest single document from each country. Specifically:

  1. For KR and IE: dropping their largest doc still leaves them in
     Cluster 1 (S08-dominant tool-use cluster).
  2. For each canonical country: dropping their largest doc does NOT move
     them into Cluster 1.

Method
------
For each country c with ≥ 2 documents:
  a. Identify the largest doc d_max (most aligned sentences).
  b. Recompute the country's 12-anchor distribution using all docs *except*
     d_max — call this the LOO row.
  c. Compute dominant aspect (A1..A4).
  d. Compute Hellinger distance to the cluster-1 centroid ({KR, IE} mean)
     and to the cluster-2 centroid (mean of all canonical countries).
  e. Assign country to cluster whichever centroid is closer.

Output
------
  data/robustness/loo_v2_summary.csv  — per-country LOO result
  data/robustness/loo_v1_summary.csv  — sensitivity
  data/robustness/loo_v2_report.md    — interpretation

Usage
-----
python scripts/04_robustness/leave_one_out.py             # v2
python scripts/04_robustness/leave_one_out.py --tag v1    # sensitivity
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

ASPECT_OF = {
    **{f"AILIT-S0{i}": "A1 HCM" for i in [1, 2, 3]},
    **{f"AILIT-S0{i}": "A2 Ethics" for i in [4, 5, 6]},
    **{f"AILIT-S0{i}": "A3 Tech" for i in [7, 8, 9]},
    **{f"AILIT-S{i:02d}": "A4 SysDes" for i in [10, 11, 12]},
}

# Cluster identity hypothesis: deviating cluster = KR + IE
DEVIATING_ISO = {"KR", "IE"}


def hellinger(p: np.ndarray, q: np.ndarray) -> float:
    """Hellinger distance between two probability vectors."""
    p = p / max(p.sum(), 1e-12)
    q = q / max(q.sum(), 1e-12)
    return float(np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v2", choices=["v1", "v2"])
    parser.add_argument("--min-aligned", type=int, default=50,
                        help="exclude countries with total_aligned < this "
                             "from the cluster centroid computation only "
                             "(default 50; protects AE n=7, AU n=42)")
    args = parser.parse_args()

    suffix = f"_{args.tag}"
    align_path = ALIGN_DIR / f"sprint1_alignment_full{suffix}.jsonl"
    if not align_path.exists():
        sys.stderr.write(f"[error] {align_path} not found.\n")
        return 1

    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchor_ids = [r["anchor_id"] for r in csv.DictReader(f)]

    # Read alignment: per-(doc, anchor) counts
    doc_counts: dict[tuple[str, str], int] = defaultdict(int)
    doc_totals: dict[str, int] = defaultdict(int)
    doc_country: dict[str, str] = {}
    with align_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            doc_counts[(r["doc_id"], r["anchor_id"])] += 1
            doc_totals[r["doc_id"]] += 1
            doc_country[r["doc_id"]] = r["iso2"]

    docs_by_country: dict[str, list[str]] = defaultdict(list)
    for d, iso in doc_country.items():
        docs_by_country[iso].append(d)

    # Country-level raw counts (for centroid computation = full matrix)
    country_counts: dict[tuple[str, str], int] = defaultdict(int)
    country_totals: dict[str, int] = defaultdict(int)
    for (d, a), n in doc_counts.items():
        c = doc_country[d]
        country_counts[(c, a)] += n
        country_totals[c] += n

    isos = sorted(docs_by_country)
    n_anchors = len(anchor_ids)

    # Build full-matrix probability rows for centroid computation
    P_full = np.zeros((len(isos), n_anchors))
    for i, c in enumerate(isos):
        tot = country_totals[c] or 1
        for j, a in enumerate(anchor_ids):
            P_full[i, j] = country_counts[(c, a)] / tot

    # Centroids on the *full* matrix (keep AE/AU out by --min-aligned)
    eligible_isos = [c for c in isos if country_totals[c] >= args.min_aligned]
    eligible_idx = [isos.index(c) for c in eligible_isos]
    P_eligible = P_full[eligible_idx]

    deviating_idx = [eligible_isos.index(c) for c in DEVIATING_ISO if c in eligible_isos]
    canonical_idx = [i for i in range(len(eligible_isos)) if i not in deviating_idx]
    cent_dev = P_eligible[deviating_idx].mean(axis=0)
    cent_can = P_eligible[canonical_idx].mean(axis=0)

    print(f"[centroids] computed from {len(eligible_isos)} countries "
          f"(deviating n={len(deviating_idx)}: {[eligible_isos[i] for i in deviating_idx]})")
    print()

    # LOO per country
    rows = []
    print(f"{'iso':<4s} {'drop_doc':<13s} {'drop_n':>6s} {'kept_n':>7s} "
          f"{'orig_dom':<10s} {'loo_dom':<10s} {'orig_cl':>7s} {'loo_cl':>6s} {'flip?':>5s}")
    for iso in isos:
        docs = docs_by_country[iso]
        if len(docs) < 2:
            print(f"{iso:<4s} {'n/a (1 doc)':<13s} {'':>6s} {country_totals[iso]:>7d}  "
                  f"-- LOO undefined for single-doc countries --")
            continue
        # Largest doc
        d_max = max(docs, key=lambda d: doc_totals[d])
        kept = [d for d in docs if d != d_max]

        # LOO row
        loo_counts = np.zeros(n_anchors)
        for d in kept:
            for j, a in enumerate(anchor_ids):
                loo_counts[j] += doc_counts[(d, a)]
        loo_total = loo_counts.sum()
        if loo_total == 0:
            print(f"{iso:<4s} {d_max:<13s} {doc_totals[d_max]:>6d} {0:>7d}  -- LOO empty --")
            continue
        loo_row = loo_counts / loo_total

        # Aspect dominant — original vs LOO
        def dom(row_pct: np.ndarray) -> str:
            agg = defaultdict(float)
            for j, a in enumerate(anchor_ids):
                agg[ASPECT_OF[a]] += row_pct[j]
            return max(agg, key=agg.get)
        orig_dom = dom(P_full[isos.index(iso)])
        loo_dom = dom(loo_row)

        # Cluster assignment by closest centroid (Hellinger)
        def cluster_of(row_pct: np.ndarray) -> int:
            d_dev = hellinger(row_pct, cent_dev)
            d_can = hellinger(row_pct, cent_can)
            return 1 if d_dev < d_can else 2
        orig_cl = cluster_of(P_full[isos.index(iso)])
        loo_cl = cluster_of(loo_row)

        flip = "Y" if loo_cl != orig_cl else ""
        rows.append({
            "iso": iso,
            "drop_doc": d_max,
            "drop_n": doc_totals[d_max],
            "kept_n": int(loo_total),
            "orig_dom": orig_dom,
            "loo_dom": loo_dom,
            "orig_cluster": orig_cl,
            "loo_cluster": loo_cl,
            "flipped": flip,
        })
        print(f"{iso:<4s} {d_max:<13s} {doc_totals[d_max]:>6d} {int(loo_total):>7d}  "
              f"{orig_dom:<10s} {loo_dom:<10s} {orig_cl:>7d} {loo_cl:>6d} {flip:>5s}")

    # Persist
    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = ROBUST_DIR / f"loo_summary{suffix}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n[out] {out_csv}")

    # Summary statistics
    n_total = len(rows)
    n_flip = sum(1 for r in rows if r["flipped"])
    kr_row = next((r for r in rows if r["iso"] == "KR"), None)
    ie_row = next((r for r in rows if r["iso"] == "IE"), None)
    print(f"\n[summary] {n_total} countries with ≥ 2 docs; {n_flip} flipped clusters")
    if kr_row:
        print(f"  KR: drop {kr_row['drop_doc']} ({kr_row['drop_n']} sents) → "
              f"cluster {kr_row['orig_cluster']} → {kr_row['loo_cluster']} "
              f"{'(KR holds in cluster 1)' if kr_row['loo_cluster']==1 else '(KR LEAVES cluster 1)'}")
    if ie_row:
        print(f"  IE: drop {ie_row['drop_doc']} ({ie_row['drop_n']} sents) → "
              f"cluster {ie_row['orig_cluster']} → {ie_row['loo_cluster']} "
              f"{'(IE holds in cluster 1)' if ie_row['loo_cluster']==1 else '(IE LEAVES cluster 1)'}")

    # Report
    md = ["# Leave-one-out per country — Phase 2 robustness module 2",
          "",
          f"Source: `{align_path.name}`. For each country with ≥ 2 documents, drop the largest single document and reassign to either Cluster 1 ({{KR, IE}}) or Cluster 2 (canonical) by closest Hellinger-centroid.",
          "",
          "## Per-country table",
          "",
          "| iso | drop_doc | drop_n | kept_n | orig_dom | loo_dom | orig_cluster | loo_cluster | flipped |",
          "|---|---|---:|---:|---|---|---:|---:|---|"]
    for r in rows:
        md.append(f"| {r['iso']} | {r['drop_doc']} | {r['drop_n']} | {r['kept_n']} | "
                  f"{r['orig_dom']} | {r['loo_dom']} | {r['orig_cluster']} | "
                  f"{r['loo_cluster']} | {r['flipped'] or 'no'} |")
    md += ["",
           "## Interpretation",
           "",
           f"- {n_flip} / {n_total} countries flipped cluster assignment after LOO.",
           f"- KR LOO outcome: {'preserved in Cluster 1' if kr_row and kr_row['loo_cluster']==1 else 'lost Cluster 1'}",
           f"- IE LOO outcome: {'preserved in Cluster 1' if ie_row and ie_row['loo_cluster']==1 else 'lost Cluster 1'}",
           "",
           "If KR and IE preserve Cluster 1 *and* no canonical country joins, the K=2 partition is robust to single-document dominance — the main empirical claim of the manuscript stands."]
    (ROBUST_DIR / f"loo_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
