#!/usr/bin/env python3
"""hellinger_cluster.py — 4-pattern hypothesis test via Hellinger clustering.

Treat each row of the 25 × 12 adherence-percentage matrix as a probability
distribution over the UNESCO student anchors and cluster countries by
Hellinger distance:

    H(p, q) = (1/sqrt(2)) * sqrt( sum_i ( sqrt(p_i) - sqrt(q_i) )^2 )

Pipeline
--------
1. Load `data/adherence_matrix/sprint1_25x12_pct_v2.csv`.
2. Normalise rows to probability simplex (already true if pct sum = 100).
3. Compute pairwise Hellinger distance matrix.
4. Hierarchical agglomerative clustering (average + ward linkage).
5. Silhouette scores at K = 2..6 to pick K.
6. Print dendrogram (text), cluster assignments, save CSV + Ward dendrogram
   PNG (if matplotlib available).

Manuscript §4.5 deliverable.

Usage
-----
python scripts/03_analysis/hellinger_cluster.py
python scripts/03_analysis/hellinger_cluster.py --tag v2
python scripts/03_analysis/hellinger_cluster.py --tag v1   # sensitivity
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

try:
    from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
    from scipy.spatial.distance import squareform
except ImportError:
    sys.stderr.write("[error] scipy not installed. pip install scipy\n")
    sys.exit(1)

try:
    from sklearn.metrics import silhouette_score
except ImportError:
    sys.stderr.write("[error] scikit-learn not installed. pip install scikit-learn\n")
    sys.exit(1)

REPO = Path(__file__).resolve().parents[2]
MATRIX_DIR = REPO / "data" / "adherence_matrix"
OUT_DIR = REPO / "data" / "clustering"


def hellinger_distance_matrix(P: np.ndarray) -> np.ndarray:
    """Pairwise Hellinger distance for rows of P (each row is a prob dist).

    P shape (n_rows, n_anchors). Returns (n_rows, n_rows) symmetric matrix.
    """
    sqrtP = np.sqrt(P)
    # H(i,j)^2 = (1/2) * sum_k (sqrtP[i,k] - sqrtP[j,k])^2
    diff = sqrtP[:, None, :] - sqrtP[None, :, :]
    sq = (diff ** 2).sum(axis=2)
    H = np.sqrt(0.5 * sq)
    # numerical: enforce zero diagonal, symmetry
    np.fill_diagonal(H, 0.0)
    H = (H + H.T) / 2.0
    return H


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tag", default="v2", choices=["v1", "v2", "teacher", "oecd"],
                        help="which anchor version (default v2)")
    parser.add_argument("--corpus", default="sprint1_25x12",
                        help="matrix prefix (default sprint1_25x12)")
    parser.add_argument("--min-aligned", type=int, default=50,
                        help="exclude countries with total_aligned < this "
                             "(default 50; protects AE=7, AU=42 from skewing "
                             "the silhouette)")
    parser.add_argument("--no-plot", action="store_true",
                        help="skip the matplotlib dendrogram PNG")
    args = parser.parse_args()

    matrix_path = MATRIX_DIR / f"{args.corpus}_pct_{args.tag}.csv"
    if not matrix_path.exists():
        sys.stderr.write(f"[error] {matrix_path} not found.\n")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load
    countries: list[str] = []
    anchor_cols: list[str] = []
    rows: list[list[float]] = []
    totals: list[int] = []
    with matrix_path.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        # header: key, S01..S12, total_aligned
        anchor_cols = header[1:-1]
        for r in reader:
            countries.append(r[0])
            rows.append([float(x) for x in r[1:-1]])
            totals.append(int(r[-1]))
    P = np.array(rows, dtype=float)

    # Filter by min-aligned
    keep = np.array([t >= args.min_aligned for t in totals])
    excluded = [c for c, t, k in zip(countries, totals, keep) if not k]
    if excluded:
        print(f"[filter] excluded (n < {args.min_aligned}): " +
              ", ".join(f"{c}(n={t})" for c, t in zip(countries, totals) if not keep[list(countries).index(c)]))
    countries = [c for c, k in zip(countries, keep) if k]
    P = P[keep]
    totals = [t for t, k in zip(totals, keep) if k]

    # Normalise to probability simplex (rows sum to 1)
    row_sums = P.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    P = P / row_sums

    print(f"[matrix ] {matrix_path.name} → {P.shape[0]} countries × {P.shape[1]} anchors")
    print(f"[anchors] {anchor_cols}")
    print()

    # Hellinger distance
    H = hellinger_distance_matrix(P)
    print(f"[hellinger] max={H.max():.3f}  mean={H[np.triu_indices_from(H, 1)].mean():.3f}  "
          f"min={H[H > 0].min():.3f}")

    # Save distance matrix
    dist_csv = OUT_DIR / f"hellinger_dist_{args.tag}.csv"
    with dist_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + countries)
        for i, c in enumerate(countries):
            w.writerow([c] + [f"{H[i, j]:.4f}" for j in range(len(countries))])
    print(f"[out    ] {dist_csv}")
    print()

    # Hierarchical clustering — Ward (typical for distance + 4-pattern)
    # scipy expects condensed (upper-triangular) form
    H_cond = squareform(H, checks=False)
    Z_ward = linkage(H_cond, method="ward")
    Z_avg = linkage(H_cond, method="average")

    # Silhouette across K = 2..6
    print(f"{'K':>3s}  {'silhouette (ward)':>18s}  {'silhouette (avg)':>17s}")
    sils = {}
    for K in range(2, 7):
        labels_w = fcluster(Z_ward, t=K, criterion="maxclust")
        labels_a = fcluster(Z_avg, t=K, criterion="maxclust")
        # silhouette over H (precomputed)
        try:
            s_w = silhouette_score(H, labels_w, metric="precomputed")
        except Exception:
            s_w = float("nan")
        try:
            s_a = silhouette_score(H, labels_a, metric="precomputed")
        except Exception:
            s_a = float("nan")
        sils[K] = (s_w, s_a)
        print(f"{K:>3d}  {s_w:>18.4f}  {s_a:>17.4f}")
    print()

    # Pick best K for Ward
    best_K_ward = max(sils, key=lambda k: sils[k][0])
    best_K_avg = max(sils, key=lambda k: sils[k][1])
    print(f"[best K] ward={best_K_ward} (s={sils[best_K_ward][0]:.4f}), "
          f"avg={best_K_avg} (s={sils[best_K_avg][1]:.4f})")
    print()

    # Report cluster assignments at K = 4 (the hypothesis) and at best K
    for label_K, Z, method in [(4, Z_ward, "ward"), (best_K_ward, Z_ward, "ward"),
                                (4, Z_avg, "average"), (best_K_avg, Z_avg, "average")]:
        if label_K < 2 or label_K > 6:
            continue
        labels = fcluster(Z, t=label_K, criterion="maxclust")
        clusters: dict[int, list[str]] = {}
        for c, l in zip(countries, labels):
            clusters.setdefault(int(l), []).append(c)
        print(f"--- {method}, K={label_K} ---")
        for k in sorted(clusters):
            members = clusters[k]
            # cluster centroid (mean prob over members)
            idx = [countries.index(m) for m in members]
            centroid = P[idx].mean(axis=0)
            dom_anchor = anchor_cols[int(centroid.argmax())]
            dom_share = centroid.max() * 100
            print(f"  cluster {k} (n={len(members)})  "
                  f"dominant {dom_anchor}={dom_share:.1f}%   "
                  f"{', '.join(members)}")
        # Save labels
        labels_csv = OUT_DIR / f"clusters_{args.tag}_{method}_K{label_K}.csv"
        with labels_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["country", "cluster", "n_aligned"])
            for c, l, t in zip(countries, labels, totals):
                w.writerow([c, int(l), t])
        print(f"  → {labels_csv}")
        print()

    # Dendrogram PNG (Ward)
    if not args.no_plot:
        try:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(12, 6))
            dendrogram(Z_ward, labels=countries, leaf_font_size=10, ax=ax,
                       color_threshold=0.5 * Z_ward[:, 2].max())
            ax.set_title(f"Ward-linkage dendrogram on Hellinger distances "
                         f"({args.tag} anchors, 25-country corpus, K_best={best_K_ward})")
            ax.set_xlabel("country")
            ax.set_ylabel("Hellinger distance")
            plt.tight_layout()
            png_path = OUT_DIR / f"dendrogram_{args.tag}_ward.png"
            plt.savefig(png_path, dpi=150)
            print(f"[plot   ] {png_path}")
        except ImportError:
            print("[plot   ] matplotlib not installed; skipped PNG")

    return 0


if __name__ == "__main__":
    sys.exit(main())
