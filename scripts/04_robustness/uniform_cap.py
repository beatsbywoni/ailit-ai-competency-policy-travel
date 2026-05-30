#!/usr/bin/env python3
"""uniform_cap.py — Phase 2 robustness module 4 (C&E IV.5).

Most aggressive size-bias correction available in this protocol: cap every
country at N = 500 randomly-sampled aligned sentences (or all sentences if
the country has fewer). Rebuild the 25 × 12 matrix, recompute Hellinger
clustering, check whether the K = 2 partition {KR, IE} vs canonical
survives size-equalisation.

Output (per iteration aggregated)
---------------------------------
- frequency with which each country is assigned to Cluster 1 across 1,000
  uniform-cap resamples (the "Cluster-1 assignment rate")
- aggregate per-country dominant-aspect rate across resamples
- summary: how often the K = 2 partition matches the full-data partition

Outputs
-------
data/robustness/uniform_cap_v{tag}.csv      per-country cluster + dominance rates
data/robustness/uniform_cap_report_v{tag}.md

Usage
-----
python scripts/04_robustness/uniform_cap.py --tag v2 --cap 500 --n-iter 1000
python scripts/04_robustness/uniform_cap.py --tag v1 --cap 500 --n-iter 1000
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

DEVIATING_ISO = {"KR", "IE"}
MIN_N_FOR_CENTROID = 50  # match Hellinger filter; excludes AE, AU

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
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tag", default="v2", choices=["v1", "v2"])
    p.add_argument("--cap", type=int, default=500)
    p.add_argument("--n-iter", type=int, default=1000)
    p.add_argument("--seed", type=int, default=20260530)
    args = p.parse_args()

    suffix = f"_{args.tag}"
    align_path = ALIGN_DIR / f"sprint1_alignment_full{suffix}.jsonl"
    if not align_path.exists():
        sys.stderr.write(f"[error] {align_path} not found.\n")
        return 1

    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchor_ids = [r["anchor_id"] for r in csv.DictReader(f)]
    anchor_idx = {a: i for i, a in enumerate(anchor_ids)}
    n_anchors = len(anchor_ids)

    # Load alignment per country (list of anchor indices)
    country_anchors: dict[str, np.ndarray] = {}
    raw: dict[str, list[int]] = defaultdict(list)
    with align_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            raw[r["iso2"]].append(anchor_idx[r["anchor_id"]])
    for iso, lst in raw.items():
        country_anchors[iso] = np.array(lst, dtype=np.int16)

    isos = sorted(country_anchors)
    rng = np.random.default_rng(args.seed)

    # Build full-data centroids (canonical = ≥ MIN_N AND not in DEVIATING)
    def dist_from_counts(counts: np.ndarray) -> np.ndarray:
        s = counts.sum()
        return counts / s if s > 0 else counts

    full_pct = {}
    for iso, arr in country_anchors.items():
        counts = np.bincount(arr, minlength=n_anchors).astype(float)
        full_pct[iso] = dist_from_counts(counts)
    eligible = [c for c in isos
                if len(country_anchors[c]) >= MIN_N_FOR_CENTROID]
    canonical_full = [c for c in eligible if c not in DEVIATING_ISO]
    deviating_full = [c for c in eligible if c in DEVIATING_ISO]
    cent_dev_full = np.mean([full_pct[c] for c in deviating_full], axis=0)
    cent_can_full = np.mean([full_pct[c] for c in canonical_full], axis=0)

    def assign_cluster(row: np.ndarray, dev_cent: np.ndarray, can_cent: np.ndarray) -> int:
        return 1 if hellinger(row, dev_cent) < hellinger(row, can_cent) else 2

    full_cluster_of = {c: assign_cluster(full_pct[c], cent_dev_full, cent_can_full)
                       for c in isos}

    print(f"[full ] {len(isos)} countries: "
          f"cluster1={[c for c, v in full_cluster_of.items() if v == 1]}, "
          f"cluster2 has {sum(1 for v in full_cluster_of.values() if v == 2)} members")
    print(f"[boot ] cap={args.cap}, n_iter={args.n_iter}")

    # Resampling loop
    cluster1_count = defaultdict(int)
    dominant_aspect_count: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    partition_match_count = 0

    for it in range(args.n_iter):
        # Cap each country
        capped_pct: dict[str, np.ndarray] = {}
        for iso, arr in country_anchors.items():
            n = len(arr)
            if n <= args.cap:
                sample = arr
            else:
                sample = rng.choice(arr, size=args.cap, replace=False)
            counts = np.bincount(sample, minlength=n_anchors).astype(float)
            capped_pct[iso] = dist_from_counts(counts)

        # Centroids from capped distributions (only eligible countries)
        capped_eligible = [c for c in isos if len(country_anchors[c]) >= MIN_N_FOR_CENTROID]
        cap_can = [c for c in capped_eligible if c not in DEVIATING_ISO]
        cap_dev = [c for c in capped_eligible if c in DEVIATING_ISO]
        if not cap_dev or not cap_can:
            continue
        cent_dev = np.mean([capped_pct[c] for c in cap_dev], axis=0)
        cent_can = np.mean([capped_pct[c] for c in cap_can], axis=0)

        # Per-iteration cluster + dominant aspect
        match_this_iter = True
        for iso in isos:
            cl = assign_cluster(capped_pct[iso], cent_dev, cent_can)
            if cl == 1:
                cluster1_count[iso] += 1
            if cl != full_cluster_of[iso]:
                match_this_iter = False
            # dominant aspect
            agg = defaultdict(float)
            for j, a in enumerate(anchor_ids):
                agg[ASPECT_OF[a]] += capped_pct[iso][j]
            dom = max(agg, key=agg.get)
            dominant_aspect_count[iso][dom] += 1
        if match_this_iter:
            partition_match_count += 1

    # Per-country summary
    print(f"\n{'iso':<4s} {'n_full':>7s} {'cl1_rate%':>10s} {'top_dom':<10s} {'top_dom%':>9s} {'full_cl':>8s}")
    rows = []
    for iso in isos:
        n_full = len(country_anchors[iso])
        cl1_rate = cluster1_count[iso] / args.n_iter * 100
        top_dom = max(dominant_aspect_count[iso], key=dominant_aspect_count[iso].get)
        top_dom_rate = dominant_aspect_count[iso][top_dom] / args.n_iter * 100
        rows.append({
            "iso": iso,
            "n_full": n_full,
            "cluster1_rate_pct": round(cl1_rate, 1),
            "full_cluster": full_cluster_of[iso],
            "top_dom_aspect": top_dom,
            "top_dom_rate_pct": round(top_dom_rate, 1),
        })
        print(f"{iso:<4s} {n_full:>7d} {cl1_rate:>9.1f}% {top_dom:<10s} {top_dom_rate:>8.1f}% {full_cluster_of[iso]:>8d}")

    partition_match_rate = partition_match_count / args.n_iter * 100
    print(f"\n[summary] full-data K=2 partition matched in {partition_match_count}/{args.n_iter} "
          f"({partition_match_rate:.1f}%) of resamples")

    # KR/IE focus
    print(f"\n[focal ] KR stays in Cluster 1 in {cluster1_count['KR']}/{args.n_iter} resamples "
          f"({cluster1_count['KR']/args.n_iter*100:.1f}%)")
    print(f"         IE stays in Cluster 1 in {cluster1_count['IE']}/{args.n_iter} resamples "
          f"({cluster1_count['IE']/args.n_iter*100:.1f}%)")
    # Count canonical countries that mistakenly enter cluster 1
    fp = [(c, cluster1_count[c] / args.n_iter * 100) for c in isos
          if full_cluster_of[c] == 2 and cluster1_count[c] > 0]
    if fp:
        print(f"         Canonical → Cluster 1 leak (any rate > 0):")
        for c, r in sorted(fp, key=lambda x: -x[1])[:10]:
            print(f"           {c:<4s}  {r:>5.1f}%")

    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = ROBUST_DIR / f"uniform_cap{suffix}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n[out] {out_csv}")

    md = [f"# Uniform-cap N = {args.cap} sub-sampling — Phase 2 robustness module 4",
          "",
          f"Source: `{align_path.name}` ({args.tag}). Resampling: every country capped at N = {args.cap} aligned sentences per iteration; {args.n_iter} iterations; seed = {args.seed}.",
          "",
          "## Per-country Cluster-1 assignment rate",
          "",
          "| iso | n (full) | Cluster-1 rate | Full-data cluster | Top dominant aspect | Rate |",
          "|---|---:|---:|---:|---|---:|"]
    for r in rows:
        md.append(f"| {r['iso']} | {r['n_full']} | {r['cluster1_rate_pct']} % | "
                  f"{r['full_cluster']} | {r['top_dom_aspect']} | {r['top_dom_rate_pct']} % |")
    md += ["",
           "## Partition stability",
           "",
           f"- Full-data K = 2 partition matched in **{partition_match_count}/{args.n_iter} "
           f"({partition_match_rate:.1f} %)** of uniform-cap resamples.",
           f"- KR stays in Cluster 1: **{cluster1_count['KR']/args.n_iter*100:.1f} %** of iterations.",
           f"- IE stays in Cluster 1: **{cluster1_count['IE']/args.n_iter*100:.1f} %** of iterations.",
           "",
           "## Interpretation",
           "",
           "Uniform-cap is the most aggressive size-equalisation in the IV battery (more so than IV.2 inverse weighting and IV.3 LOO combined). If KR maintains Cluster 1 assignment under uniform cap, the Tool-use deviating signature is *not* an artefact of corpus size. The IE assignment rate quantifies how borderline IE actually is — under aggressive resampling, the IE-01 single-document dependency may push IE's Cluster-1 rate down below KR's."]
    (ROBUST_DIR / f"uniform_cap_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
