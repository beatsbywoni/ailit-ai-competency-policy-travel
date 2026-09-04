#!/usr/bin/env python3
"""figure_cross_framework.py — Figure 1 (cross-framework replication) for the manuscript.

Single PNG (4-panel composite) showing that the K = 2 partition {KR, IE}
vs canonical replicates across three independent anchor frameworks:

  ┌─────────────┬─────────────┬─────────────┐
  │ student-12  │ teacher-5   │ OECD-4      │   ← 3 Ward dendrograms
  │ s=0.379     │ s=0.473     │ s=0.483     │     with K=2 cut highlighted
  └─────────────┴─────────────┴─────────────┘
  ┌───────────────────────────────────────────┐
  │ Cross-framework cluster identity table    │   ← heatmap rows = countries,
  │ KR ★ ★ ★   IE ★ ★ ★   US — ★ ★ ...        │     cols = frameworks,
  │                                            │     ★ = Cluster 1 assignment
  └───────────────────────────────────────────┘

Usage
-----
python scripts/03_analysis/figure_cross_framework.py
python scripts/03_analysis/figure_cross_framework.py --student-tag v2
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ALIGN_DIR = REPO / "data" / "adherence_matrix"
CLUSTER_DIR = REPO / "data" / "clustering"
OUT_DIR = CLUSTER_DIR

DEVIATING_ISO = {"KR", "IE"}
MIN_N = 50


def hellinger(p: np.ndarray, q: np.ndarray) -> float:
    p = p / max(p.sum(), 1e-12)
    q = q / max(q.sum(), 1e-12)
    return float(np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum()))


def hellinger_distance_matrix(P: np.ndarray) -> np.ndarray:
    sqrtP = np.sqrt(P)
    diff = sqrtP[:, None, :] - sqrtP[None, :, :]
    sq = (diff ** 2).sum(axis=2)
    H = np.sqrt(0.5 * sq)
    np.fill_diagonal(H, 0.0)
    return (H + H.T) / 2.0


def load_matrix(path: Path) -> tuple[list[str], np.ndarray, list[int]]:
    isos, totals, rows = [], [], []
    with path.open(newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        n_anchors = len(header) - 2
        for r in rdr:
            isos.append(r[0])
            rows.append([float(x) for x in r[1:1 + n_anchors]])
            totals.append(int(r[-1]))
    return isos, np.array(rows, dtype=float), totals


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--student-tag", default="v2",
                        help="student anchor matrix suffix (v2 default; v1 for sensitivity)")
    parser.add_argument("--out", default=None, help="optional output PNG path")
    args = parser.parse_args()

    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        from matplotlib.gridspec import GridSpec
        from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
        from scipy.spatial.distance import squareform
        from sklearn.metrics import silhouette_score
    except ImportError as e:
        sys.stderr.write(f"[error] missing dependency: {e}\n")
        return 1

    frameworks = [
        ("student", "UNESCO student (12 anchors)",
         ALIGN_DIR / f"sprint1_25x12_pct_{args.student_tag}.csv"),
        ("teacher", "UNESCO teacher (5 anchors)",
         ALIGN_DIR / "sprint1_25x5_pct_teacher.csv"),
        ("oecd", "OECD–EC draft, May 2025 (4 anchors)",
         ALIGN_DIR / "sprint1_25x4_pct_oecd.csv"),
    ]

    cluster_assign: dict[str, dict[str, int]] = {}
    silhouettes: dict[str, float] = {}
    dendrogram_data: dict[str, dict] = {}

    for name, _label, path in frameworks:
        if not path.exists():
            sys.stderr.write(f"[error] {path} missing — run Phase 3 step 1+2 first.\n")
            return 1
        isos, P, totals = load_matrix(path)
        # Hellinger filter
        keep = [i for i, n in enumerate(totals) if n >= MIN_N]
        elig_isos = [isos[i] for i in keep]
        P_keep = P[keep]
        # Normalise rows to probability simplex
        row_sums = P_keep.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        P_keep = P_keep / row_sums

        H = hellinger_distance_matrix(P_keep)
        H_cond = squareform(H, checks=False)
        Z = linkage(H_cond, method="ward")
        labels = fcluster(Z, t=2, criterion="maxclust")
        # Normalise: cluster containing KR/IE → 1
        dev_idx = [i for i, c in enumerate(elig_isos) if c in DEVIATING_ISO]
        if dev_idx:
            dev_lbl = labels[dev_idx[0]]
            labels = np.where(labels == dev_lbl, 1, 2)
        sil = silhouette_score(H, labels, metric="precomputed")
        silhouettes[name] = float(sil)
        cluster_assign[name] = {iso: int(l) for iso, l in zip(elig_isos, labels)}

        # Add countries below threshold as 0 (n/a)
        for iso in isos:
            if iso not in cluster_assign[name]:
                cluster_assign[name][iso] = 0

        dendrogram_data[name] = {
            "isos": elig_isos,
            "Z": Z,
            "labels": labels,
            "max_dist": float(Z[:, 2].max()),
        }

    # Determine country ordering for the heatmap: rep_score descending, then alphabetical
    iso_universe = sorted({iso for d in cluster_assign.values() for iso in d})
    rep_score: dict[str, int] = {}
    for iso in iso_universe:
        rep_score[iso] = sum(1 for n in cluster_assign if cluster_assign[n].get(iso) == 1)
    iso_universe.sort(key=lambda c: (-rep_score[c], c))

    # ============ DRAW ============
    fig = plt.figure(figsize=(15, 11))
    gs = GridSpec(2, 3, height_ratios=[1.0, 1.3], hspace=0.40, wspace=0.30,
                  left=0.06, right=0.98, top=0.93, bottom=0.05)

    colour_dev = "#d62728"  # red — cluster 1
    colour_can = "#777777"  # grey — cluster 2
    colour_low = "#dddddd"  # light grey — n/a small corpus

    # ---- Row 1: 3 dendrograms ----
    for col, (name, label_full, _path) in enumerate(frameworks):
        ax = fig.add_subplot(gs[0, col])
        data = dendrogram_data[name]
        labels = data["labels"]
        # Color leaves by cluster identity
        leaf_colors = []
        for iso in data["isos"]:
            cl = cluster_assign[name][iso]
            if iso in DEVIATING_ISO:
                leaf_colors.append("#a30000")  # darker red for KR/IE themselves
            else:
                leaf_colors.append(colour_dev if cl == 1 else colour_can)

        # Determine threshold for K=2 cut (top split)
        cut_at = data["Z"][-1, 2] * 0.99  # just below the top merge

        d = dendrogram(data["Z"], labels=data["isos"], ax=ax,
                       leaf_font_size=9, leaf_rotation=0,
                       color_threshold=cut_at,
                       above_threshold_color="#888888")
        # Recolor leaf labels by cluster identity
        xlbls = ax.get_xmajorticklabels()
        for lbl in xlbls:
            iso = lbl.get_text()
            cl = cluster_assign[name].get(iso, 0)
            if iso in DEVIATING_ISO:
                lbl.set_color("#a30000")
                lbl.set_fontweight("bold")
            elif cl == 1:
                lbl.set_color(colour_dev)
                lbl.set_fontweight("bold")
            else:
                lbl.set_color(colour_can)

        # Title with silhouette
        n_eligible = len(data["isos"])
        ax.set_title(f"{label_full}\nK=2 silhouette = {silhouettes[name]:.3f}  "
                     f"(n = {n_eligible} countries)",
                     fontsize=11)
        ax.set_ylabel("Hellinger distance" if col == 0 else "")
        ax.tick_params(axis="x", which="major", labelsize=8)
        # Lightly shade the K=2 cut height
        ax.axhline(cut_at, color="#aaa", linestyle=":", linewidth=0.7, alpha=0.6)

    # ---- Row 2: cross-framework heatmap ----
    ax_hm = fig.add_subplot(gs[1, :])
    n_iso = len(iso_universe)
    n_fw = len(frameworks)

    # Build matrix: 1 = Cluster 1 (deviating), 2 = Cluster 2 (canonical), 0 = n/a
    M = np.zeros((n_iso, n_fw))
    for i, iso in enumerate(iso_universe):
        for j, (name, _, _) in enumerate(frameworks):
            M[i, j] = cluster_assign[name].get(iso, 0)

    # Draw cells as rectangles
    for i, iso in enumerate(iso_universe):
        for j, (name, label_full, _) in enumerate(frameworks):
            v = int(M[i, j])
            if v == 1:
                color = colour_dev
                text = "★"
                fontcolor = "white"
            elif v == 2:
                color = "white"
                text = "·"
                fontcolor = "#999"
            else:
                color = colour_low
                text = "—"
                fontcolor = "#777"
            ax_hm.add_patch(Rectangle((j, n_iso - 1 - i), 1, 1,
                                       facecolor=color, edgecolor="#666", linewidth=0.5))
            ax_hm.text(j + 0.5, n_iso - 1 - i + 0.5, text,
                       ha="center", va="center", fontsize=14,
                       color=fontcolor, fontweight="bold")
        # Country label (left)
        is_dev_anchor = iso in DEVIATING_ISO
        rep = rep_score.get(iso, 0)
        weight = "bold" if (is_dev_anchor or rep == 3) else "normal"
        col = "#a30000" if is_dev_anchor else ("#d62728" if rep >= 2 else "#222")
        ax_hm.text(-0.15, n_iso - 1 - i + 0.5,
                   f"{iso}",
                   ha="right", va="center", fontsize=10, color=col, fontweight=weight)
        # Rep score (right)
        ax_hm.text(n_fw + 0.15, n_iso - 1 - i + 0.5,
                   f"{rep}/3",
                   ha="left", va="center", fontsize=9,
                   color="#a30000" if rep == 3 else ("#d62728" if rep == 2 else "#555"),
                   fontweight="bold" if rep == 3 else "normal")

    # Column headers
    for j, (name, label_full, _) in enumerate(frameworks):
        short = {"student": "UNESCO\nstudent\n(12)",
                 "teacher": "UNESCO\nteacher\n(5)",
                 "oecd": "OECD–EC\ndraft 2025\n(4)"}[name]
        ax_hm.text(j + 0.5, n_iso + 0.5, short,
                   ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Rep-score header
    ax_hm.text(n_fw + 0.5, n_iso + 0.5, "Rep.\nscore",
               ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax_hm.set_xlim(-1.2, n_fw + 1.0)
    ax_hm.set_ylim(-1.6, n_iso + 1.5)
    ax_hm.axis("off")

    # Legend
    legend_y = -1.3
    legend_items = [
        ("#d62728", "Cluster 1 — deviating (≈ {KR, IE} centroid)"),
        ("white", "Cluster 2 — canonical"),
        (colour_low, "n/a — corpus size < 50"),
    ]
    for k, (c, txt) in enumerate(legend_items):
        x = 0.02 + k * 0.37
        ax_hm.add_patch(Rectangle((x * (n_fw + 1), legend_y), 0.4, 0.5,
                                   facecolor=c, edgecolor="#666", linewidth=0.5,
                                   transform=ax_hm.transData))
        ax_hm.text(x * (n_fw + 1) + 0.6, legend_y + 0.25, txt,
                   fontsize=9, va="center", transform=ax_hm.transData)

    # Big title for the figure
    fig.suptitle("Cross-framework replication of the K = 2 cluster {KR, IE} across the three pre-specified anchor sets",
                 fontsize=14, fontweight="bold", y=0.985)

    out_path = Path(args.out) if args.out else OUT_DIR / f"figure_cross_framework_{args.student_tag}.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"[out] {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
