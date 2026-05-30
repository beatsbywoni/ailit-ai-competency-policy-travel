#!/usr/bin/env python3
"""cross_framework_compare.py — Phase 3 §4.5 cross-framework cluster identity.

For each of the three anchor frameworks (UNESCO student 12, UNESCO teacher 5,
OECD AILit 4), determine which countries land in the same Hellinger K = 2
cluster as KR + IE (the "deviating" cluster from the §4.5 main analysis).

Output: a 25 × 3 table showing per-country cluster identity across
frameworks, plus an aggregate "replication score" per country.

Hypothesis: KR and IE are in the deviating cluster in all 3 frameworks
→ the Tool-use signature is a property of the national policy text, not
of any single anchor framework.

Outputs
-------
data/clustering/cross_framework_v2.csv      country × framework cluster id
data/clustering/cross_framework_v2.md       interpretation table

Usage
-----
python scripts/03_analysis/cross_framework_compare.py
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
ALIGN_DIR = REPO / "data" / "adherence_matrix"
OUT_DIR = REPO / "data" / "clustering"

DEVIATING_ISO = {"KR", "IE"}
MIN_N = 50  # match the Hellinger filter; excludes AE / AU


def hellinger(p: np.ndarray, q: np.ndarray) -> float:
    p = p / max(p.sum(), 1e-12)
    q = q / max(q.sum(), 1e-12)
    return float(np.sqrt(0.5 * ((np.sqrt(p) - np.sqrt(q)) ** 2).sum()))


def load_matrix(path: Path) -> tuple[list[str], np.ndarray, list[int]]:
    isos, totals = [], []
    rows = []
    with path.open(newline="", encoding="utf-8") as f:
        rdr = csv.reader(f)
        header = next(rdr)
        n_anchors = len(header) - 2  # key + anchors + total_aligned
        for r in rdr:
            isos.append(r[0])
            rows.append([float(x) for x in r[1:1 + n_anchors]])
            totals.append(int(r[-1]))
    return isos, np.array(rows), totals


def cluster_against_deviating(isos: list[str], P: np.ndarray, totals: list[int]) -> dict[str, int]:
    """Cluster id: 1 = closer to {KR,IE} centroid, 2 = closer to canonical centroid."""
    eligible_idx = [i for i, n in enumerate(totals) if n >= MIN_N]
    elig_isos = [isos[i] for i in eligible_idx]
    P_elig = P[eligible_idx]
    # normalise each row to probabilities
    sums = P_elig.sum(axis=1, keepdims=True)
    sums[sums == 0] = 1
    P_elig = P_elig / sums

    dev_idx = [eligible_idx.index(i) for i, c in enumerate(elig_isos) if c in DEVIATING_ISO]
    can_idx = [i for i in range(len(elig_isos)) if i not in dev_idx]
    if not dev_idx or not can_idx:
        return {c: 0 for c in isos}
    cent_dev = P_elig[dev_idx].mean(axis=0)
    cent_can = P_elig[can_idx].mean(axis=0)

    out: dict[str, int] = {}
    for i, iso in enumerate(isos):
        if totals[i] < MIN_N:
            out[iso] = 0  # "n/a — small corpus"
            continue
        row = P[i].astype(float)
        s = row.sum()
        if s == 0:
            out[iso] = 0
            continue
        row = row / s
        out[iso] = 1 if hellinger(row, cent_dev) < hellinger(row, cent_can) else 2
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--student-tag", default="v2",
                        help="suffix on student matrix (default v2; use v1 for sensitivity)")
    args = parser.parse_args()

    frameworks = [
        ("student", ALIGN_DIR / f"sprint1_25x12_pct_{args.student_tag}.csv"),
        ("teacher", ALIGN_DIR / "sprint1_25x5_pct_teacher.csv"),
        ("oecd",    ALIGN_DIR / "sprint1_25x4_pct_oecd.csv"),
    ]

    table: dict[str, dict[str, int]] = {}
    iso_universe: list[str] = []
    for name, path in frameworks:
        if not path.exists():
            sys.stderr.write(f"[error] {path} missing. Run Phase 3 step 1 first.\n")
            return 1
        isos, P, totals = load_matrix(path)
        clusters = cluster_against_deviating(isos, P, totals)
        table[name] = clusters
        if not iso_universe:
            iso_universe = isos

    # Per-country replication score (count of frameworks where in cluster 1)
    print(f"{'iso':<4s}  {'student':>7s}  {'teacher':>7s}  {'oecd':>5s}  {'rep_score':>10s}  note")
    rows = []
    for iso in iso_universe:
        s = table["student"].get(iso, 0)
        t = table["teacher"].get(iso, 0)
        o = table["oecd"].get(iso, 0)
        score = sum(1 for x in [s, t, o] if x == 1)
        if iso in DEVIATING_ISO:
            note = "anchor of cluster"
        elif score >= 2:
            note = "REPLICATES deviating signature"
        elif s == 0 and t == 0 and o == 0:
            note = "all small-n"
        else:
            note = ""
        rows.append({
            "iso": iso,
            "student_cluster": s,
            "teacher_cluster": t,
            "oecd_cluster": o,
            "rep_score": score,
            "note": note,
        })
        print(f"{iso:<4s}  {s:>7d}  {t:>7d}  {o:>5d}  {score:>10d}  {note}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = OUT_DIR / f"cross_framework_{args.student_tag}.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\n[out] {out_csv}")

    # Quick agreement statistics
    elig = [r for r in rows if r["student_cluster"] in {1, 2}]
    n = len(elig)
    pair_agree = {
        ("student", "teacher"): sum(1 for r in elig if r["teacher_cluster"] == r["student_cluster"]),
        ("student", "oecd"):    sum(1 for r in elig if r["oecd_cluster"]    == r["student_cluster"]),
        ("teacher", "oecd"):    sum(1 for r in elig if r["teacher_cluster"] == r["oecd_cluster"]),
    }
    print(f"\n[agreement on n={n} eligible countries]")
    for (a, b), k in pair_agree.items():
        print(f"  {a}↔{b}:  {k}/{n}  ({k/n*100:.0f}%)")

    kr_t = table["teacher"].get("KR", 0)
    kr_o = table["oecd"].get("KR", 0)
    ie_t = table["teacher"].get("IE", 0)
    ie_o = table["oecd"].get("IE", 0)
    print(f"\n[KR]  student=1 (anchor), teacher={kr_t}, oecd={kr_o}  → replication count {sum(1 for x in [kr_t, kr_o] if x == 1)}/2")
    print(f"[IE]  student=1 (anchor), teacher={ie_t}, oecd={ie_o}  → replication count {sum(1 for x in [ie_t, ie_o] if x == 1)}/2")

    # Markdown
    md = ["# Cross-framework cluster identity — Phase 3 §4.5",
          "",
          f"Source matrices: `sprint1_25x12_pct_{args.student_tag}.csv` (student 12), `sprint1_25x5_pct_teacher.csv` (teacher 5), `sprint1_25x4_pct_oecd.csv` (OECD 4). Each country is assigned to cluster 1 (closer to KR + IE centroid) or 2 (closer to canonical centroid) by Hellinger distance, with `--min-aligned 50` filter (0 = excluded).",
          "",
          "## Per-country cluster across frameworks",
          "",
          "| iso | student | teacher | oecd | rep_score | note |",
          "|---|:-:|:-:|:-:|:-:|---|"]
    for r in rows:
        md.append(f"| {r['iso']} | {r['student_cluster']} | {r['teacher_cluster']} | "
                  f"{r['oecd_cluster']} | {r['rep_score']} | {r['note']} |")
    md += ["",
           f"## Framework-pair agreement (n = {n} eligible countries)",
           "",
           "| pair | agreement |",
           "|---|---:|"]
    for (a, b), k in pair_agree.items():
        md.append(f"| {a} ↔ {b} | {k}/{n} ({k/n*100:.0f} %) |")
    md += ["",
           "## Interpretation",
           "",
           "- KR and IE were defined as Cluster 1 in the student analysis (§4.5.1). The question for §4.5.2-3 is whether they remain in Cluster 1 (the {KR, IE} centroid) when teacher / OECD frameworks are substituted.",
           "- A country with `rep_score = 3` is in the deviating cluster across all three frameworks. A country with `rep_score = 2` replicates in two of three. The deviating signature is *framework-replicable* for the country.",
           "- If agreement between framework pairs is high (≥ 70 %), the cluster partition is largely framework-invariant. Lower agreement indicates framework-specific structure — interesting in its own right, but weakens the §4.5 main claim."]
    (OUT_DIR / f"cross_framework_{args.student_tag}.md").write_text("\n".join(md), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
