#!/usr/bin/env python3
"""forest_plot_robustness.py — §4.6 robustness summary figure.

Assembles a single PNG figure showing per-module robustness evidence for
the K = 2 cluster claim. One panel per stress test, KR and IE shown side
by side; the canonical band is shaded grey.

Panels (left → right):
  1. Bootstrap CI on S08 (Application skills) share
  2. Inverse-corpus-weighted T/E ratio
  3. Leave-one-out cluster assignment (binary indicator)
  4. Uniform-cap N=500 Cluster-1 assignment rate (%)
  5. Pre/post cohort cluster assignment

Output: data/clustering/figure_robustness_summary_v2.png

Usage
-----
python scripts/03_analysis/forest_plot_robustness.py --tag v2
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROBUST_DIR = REPO / "data" / "robustness"
ALIGN_DIR = REPO / "data" / "adherence_matrix"
OUT_DIR = REPO / "data" / "clustering"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v2", choices=["v1", "v2"])
    args = parser.parse_args()
    suffix = f"_{args.tag}"

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        sys.stderr.write("[error] matplotlib not installed.\n")
        return 1

    # Read each robustness file (if it exists)
    def read_csv(path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    boot_ci_rows = read_csv(ROBUST_DIR / f"bootstrap_ci{suffix}.csv")
    inv_rows = read_csv(ROBUST_DIR / f"inverse_weighted_summary{suffix}.csv")
    loo_rows = read_csv(ROBUST_DIR / f"loo_summary{suffix}.csv")
    cap_rows = read_csv(ROBUST_DIR / f"uniform_cap{suffix}.csv")
    coh_rows = read_csv(ROBUST_DIR / f"cohort_summary{suffix}.csv")

    if not boot_ci_rows:
        sys.stderr.write(f"[error] missing bootstrap data for {args.tag}\n")
        return 1

    # Per-country lookups
    by_iso_boot = {r["iso"]: r for r in boot_ci_rows}
    by_iso_inv = {r["iso"]: r for r in inv_rows}
    by_iso_loo = {r["iso"]: r for r in loo_rows}
    by_iso_cap = {r["iso"]: r for r in cap_rows}
    by_iso_coh = {r["iso"]: r for r in coh_rows}

    # Canonical countries (≥ 50, excluding KR/IE/AE/AU)
    canonical = [iso for iso, r in by_iso_boot.items()
                 if int(r["n"]) >= 50 and iso not in {"KR", "IE", "AE", "AU"}]
    can_means = [float(by_iso_boot[c]["focal_mean_pct"]) for c in canonical]
    can_mean = sum(can_means) / len(can_means) if can_means else 0
    can_lo = min(float(by_iso_boot[c]["ci_lo"]) for c in canonical) if canonical else 0
    can_hi = max(float(by_iso_boot[c]["ci_hi"]) for c in canonical) if canonical else 0

    # Build the figure: 1 row × 5 panels
    fig, axes = plt.subplots(1, 5, figsize=(18, 5))
    fig.suptitle(f"Robustness of the K=2 cluster {{KR, IE}} — {args.tag} anchors",
                 fontsize=14, fontweight="bold")

    target_countries = ["KR", "IE"]
    colors = {"KR": "#d62728", "IE": "#1f77b4", "canonical": "#bbbbbb"}

    # Panel 1: Bootstrap CI on S08
    ax = axes[0]
    ys = [0, 1]
    for y, iso in zip(ys, target_countries):
        r = by_iso_boot.get(iso)
        if not r:
            continue
        mean = float(r["focal_mean_pct"])
        lo, hi = float(r["ci_lo"]), float(r["ci_hi"])
        ax.errorbar(mean, y, xerr=[[mean - lo], [hi - mean]], fmt="o",
                    color=colors[iso], capsize=4, markersize=10)
    ax.axvspan(can_lo, can_hi, color=colors["canonical"], alpha=0.4, label=f"canonical (n={len(canonical)})")
    ax.axvline(can_mean, color=colors["canonical"], linestyle="--", linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(target_countries)
    ax.set_xlabel("AILIT-S08 share (%)")
    ax.set_title("Module 3: Bootstrap CI (n=1,000)")
    ax.set_xlim(0, max(35, can_hi + 5))
    ax.invert_yaxis()
    ax.legend(loc="lower right", fontsize=8)
    ax.grid(axis="x", alpha=0.3)

    # Panel 2: Inverse-weighted T/E
    ax = axes[1]
    for y, iso in zip(ys, target_countries):
        r = by_iso_inv.get(iso)
        if not r:
            continue
        raw_te = float(r["raw_T/E"])
        w_te = float(r["weighted_T/E"])
        ax.plot([raw_te, w_te], [y, y], "o-", color=colors[iso], markersize=8)
        ax.annotate("raw", (raw_te, y), textcoords="offset points",
                    xytext=(-5, -12), fontsize=7)
        ax.annotate("wgt", (w_te, y), textcoords="offset points",
                    xytext=(5, -12), fontsize=7)
    canonical_wtes = [float(by_iso_inv[c]["weighted_T/E"]) for c in canonical if c in by_iso_inv]
    if canonical_wtes:
        ax.axvspan(min(canonical_wtes), max(canonical_wtes),
                   color=colors["canonical"], alpha=0.4)
        ax.axvline(sum(canonical_wtes) / len(canonical_wtes),
                   color=colors["canonical"], linestyle="--", linewidth=1)
    ax.axvline(1.0, color="black", linestyle=":", alpha=0.5, linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(target_countries)
    ax.set_xlabel("T/E ratio (raw → weighted)")
    ax.set_title("Module 1: Inverse weighting")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    # Panel 3: LOO binary indicator (cluster after LOO)
    ax = axes[2]
    for y, iso in zip(ys, target_countries):
        r = by_iso_loo.get(iso)
        if not r:
            continue
        cluster = int(r["loo_cluster"])
        marker = "✓" if cluster == 1 else "✗"
        color = colors[iso] if cluster == 1 else "#888888"
        ax.text(0.5, y, marker, fontsize=44, color=color,
                ha="center", va="center", fontweight="bold")
        ax.text(0.5, y + 0.30, f"drop {r['drop_doc']}",
                fontsize=8, color="#444", ha="center", va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(1.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks(ys)
    ax.set_yticklabels(target_countries)
    ax.set_title("Module 2: LOO (still Cluster 1?)")

    # Panel 4: Uniform-cap N=500
    ax = axes[3]
    for y, iso in zip(ys, target_countries):
        r = by_iso_cap.get(iso)
        if not r:
            continue
        rate = float(r["cluster1_rate_pct"])
        ax.barh([y], [rate], color=colors[iso], height=0.5)
        ax.text(rate + 1, y, f"{rate:.0f}%", va="center", fontsize=10)
    ax.set_yticks(ys)
    ax.set_yticklabels(target_countries)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Cluster-1 rate over 1,000 resamples (%)")
    ax.set_title("Module 4: Uniform-cap N=500")
    ax.invert_yaxis()
    ax.grid(axis="x", alpha=0.3)

    # Panel 5: Pre/post cohort
    ax = axes[4]
    for y, iso in zip(ys, target_countries):
        r = by_iso_coh.get(iso)
        if not r:
            continue
        pre_cl = r.get("pre_cluster", "-")
        post_cl = r.get("post_cluster", "-")

        def to_xy(cl_str: str, x: float) -> tuple[float, float, str, str]:
            if cl_str in {"1", "2"}:
                cluster = int(cl_str)
                marker = "✓" if cluster == 1 else "✗"
                color = colors[iso] if cluster == 1 else "#888888"
                return x, y, marker, color
            return x, y, "—", "#aaa"

        for x, lab in [(0.3, "pre"), (0.7, "post")]:
            cl_str = pre_cl if lab == "pre" else post_cl
            xx, yy, marker, color = to_xy(cl_str, x)
            ax.text(xx, yy, marker, fontsize=30, color=color,
                    ha="center", va="center", fontweight="bold")
            ax.text(xx, yy + 0.30, lab, fontsize=8, color="#444",
                    ha="center", va="center")
    ax.set_xlim(0, 1)
    ax.set_ylim(1.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks(ys)
    ax.set_yticklabels(target_countries)
    ax.set_title("Module 5: Temporal cohort")

    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"figure_robustness_summary{suffix}.png"
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    print(f"[out] {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
