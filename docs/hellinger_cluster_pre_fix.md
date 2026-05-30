# Hellinger clustering — pre-fix snapshot

**Date:** 2026-05-30
**Inputs:** `data/adherence_matrix/sprint1_25x12_pct_v2.csv` (and v1)
**Outputs:** `data/clustering/{hellinger_dist_*.csv, clusters_*_K{2,3,4}.csv, dendrogram_*.png}`

This is the *first* Hellinger clustering pass, run **before** the MX-01 OCR
re-alignment and the ZA-01 / ZA-02 corpus replacements land. AE and AU
(n=7, n=42) are excluded by the `--min-aligned 50` filter so they do not
distort silhouette geometry. 23 / 25 countries retained.

## What survives the sensitivity check

Across v1 and v2 anchors, **two clusters are stable**:

1. **{KR, IE}** — dominant anchor **AILIT-S08 Application skills (Tool-use)**.
   KR ~25-30 % S08, IE ~23 % S08. This is the strongest signal in the matrix.
   The 4-pattern hypothesis predicted Korea would isolate as Tool-use;
   Ireland's joining is the surprise — and it matches the Junior Cert
   "AI in Schools" pilots, which are heavily oriented around concrete
   tool-use rather than human-rights framing.

2. **{MX, ZA}** — currently dominant on S05 (v1) / S03 (v2). **This cluster
   is an artifact of bad data**: MX is currently 55 sentences (only MX-02;
   MX-01 was CID-broken, now OCR'd but not yet re-aligned) and ZA-02 was
   accidentally Saudi-Arabia content. Both rows will be replaced on the
   next pipeline run.

## What silhouette says about K

| K | v2 Ward | v2 Avg | v1 Ward | v1 Avg |
|---|---|---|---|---|
| 2 | **0.349** | **0.349** | 0.390 | 0.390 |
| 3 | 0.346 | 0.346 | **0.392** | **0.392** |
| 4 | 0.256 | 0.269 | 0.243 | 0.299 |
| 5 | 0.222 | 0.249 | 0.251 | 0.270 |
| 6 | 0.243 | 0.237 | 0.193 | 0.243 |

Best K is **2 (v2) / 3 (v1)** — not 4. The 4-pattern hypothesis does not
survive the silhouette check at K = 4 on this matrix. The natural
partition is **"canonical majority (n ≈ 21) + 2 outlier pairs"**.

This is consistent with the manuscript-ready reading already drafted in
`sprint1_phase2_decision.md` §3 — **one canonical pattern (System-Design,
~70 % of countries) + a small set of policy outliers**. The 4-pattern
language must be reframed in the manuscript from "four clusters" to
"one canonical pattern + three deviating signatures".

## Open question for the post-fix re-run

Once MX-01 contributes ~1,000 OCR'd Spanish sentences and ZA-01 + ZA-02
draw from gov.za + ISC (instead of a Saudi mislabel), three things may
shift:

- MX could move from the "outlier pair with ZA" into either the canonical
  cluster or a clean Ethics-dominant signature (the §3 reading of v4
  memo placed MX in A2 Ethics).
- ZA likely lands in the canonical cluster — South Africa's draft policy
  is heavy on national-strategy framing, which sits in S10 Problem
  scoping.
- Silhouette at K = 4 may rise as the {MX, ZA} artifact cluster
  dissolves, but the **{KR, IE} Tool-use cluster** should remain the
  paper's anchor finding.

## Files produced

- `data/clustering/hellinger_dist_v2.csv` — 23 × 23 Hellinger distances (v2)
- `data/clustering/hellinger_dist_v1.csv` — same on v1 anchors
- `data/clustering/clusters_v{1,2}_{ward,average}_K{2,3,4}.csv` — labelled
  assignments at each K
- `data/clustering/dendrogram_v{1,2}_ward.png` — Ward dendrograms for visual
  inspection of where each country joins the tree

**Next checkpoint:** rerun `scripts/03_analysis/hellinger_cluster.py --tag
v2` after the user-side harvest + pipeline rebuild, and overwrite this
memo with the post-fix reading.
