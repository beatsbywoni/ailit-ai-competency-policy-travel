#!/usr/bin/env python3
"""verify_oecd_final.py — independent verification and extension of the
OECD–EC final-framework re-run (pre-submission fix round, 2026-09-04).

Reads ONLY the pipeline outputs already on disk (no embedding, no model):

  data/adherence_matrix/sprint1_25x4_{counts,pct}_oecd.csv          (draft, May 2025)
  data/adherence_matrix/sprint1_25x4_{counts,pct}_oecd_final.csv    (final, June 2026)
  data/adherence_matrix/sprint1_25x12_pct_v2.csv                    (UNESCO student)
  data/adherence_matrix/sprint1_25x5_pct_teacher.csv                (UNESCO teacher)
  data/clustering/hellinger_dist_oecd_final.csv                      (as written by run_oecd_final.py)
  data/clustering/clusters_oecd_ward_K2.csv                          (draft K=2 partition)

and (re)computes, from first principles:

  A2  Table 3 per-domain mean / SD / range (draft vs final, eligible countries),
      alignment totals, Ward+average silhouettes K=2..6 from the Hellinger
      matrix, K=2 Ward membership, and a byte-level check that the Hellinger
      matrix on disk equals the one recomputed from the pct file.
  A3  (1) Estonia-excluded re-clustering under the final anchors, K=2..6,
          Ward and average — does any K put KR and IE in the same non-majority
          group?
      (2) eligibility floor n >= 100 — same question.
      (3) mean pairwise Hellinger distance among eligible countries under
          draft, final, UNESCO student and UNESCO teacher anchors; Hellinger
          distance of KR and IE to the canonical centroid (mean profile of
          the countries in neither KR's nor IE's draft cluster) under draft
          and final.

Writes  data/clustering/oecd_final_verification.json
        data/clustering/oecd_final_verification.md
and prints a human-readable report.  Deterministic; safe to re-run.

Usage:  python scripts/06_oecd_final/verify_oecd_final.py [--min-aligned 50]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from sklearn.metrics import silhouette_score

REPO = Path(__file__).resolve().parents[2]
MAT = REPO / "data" / "adherence_matrix"
CLU = REPO / "data" / "clustering"


# ----------------------------------------------------------------- helpers
def read_matrix(path: Path):
    """Return (countries, header_anchor_ids, values[n,k], totals[n])."""
    with path.open(newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        hdr = next(rd)
        countries, rows, totals = [], [], []
        for r in rd:
            countries.append(r[0])
            rows.append([float(x) for x in r[1:-1]])
            totals.append(int(float(r[-1])))
    return countries, hdr[1:-1], np.array(rows), np.array(totals)


def hellinger(P: np.ndarray) -> np.ndarray:
    s = np.sqrt(P)
    d = s[:, None, :] - s[None, :, :]
    H = np.sqrt(0.5 * (d ** 2).sum(axis=2))
    np.fill_diagonal(H, 0.0)
    return (H + H.T) / 2.0


def read_dist(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        hdr = next(rd)[1:]
        rows = [[float(x) for x in r[1:]] for r in rd]
    return hdr, np.array(rows)


def cluster_table(H: np.ndarray, names: list[str], Ks=range(2, 7)):
    """Silhouettes and memberships for Ward and average linkage."""
    out = {}
    cond = squareform(H, checks=False)
    for method in ("ward", "average"):
        Z = linkage(cond, method=method)
        for K in Ks:
            lab = fcluster(Z, K, criterion="maxclust")
            sil = float(silhouette_score(H, lab, metric="precomputed")) if len(set(lab)) > 1 else float("nan")
            groups = {}
            for n, l in zip(names, lab):
                groups.setdefault(int(l), []).append(n)
            out[(method, K)] = {"silhouette": round(sil, 4),
                                "groups": [sorted(g) for g in groups.values()]}
    return out


def kr_ie_same_minority_group(groups: list[list[str]]) -> bool:
    """True if KR and IE sit together in a group that is NOT the largest group."""
    largest = max(len(g) for g in groups)
    for g in groups:
        if "KR" in g and "IE" in g and len(g) < largest:
            return True
    return False


def profile_stats(P: np.ndarray, names: list[str], anchors: list[str], pct=True):
    """Per-domain mean/SD/range over rows (countries)."""
    X = P if pct else 100 * P / P.sum(axis=1, keepdims=True)
    return {a: {"mean": round(float(X[:, j].mean()), 1),
                "sd": round(float(X[:, j].std(ddof=1)), 1),
                "min": round(float(X[:, j].min()), 1),
                "max": round(float(X[:, j].max()), 1),
                "argmin": names[int(X[:, j].argmin())],
                "argmax": names[int(X[:, j].argmax())]}
            for j, a in enumerate(anchors)}


def mean_pairwise(H: np.ndarray) -> float:
    iu = np.triu_indices_from(H, k=1)
    return float(H[iu].mean())


# ----------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-aligned", type=int, default=50)
    args = ap.parse_args()
    N = args.min_aligned
    rep: dict = {"min_aligned": N}
    lines: list[str] = []
    say = lambda s="": (print(s), lines.append(s))

    # ---------- load draft & final OECD matrices
    cD, aD, PD_pct, tD = read_matrix(MAT / "sprint1_25x4_pct_oecd.csv")
    cF, aF, PF_pct, tF = read_matrix(MAT / "sprint1_25x4_pct_oecd_final.csv")
    _, _, CD, tD2 = read_matrix(MAT / "sprint1_25x4_counts_oecd.csv")
    _, _, CF, tF2 = read_matrix(MAT / "sprint1_25x4_counts_oecd_final.csv")
    assert cD == cF, "country order differs between draft and final matrices"
    assert (tD == tD2).all() and (tF == tF2).all()

    say("# OECD–EC final-framework re-run — verification report")
    say(f"eligibility floor: n_aligned >= {N}")
    say()

    # ---------- A2.2 alignment totals
    say("## A2 — alignment totals (all 25 countries)")
    say(f"draft : {int(CD.sum()):,} aligned sentences")
    say(f"final : {int(CF.sum()):,} aligned sentences")
    rep["aligned_total"] = {"draft": int(CD.sum()), "final": int(CF.sum())}
    say()

    # ---------- eligibility
    keepD = tD >= N
    keepF = tF >= N
    keep = keepD & keepF
    elig = [c for c, k in zip(cD, keep) if k]
    say(f"eligible under both (n >= {N}): {len(elig)} countries — excluded: "
        + ", ".join(f"{c}(draft n={int(a)}, final n={int(b)})" for c, a, b, k in zip(cD, tD, tF, keep) if not k))
    rep["eligible"] = elig
    say()

    PD = PD_pct[keep]
    PF = PF_pct[keep]

    # ---------- A2.2 Table 3
    say("## A2 — Table 3 (per-domain adherence share, %, across eligible countries)")
    sD = profile_stats(PD, elig, aD)
    sF = profile_stats(PF, elig, aF)
    say("| domain | draft mean | draft SD | draft range | final mean | final SD | final range |")
    say("|---|---|---|---|---|---|---|")
    for j in range(4):
        d, f = sD[aD[j]], sF[aF[j]]
        say(f"| {aD[j]} → {aF[j]} | {d['mean']} | {d['sd']} | {d['min']}–{d['max']} ({d['argmin']}–{d['argmax']}) "
            f"| {f['mean']} | {f['sd']} | {f['min']}–{f['max']} ({f['argmin']}–{f['argmax']}) |")
    sumSD_D = round(sum(v["sd"] for v in sD.values()), 1)
    sumSD_F = round(sum(v["sd"] for v in sF.values()), 1)
    say(f"| sum of SDs (old row, for reference) | | {sumSD_D} | | | {sumSD_F} | |")
    rep["table3"] = {"draft": sD, "final": sF, "sum_sd": {"draft": sumSD_D, "final": sumSD_F}}
    say()
    say("Named values:")
    for c in ("KR", "US", "IE", "FR", "EE"):
        if c in elig:
            i = elig.index(c)
            say(f"  {c}: O4 draft {PD[i, 3]:.1f}% → final {PF[i, 3]:.1f}%   | O3 {PD[i, 2]:.1f} → {PF[i, 2]:.1f} | O2 {PD[i, 1]:.1f} → {PF[i, 1]:.1f} | O1 {PD[i, 0]:.1f} → {PF[i, 0]:.1f}")
            rep.setdefault("named", {})[c] = {"O4_draft": round(float(PD[i, 3]), 1), "O4_final": round(float(PF[i, 3]), 1)}
    # countries with final O4 >= 9
    hi = sorted(((float(PF[i, 3]), c) for i, c in enumerate(elig)), reverse=True)[:4]
    say("  top final Shape-AI shares: " + ", ".join(f"{c} {v:.1f}%" for v, c in hi))
    rep["top_final_O4"] = [(c, round(v, 1)) for v, c in hi]
    say()

    # ---------- A2.3 Hellinger + silhouettes (final)
    say("## A2 — Hellinger matrix and silhouettes (final anchors)")
    PFn = PF / PF.sum(axis=1, keepdims=True)
    HF = hellinger(PFn)
    hdr_disk, H_disk = read_dist(CLU / "hellinger_dist_oecd_final.csv")
    same_order = hdr_disk == elig
    maxdiff = float(np.abs(H_disk - HF).max()) if same_order else float("nan")
    say(f"on-disk Hellinger matrix: same country order = {same_order}; max |diff| vs recomputed = {maxdiff:.2e}")
    rep["hellinger_disk_check"] = {"same_order": same_order, "max_abs_diff": maxdiff}
    tabF = cluster_table(HF, elig)
    say("| linkage | K | silhouette | groups |")
    say("|---|---|---|---|")
    for (m, K), v in tabF.items():
        say(f"| {m} | {K} | {v['silhouette']:.4f} | {' / '.join(','.join(g) for g in v['groups'])} |")
    rep["silhouette_final"] = {f"{m}_K{K}": v for (m, K), v in tabF.items()}
    say()

    # draft, for reference
    PDn = PD / PD.sum(axis=1, keepdims=True)
    HD = hellinger(PDn)
    tabD = cluster_table(HD, elig)
    say("Draft anchors, same eligible set (reference):")
    for (m, K), v in tabD.items():
        if K == 2:
            say(f"  {m} K=2 silhouette {v['silhouette']:.4f}  groups {' / '.join(','.join(g) for g in v['groups'])}")
    rep["silhouette_draft_K2"] = {m: tabD[(m, 2)] for m in ("ward", "average")}
    say()

    # ---------- A3.1 Estonia excluded
    say("## A3.1 — Estonia excluded (final anchors)")
    idx = [i for i, c in enumerate(elig) if c != "EE"]
    names = [elig[i] for i in idx]
    H_noEE = hellinger(PFn[idx])
    tab = cluster_table(H_noEE, names)
    any_kr_ie = False
    say("| linkage | K | silhouette | KR&IE together in a minority group? | groups |")
    say("|---|---|---|---|---|")
    for (m, K), v in tab.items():
        flag = kr_ie_same_minority_group(v["groups"])
        any_kr_ie |= flag
        say(f"| {m} | {K} | {v['silhouette']:.4f} | {'YES' if flag else 'no'} | {' / '.join(','.join(g) for g in v['groups'])} |")
    say(f"→ any K/linkage recovering a KR+IE minority group: {any_kr_ie}")
    rep["A3_1_EE_excluded"] = {"n": len(names), "any_KR_IE_minority_group": any_kr_ie,
                               "table": {f"{m}_K{K}": v for (m, K), v in tab.items()}}
    say()

    # ---------- A3.2 floor n >= 100
    say("## A3.2 — eligibility floor n >= 100 (final anchors)")
    keep100 = (tD >= 100) & (tF >= 100)
    elig100 = [c for c, k in zip(cD, keep100) if k]
    P100 = PF_pct[keep100]
    P100 = P100 / P100.sum(axis=1, keepdims=True)
    H100 = hellinger(P100)
    tab = cluster_table(H100, elig100)
    any_kr_ie = False
    say(f"eligible: {len(elig100)} — dropped vs n>=50: {sorted(set(elig) - set(elig100))}")
    say("| linkage | K | silhouette | KR&IE together in a minority group? | groups |")
    say("|---|---|---|---|---|")
    for (m, K), v in tab.items():
        flag = kr_ie_same_minority_group(v["groups"])
        any_kr_ie |= flag
        say(f"| {m} | {K} | {v['silhouette']:.4f} | {'YES' if flag else 'no'} | {' / '.join(','.join(g) for g in v['groups'])} |")
    say(f"→ any K/linkage recovering a KR+IE minority group: {any_kr_ie}")
    rep["A3_2_floor100"] = {"eligible": elig100, "any_KR_IE_minority_group": any_kr_ie,
                            "table": {f"{m}_K{K}": v for (m, K), v in tab.items()}}
    say()

    # ---------- A3.3 distance-level statistics
    say("## A3.3 — mean pairwise Hellinger distance (eligible countries)")
    res = {}
    res["oecd_draft"] = (mean_pairwise(HD), len(elig))
    res["oecd_final"] = (mean_pairwise(HF), len(elig))
    # UNESCO student / teacher on their own eligible sets (n>=50) and on the OECD-eligible set
    for tag, fn in (("unesco_student", "sprint1_25x12_pct_v2.csv"), ("unesco_teacher", "sprint1_25x5_pct_teacher.csv")):
        cU, aU, PU, tU = read_matrix(MAT / fn)
        kU = tU >= N
        PUn = PU[kU] / PU[kU].sum(axis=1, keepdims=True)
        res[tag] = (mean_pairwise(hellinger(PUn)), int(kU.sum()))
        # restricted to the 23 OECD-eligible countries for like-for-like
        sel = [i for i, c in enumerate(cU) if c in elig]
        PUs = PU[sel] / PU[sel].sum(axis=1, keepdims=True)
        res[tag + "_on_oecd_eligible"] = (mean_pairwise(hellinger(PUs)), len(sel))
    say("| anchor set | n countries | mean pairwise Hellinger |")
    say("|---|---|---|")
    for k, (v, n) in res.items():
        say(f"| {k} | {n} | {v:.3f} |")
    rep["A3_3_mean_pairwise_hellinger"] = {k: {"n": n, "mean": round(v, 4)} for k, (v, n) in res.items()}
    red = 100 * (res["oecd_draft"][0] - res["oecd_final"][0]) / res["oecd_draft"][0]
    say(f"→ draft → final reduction: {red:.1f}%")
    rep["A3_3_reduction_pct"] = round(red, 1)
    say()

    # KR / IE to canonical centroid
    say("## A3.3 — distance of KR and IE to the canonical centroid")
    dk2 = {}
    with (CLU / "clusters_oecd_ward_K2.csv").open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            dk2[r["country"]] = int(r["cluster"])
    dev_lab = dk2.get("KR")
    canon = [c for c in elig if dk2.get(c) is not None and dk2[c] != dev_lab]
    say(f"canonical set = draft Ward K=2 majority cluster, {len(canon)} countries: {','.join(canon)}")
    ci = [elig.index(c) for c in canon]
    out = {}
    for tag, P in (("draft", PDn), ("final", PFn)):
        cen = P[ci].mean(axis=0)
        cen = cen / cen.sum()
        for c in ("KR", "IE"):
            i = elig.index(c)
            d = float(np.sqrt(0.5 * ((np.sqrt(P[i]) - np.sqrt(cen)) ** 2).sum()))
            out[f"{c}_{tag}"] = round(d, 3)
        # also mean distance of canonical members to their own centroid, for scale
        dd = [float(np.sqrt(0.5 * ((np.sqrt(P[i]) - np.sqrt(cen)) ** 2).sum())) for i in ci]
        out[f"canonical_mean_to_centroid_{tag}"] = round(float(np.mean(dd)), 3)
        out[f"canonical_max_to_centroid_{tag}"] = round(float(np.max(dd)), 3)
    for k, v in out.items():
        say(f"  {k}: {v}")
    rep["A3_3_centroid_distances"] = out
    say()

    # ---------- write
    (CLU / "oecd_final_verification.json").write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
    (CLU / "oecd_final_verification.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[out] {CLU / 'oecd_final_verification.json'}")
    print(f"[out] {CLU / 'oecd_final_verification.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
