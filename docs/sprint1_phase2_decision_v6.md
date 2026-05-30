# Sprint 1 — Phase 2 Decision Memo (v6)

**Date:** 2026-05-30
**Author:** AILIT_TRAVEL project lead
**Status:** Phase 2 GO — robustness battery starts now
**Inputs:** post-fix 25 × 12 matrices (`data/adherence_matrix/sprint1_25x12_pct_{v1,v2}.csv`), Hellinger clustering (`data/clustering/*_post_fix`)
**Supersedes:** v5 memo (which used the pre-fix matrix with broken MX-01 + Saudi-contaminated ZA)

---

## 1. What changed since v5

The user re-ran harvest + the full pipeline on the macOS environment. Three remediations from v5 landed in this run:

| Fix | v5 (pre-fix) | v6 (post-fix) | Effect |
|---|---|---|---|
| MX-01 OCR | 8,359 sents, **0 aligned** (CID font, garbage) | 2,177 OCR'd sents, **1,198 aligned (55 %)** | MX moves from n = 55 → n = 1,253 |
| ZA-01 source | Phoca landing page, 4 sents, 1 aligned | gov.za direct PDF, 1,934 sents, **1,225 aligned (63 %)** | ZA moves from n = 94 (Saudi contamination) → n = 1,225 |
| CN-03 drop | 0-char scanned PDF in pipeline | `DROP:` sentinel respected | clean exit (1 doc dropped, not failed) |

**Total corpus alignment now:** 23,961 (v2) / 24,532 (v1) aligned sentences at θ = 0.35 — up from 21,632 / 22,130 in v5. Yield rate **66.8 % (v2) and 68.4 % (v1)** — pilot range was 53–55 %.

Two remediations did **not** fully land and are flagged below:

- **ZA-02** (replacement = ISC South Africa case study at council.science): the file is 403-blocked by the cloud CDN for scripted curl from the user's macOS machine as well as from the analysis sandbox. ZA in the v6 matrix rests on ZA-01 only (1,225 sents) — defensible but n is lower than the original two-document target. *Action:* user can browser-download from `https://council.science/wp-content/uploads/2025/02/AI-Paper-Case-Study-South-Africa_V2.pdf` and re-run pipeline; not a blocker for Phase 2 entry.
- **SG-03**: the moe.gov.sg AI-in-Education page DOM changed between the v5 run (27 sents) and v6 run (14 sents). The total Singapore alignment drops from 506 → 493 sentences — negligible. *Action:* document as a Limitation; no re-fetch needed.

---

## 2. Post-fix aspect aggregation (the main empirical finding)

Aggregating the 12-anchor row to the four UNESCO aspects (A1 = HCM, A2 = Ethics, A3 = Techniques & Applications, A4 = System Design), the **dominant-aspect signature** for each country at v2 anchors is now:

| Dominant aspect | Countries | n |
|---|---|---|
| **A4 — System Design** | GB, SG, CN, JP, DE, FR, CA, IL, IN, EE, NO, SE, NL, ES, IT, SA, BR | **17** |
| **A1 — Human-Centred Mindset** | US, IE, MX, ZA | **4** |
| **A2 — Ethics of AI** | FI | **1** |
| **A3 — Techniques & Applications (Tool-use)** | KR | **1** |
| *insufficient n (< 50)* | AE (n = 7), AU (n = 42) | 2 |

Three changes from v5 are worth flagging:

- **MX moves to A1** (was A2 on n = 55 garbage; now A1 = 37.8 % on n = 1,253 clean OCR). The MX Agenda is heavier on civic-citizenship framing than on Ethics-as-action — a direct consequence of the IA2030Mx coalition's multi-stakeholder process, not a procedural / regulatory policy.
- **ZA moves to A1** (was A2 on n = 94 *Saudi* content). The gov.za draft policy is also dominated by S01 (Human agency) + S03 (Citizenship) — South Africa's draft frames AI in citizenship terms before scoping technical architecture.
- **KR's tool-use signature strengthens** (A3 = 42.8 %, up from 42.7 %). Adding fixed-data has not diluted the KR anomaly.

Conservatively, the manuscript should describe the finding as:

> "In a 23-country sample of national education-AI policy documents, the dominant UNESCO student-anchor aspect is **System Design (74 %)**, with **Human-Centred Mindset secondary (17 %)**. Two singletons — **Finland (Ethics-led)** and **Korea (Tool-use-led)** — depart from the canonical signature."

---

## 3. Hellinger clustering — post-fix result

Running `scripts/03_analysis/hellinger_cluster.py` on the new matrices (23 countries retained after the `--min-aligned 50` filter excludes AE and AU):

| K | v2 Ward silhouette | v1 Ward silhouette |
|---|---|---|
| **2** | **0.378** | **0.414** |
| 3 | 0.229 | 0.249 |
| 4 | 0.212 | 0.252 |
| 5 | 0.239 | 0.196 |
| 6 | 0.234 | 0.180 |

Best K = 2 on both anchor versions. The post-fix silhouette at K = 2 is **higher** than the pre-fix matrix (0.378 vs 0.349 for v2; 0.414 vs 0.390 for v1) — the cleaned MX / ZA rows tighten the canonical cluster.

The K = 2 partition is identical across v1 and v2:

- **Cluster 1 (n = 2): KR, IE** — dominant anchor S08 (Application skills) at 27 % v2 / 25 % v1
- **Cluster 2 (n = 21): everyone else** — dominant anchor S10 (Problem scoping) at 23 % v2 / 21 % v1

At K = 4 (the original "4-pattern" hypothesis target), the Ward partition does *not* recover an Ethics cluster or a Human-Centred cluster cleanly — instead it gives:

- {KR, IE} — tool-use
- {CN, SE, ES, SA} — strong S10 with S07 secondary
- {EE, BR} — small mixed
- {GB, SG, FI, US, JP, DE, FR, CA, IL, IN, NO, NL, IT, MX, ZA} — canonical

The original 4-cluster hypothesis is **not supported** at the statistical-silhouette level. The empirical structure is **1 canonical pattern + 1 robust deviation (Tool-use)** — plus sub-structure within the canonical mass that the manuscript can describe but should not over-claim as separate clusters.

---

## 4. Phase 2 entry — final checklist

| # | Criterion | Status |
|---|---|---|
| C1 | ≥ 20 countries with ≥ 100 aligned sents | **23 / 25** (only AE and AU short — documented Limitations) |
| C2 | Dual-anchor (v1 ↔ v2) concordance ≥ 80 % | **Cluster partition K = 2 is identical** across v1 and v2 |
| C3 | Threshold sensitivity preserves dominant-aspect ordering | passed in Sprint 0 sweep — Phase 2 will redo on full corpus |
| C4 | Inverse-corpus-weighted analysis | currently only 5 pilot countries → **must extend to 25 in Phase 2 IV.2** |
| C5 | US-01 sub-sampling | passed (preserved) |
| C6 | Each identified failure mode has an explicit remediation logged | passed (MX-01 OCR, ZA-01 replacement, ZA-02 documented, CN-03 dropped) |

**Verdict: Phase 2 — GO.**

---

## 5. Phase 2 robustness battery — module sequence

The plan was 6 robustness modules. With v6 matrix in hand, the priority order is:

1. **IV.2 inverse-corpus weighting — extend to 25 countries** (currently `scripts/04_robustness/inverse_corpus_weighting.py` operates on the 5-pilot path). This is the single criterion still unchecked (C4).
2. **Leave-one-out per country** — does dropping the largest document (KR-02 4,041 sents; FI-01 2,944 sents; FR-03 1,791 sents) change KR's tool-use signature or FI's Ethics signature?
3. **Bootstrap re-sampling** of aligned sentences → 95 % CI on the per-country dominant-aspect share.
4. **Sub-sampling** of US-01 (already done), plus uniform-cap sub-sampling to N = 500 per country for cluster stability.
5. **Temporal cohort split** — pre vs post 2024-09 (UNESCO framework release). Does post-cohort show different anchor distribution?
6. **Negative corpus × 2** — (a) curriculum-only docs vs strategy docs; (b) non-policy AI texts (ArXiv ML papers) should *not* cluster with policy texts.
7. **Discriminant** — train a linear classifier on the 12 features and check whether KR / IE separate cleanly from cluster 2 (out-of-sample fold).

Module 1 is the next concrete deliverable.

---

## 6. Open items for the next memo (v7 — after IV.2 ext.)

- Does the 25-country inverse-weighted analysis preserve the {KR, IE} cluster?
- Does it move any of the canonical-cluster countries into the deviating cluster (concept: heavily-weighted policy might flip)?
- Does the KR : ethics ratio (the original Paper C statistic) survive the size-correction?

**End v6 memo.** Next checkpoint after Phase 2 module 1 (inverse-weighting extended).
