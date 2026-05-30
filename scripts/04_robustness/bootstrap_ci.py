#!/usr/bin/env python3
"""bootstrap_ci.py — Phase 2 robustness module 3 (planning §7.9 + C&E IV.4).

Resampling unit: aligned sentences within each country (with replacement,
n = original total per country). 1,000 bootstrap iterations by default.

Computed statistics (all reported with point estimate + percentile 95 % CI)
--------------------------------------------------------------------------
A. Per-country anchor distribution (12 shares) → focal on KR's S08 and
   IE's S08 (the Tool-use signature of Cluster 1).
B. Per-country dominant-aspect agreement rate across bootstrap iterations
   (proxy for cluster stability).
C. Effect sizes (95 % CI on each difference):
   - KR S08 % minus canonical-mean S08 %        ← strength of KR deviation
   - IE S08 % minus canonical-mean S08 %        ← strength of IE deviation
   - IE-01 S08 % minus IE-02 S08 %              ← *intra-IE asymmetry*

(Canonical = all countries except {KR, IE} and the n<50 small-corpus set
{AE, AU}, matching the Hellinger filter.)

Outputs
-------
data/robustness/bootstrap_ci_v{tag}.csv          per-country S08 mean + CI
data/robustness/bootstrap_effects_v{tag}.csv     effect-size table
data/robustness/bootstrap_report_v{tag}.md       interpretation

Usage
-----
python scripts/04_robustness/bootstrap_ci.py --tag v2 --n-boot 1000
python scripts/04_robustness/bootstrap_ci.py --tag v1 --n-boot 1000
python scripts/04_robustness/bootstrap_ci.py --tag v2 --n-boot 200       # quick
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
EXCLUDE_FROM_CANONICAL = DEVIATING_ISO | {"AE", "AU"}  # small-n excluded too


def percentile_ci(samples: np.ndarray, alpha: float = 0.05) -> tuple[float, float]:
    lo = float(np.percentile(samples, 100 * alpha / 2))
    hi = float(np.percentile(samples, 100 * (1 - alpha / 2)))
    return lo, hi


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tag", default="v2", choices=["v1", "v2"])
    p.add_argument("--n-boot", type=int, default=1000)
    p.add_argument("--seed", type=int, default=20260530)
    p.add_argument("--focal-anchor", default="AILIT-S08",
                   help="anchor whose share is bootstrapped per country (default S08 Application skills)")
    args = p.parse_args()

    suffix = f"_{args.tag}"
    align_path = ALIGN_DIR / f"sprint1_alignment_full{suffix}.jsonl"
    if not align_path.exists():
        sys.stderr.write(f"[error] {align_path} not found.\n")
        return 1

    with ANCHOR_CSV.open(encoding="utf-8") as f:
        anchor_ids = [r["anchor_id"] for r in csv.DictReader(f)]
    anchor_idx = {a: i for i, a in enumerate(anchor_ids)}
    if args.focal_anchor not in anchor_idx:
        sys.stderr.write(f"[error] focal anchor {args.focal_anchor} not in anchor list\n")
        return 1
    focal_j = anchor_idx[args.focal_anchor]

    # Load alignment — per country, list of anchor indices (one per sentence)
    country_anchors: dict[str, list[int]] = defaultdict(list)
    doc_anchors: dict[str, list[int]] = defaultdict(list)
    doc_country: dict[str, str] = {}
    with align_path.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            j = anchor_idx[r["anchor_id"]]
            country_anchors[r["iso2"]].append(j)
            doc_anchors[r["doc_id"]].append(j)
            doc_country[r["doc_id"]] = r["iso2"]

    rng = np.random.default_rng(args.seed)
    n_anchors = len(anchor_ids)

    # A. Per-country focal-anchor share with CI
    print(f"[boot ] focal anchor = {args.focal_anchor}  n_boot = {args.n_boot}")
    print(f"{'iso':<4s} {'n':>5s} {'mean%':>7s} {'95%CI':>15s}")
    per_country_rows = []
    boot_share_by_country: dict[str, np.ndarray] = {}
    for iso, js in country_anchors.items():
        arr = np.array(js)
        n = len(arr)
        if n == 0:
            continue
        boot_shares = np.empty(args.n_boot)
        for b in range(args.n_boot):
            sample = rng.choice(arr, size=n, replace=True)
            boot_shares[b] = (sample == focal_j).mean() * 100
        point = (arr == focal_j).mean() * 100
        lo, hi = percentile_ci(boot_shares)
        per_country_rows.append({
            "iso": iso, "n": n,
            "focal_mean_pct": round(point, 2),
            "ci_lo": round(lo, 2),
            "ci_hi": round(hi, 2),
        })
        boot_share_by_country[iso] = boot_shares
        print(f"{iso:<4s} {n:>5d} {point:>7.2f} [{lo:>5.2f}, {hi:>5.2f}]")

    ROBUST_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = ROBUST_DIR / f"bootstrap_ci{suffix}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per_country_rows[0].keys()))
        w.writeheader()
        w.writerows(per_country_rows)
    print(f"\n[out] {out_csv}")

    # B. Effect sizes
    canonical_isos = [c for c in boot_share_by_country
                      if c not in EXCLUDE_FROM_CANONICAL
                      and len(country_anchors[c]) >= 50]
    print(f"\n[effects] canonical group n={len(canonical_isos)} "
          f"(excluded: KR, IE, AE, AU)")

    # Stack canonical bootstrap distributions and take mean per iteration
    canonical_stack = np.stack([boot_share_by_country[c] for c in canonical_isos])
    canonical_mean_boot = canonical_stack.mean(axis=0)
    canonical_point = float(canonical_mean_boot.mean())
    can_lo, can_hi = percentile_ci(canonical_mean_boot)

    effect_rows: list[dict] = [{
        "contrast": "canonical_mean",
        "point_pct": round(canonical_point, 2),
        "ci_lo": round(can_lo, 2),
        "ci_hi": round(can_hi, 2),
        "note": f"mean across {len(canonical_isos)} canonical countries",
    }]

    for iso in DEVIATING_ISO:
        if iso not in boot_share_by_country:
            continue
        diff = boot_share_by_country[iso] - canonical_mean_boot
        point = float(diff.mean())
        lo, hi = percentile_ci(diff)
        effect_rows.append({
            "contrast": f"{iso} − canonical_mean",
            "point_pct": round(point, 2),
            "ci_lo": round(lo, 2),
            "ci_hi": round(hi, 2),
            "note": "effect size for the Cluster-1 deviation",
        })

    # IE-01 vs IE-02 asymmetry
    for d_a, d_b in [("IE-01", "IE-02")]:
        if d_a not in doc_anchors or d_b not in doc_anchors:
            continue
        arr_a = np.array(doc_anchors[d_a])
        arr_b = np.array(doc_anchors[d_b])
        if len(arr_a) == 0 or len(arr_b) == 0:
            continue
        boot_a = np.empty(args.n_boot)
        boot_b = np.empty(args.n_boot)
        for bi in range(args.n_boot):
            sa = rng.choice(arr_a, size=len(arr_a), replace=True)
            sb = rng.choice(arr_b, size=len(arr_b), replace=True)
            boot_a[bi] = (sa == focal_j).mean() * 100
            boot_b[bi] = (sb == focal_j).mean() * 100
        diff = boot_a - boot_b
        point = float((arr_a == focal_j).mean() * 100 - (arr_b == focal_j).mean() * 100)
        lo, hi = percentile_ci(diff)
        effect_rows.append({
            "contrast": f"{d_a} − {d_b} (intra-IE asymmetry)",
            "point_pct": round(point, 2),
            "ci_lo": round(lo, 2),
            "ci_hi": round(hi, 2),
            "note": f"n_{d_a}={len(arr_a)}, n_{d_b}={len(arr_b)}",
        })

    print(f"\n{'contrast':<40s} {'point':>7s} {'95%CI':>15s}  note")
    for r in effect_rows:
        print(f"{r['contrast']:<40s} {r['point_pct']:>7.2f} "
              f"[{r['ci_lo']:>5.2f}, {r['ci_hi']:>5.2f}]  {r['note']}")

    out_eff = ROBUST_DIR / f"bootstrap_effects{suffix}.csv"
    with out_eff.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(effect_rows[0].keys()))
        w.writeheader()
        w.writerows(effect_rows)
    print(f"\n[out] {out_eff}")

    # Report
    md = [f"# Bootstrap 95 % CI — focal anchor {args.focal_anchor}, n_boot = {args.n_boot}",
          "",
          f"Source: `{align_path.name}`. Resampling unit = aligned sentence; iteration count = {args.n_boot}; seed = {args.seed}.",
          "",
          "## Per-country focal-anchor share",
          "",
          "| iso | n | mean % | 95 % CI |",
          "|---|---:|---:|---|"]
    for r in per_country_rows:
        md.append(f"| {r['iso']} | {r['n']} | {r['focal_mean_pct']} | "
                  f"[{r['ci_lo']}, {r['ci_hi']}] |")
    md += ["",
           "## Effect sizes",
           "",
           "| contrast | point % | 95 % CI | note |",
           "|---|---:|---|---|"]
    for r in effect_rows:
        md.append(f"| {r['contrast']} | {r['point_pct']} | "
                  f"[{r['ci_lo']}, {r['ci_hi']}] | {r['note']} |")
    md += ["",
           "## Interpretation",
           "",
           "- If the *contrast* row \"KR − canonical_mean\" has a 95 % CI that does NOT include zero, KR's Tool-use deviation is statistically distinguishable from the canonical signature at this resolution.",
           "- Similarly for IE.",
           "- The \"IE-01 − IE-02\" row quantifies the intra-IE asymmetry: if the CI excludes zero, the §4.5 LOO finding (IE-01 carries the tool-use signal) is supported by bootstrap inference, not just by point estimates."]
    (ROBUST_DIR / f"bootstrap_report{suffix}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
