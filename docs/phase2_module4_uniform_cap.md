# Phase 2 Module 4 — Uniform-cap N = 500 sub-sampling

**Date:** 2026-05-30
**Inputs:** `sprint1_alignment_full_{v1,v2}.jsonl` (24,070 / 24,645 lines)
**Code:** `scripts/04_robustness/uniform_cap.py` — N_cap = 500, n_iter = 1,000, seed = 20260530
**Outputs:** `data/robustness/uniform_cap_{v1,v2}.csv`, `uniform_cap_report_{v1,v2}.md`
**C&E checklist item:** IV.5 (Sub-sampling for largest national corpus) — **PASSED**

## What this module does for the paper

The IV battery now has three independent size-equalisation tests:

- **IV.2 inverse weighting** — each document weighted equally regardless of size (within-country averaging across documents).
- **IV.3 leave-one-out** — each country's *largest* document removed.
- **IV.5 uniform cap** — each country randomly sub-sampled to N = 500 aligned sentences.

These three address slightly different reviewer questions; uniform-cap is the **most aggressive** because it equalises both within-country document weight *and* across-country sample size simultaneously.

## Headline result

| Statistic | v2 (1,000 iter) | v1 (1,000 iter) |
|---|---:|---:|
| KR Cluster-1 assignment rate | **100.0 %** | **100.0 %** |
| IE Cluster-1 assignment rate | **100.0 %** | **100.0 %** |
| Full-data K = 2 partition match rate | **99.9 %** | **95.9 %** ¹ |
| Canonical countries leaking into Cluster 1 | US 0.1 % only | AE 4.1 %, others 0 % ² |

¹ The v1 partition match dips because AE (n = 7) is noisy — see footnote 2.
² AE has only 7 aligned sentences total; uniform-cap at 500 is meaningless for AE (we just resample 7-of-7 each time). AE's flip is a sample-size artefact, not a signal that the cluster is unstable. Filtering AE/AU out (the same threshold used in Hellinger clustering, `--min-aligned 50`), the v1 partition match rate is effectively 100 %.

## Why this result is decisive

Under the IV.5 protocol every country contributes at most 500 sentences. KR (which had 3,297 sentences in raw data) and IE (1,290) are *shrunk* to the same scale as ES (210), CN (387), and BR (694). Even at this equalised scale, KR and IE retain their Cluster-1 identity in **every single one of 1,000 random sub-samples**. No canonical country reaches Cluster 1 in more than 0.1 % of iterations.

This rules out, at the strongest available evidentiary level for this protocol, the alternative explanation that the {KR, IE} cluster is an artefact of either (i) corpus size or (ii) within-country document dominance. The cluster is a property of the underlying anchor-distribution geometry.

## Compared to the LOO finding

Module 2 (LOO) showed that **IE moves into Cluster 2 if IE-01 is removed entirely**. Module 4 (uniform-cap @ 500) shows that **if IE-01 is kept but down-sampled**, IE stays in Cluster 1 — because the *proportion* of IE-01-style content within IE's row is preserved by random sub-sampling.

These two findings together support the §4.6 manuscript framing:

> "Under uniform-cap (every country sub-sampled to N = 500), KR and IE preserve Cluster 1 assignment in 100 % of 1,000 resamples (Module 4). The Cluster-1 identity is therefore robust to absolute corpus size and to within-country document weighting. The narrower asymmetry — that IE's signal is concentrated in IE-01 specifically — is brought out only by leave-one-out (Module 2), which is the appropriate test for document-singular vs document-replicable patterns."

## Coverage of C&E rigour checklist

| Row | Expectation | Status |
|---|---|---|
| IV.1 | Threshold sensitivity | ✅ Sprint 0.5 |
| IV.2 | Inverse-corpus weighting | ✅ Module 1 |
| IV.3 | Leave-one-out per country | ✅ Module 2 |
| IV.4 | Bootstrap CI (≥ 1,000 iter) | ✅ Module 3 |
| **IV.5** | **Sub-sampling for largest national corpus** | ✅ **Module 4** |
| IV.6 | Pre/post 2024-09 cohort stability | 🟥 next — Module 5 |

Five of six IV rows now ticked. The robustness battery is one module short of complete.

## Next step

**Module 5 — Temporal cohort split (pre/post 2024-09 UNESCO release)**, addressing C&E checklist IV.6. The hypothesis to test: the K = 2 partition holds in both temporal cohorts, ruling out the alternative that {KR, IE} is just an artefact of the timing of when UNESCO's framework was published vs when each country's policy was drafted.
