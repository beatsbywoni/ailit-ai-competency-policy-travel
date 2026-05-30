# C&E rigour checklist — living document

**Target journal**: *Computers & Education* (Elsevier, SSCI Q1, IF 13.85)
**Last updated**: 2026-05-29 (Sprint 0 → Sprint 1 boundary)
**Discipline**: every project decision is logged here against C&E publication-standard expectations. Updated at the end of each Sprint phase.

---

## How this file is used

Before submitting any output for review, walk this checklist. Each row is a methodological choice + the explicit C&E rationale + current status + Sprint stage where it's resolved. Decisions are not "done" until the manuscript citation and replication-archive evidence are both in place.

Legend: ✅ in place · 🟨 partial / Sprint 1 work · 🟥 missing · ⬛ Sprint 2 / post-acceptance

---

## I. Construct validity & measurement

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| I.1 | Anchor sentences extracted verbatim from authoritative source | ✅ UNESCO §3.3 verbatim for 9 unchanged anchors; v2 revisions composed exclusively from §3.3 sub-principles + lifecycle stages | `docs/anchor_revision_rationale.md`, `anchors/unesco_ai_student_2024.csv` | Sprint 0.5 |
| I.2 | Anchor cohesion measured quantitatively | ✅ 21×21 cosine matrix + within/between aspect cohesion ratio | `data/validation/anchor_cohesion_v2.csv` | Sprint 0.5 |
| I.3 | Over-recruiting anchors identified and revised | ✅ S04 0.97 → 1.16; S05/S06 borderline (documented) | `docs/sprint0_decision_v4.md` §"Cohesion improvements" | Sprint 0.5 |
| I.4 | Discriminant validity against off-domain text (negative corpus) | ✅ 0.0 % alignment on Gatsby + WWI + Photosynthesis (n=3,271; v1 0.1 %) — unambiguously passed | `scripts/05_validation/discriminant_validity.py`; `docs/phase2_module6_discriminant.md` | Sprint 1 Phase 2 |
| I.5 | Discriminant validity against adjacent-domain text (hard negative) | 🟨 partial — Google/Microsoft AI policy aligns at 68.9 % (similar concept space). WHO + DoD failed extraction (Limitation §6). Manuscript reframes as concept-space alignment per §3 | `scripts/05_validation/discriminant_validity.py`; `docs/phase2_module6_discriminant.md` | Sprint 1 Phase 2 |
| I.6 | Anchor versioning preserved for sensitivity analysis | ✅ v1 archived; v2 active; both runnable via `--student-csv` | `anchors/unesco_ai_student_2024_v1_archived.csv` | Sprint 0.5 |

## II. Sample & corpus

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| II.1 | Inclusion criteria pre-stated and applied transparently | ✅ planning §6.2 priorities (strategy / curriculum / guidance / report / legislation) | `AILIT_TRAVEL_planning_v1.md` §6.2 | Sprint 0 |
| II.2 | Documents have ≥ 1 from priority genres 1–3 per country | ✅ pilot 5/5; Sprint 1 25/25 target | `data/corpus_inventory/sprint1_urls.csv` | Sprint 1 Phase 1 |
| II.3 | Pre/post 2024-09 cohort transparent per document | ✅ `unesco_cohort` column | `data/corpus_inventory/*.csv` | Sprint 0 |
| II.4 | Corpus provenance documented for reviewers | ✅ harvest_log.tsv + provenance notes in inventory README | `data/corpus_pilot/raw/_harvest_log.tsv` | Sprint 0 |
| II.5 | Third-party mirrors flagged (KR-01..03 EduNet/EIEC) | ✅ in `data/corpus_inventory/README.md` | inventory README | Sprint 0 |
| II.6 | Document weighting strategy to handle single-doc dominance | 🟨 inverse-corpus weighting script in progress | `scripts/04_robustness/inverse_corpus_weighting.py` | Sprint 1 Phase 2 |
| II.7 | Excluded countries documented | 🟥 will produce after Sprint 1 inventory pass | `data/corpus_inventory/excluded.md` | Sprint 1 Phase 1 |

## III. Method transparency

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| III.1 | Embedding model + version pinned | ✅ `paraphrase-multilingual-mpnet-base-v2` documented + pinned in requirements.txt | `requirements.txt` | Sprint 0 |
| III.2 | Threshold pre-stated (default 0.35) | ✅ planning §7.3 | planning §7.3 | Sprint 0 |
| III.3 | Threshold sensitivity reported | ✅ 0.30 / 0.35 / 0.40 / 0.45 / 0.50 sweep | `data/robustness/threshold_sweep_report.md` | Sprint 0.5 |
| III.4 | Anchor sensitivity (v1 vs v2) | ✅ infrastructure ready; v2 sharper | `data/adherence_matrix/anchor_version_comparison.md` | Sprint 0.5 |
| III.5 | Pipeline reproducible end-to-end with one command | ✅ `run_sprint0_pipeline.sh`, `run_sprint0_v2.sh`, `run_sprint0_5.sh` | repo root | Sprint 0 |
| III.6 | All transformations idempotent + logged | ✅ atomic write + skip-existing | `scripts/02_pipeline/*` | Sprint 0 |

## IV. Robustness (planning §7.9)

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| IV.1 | Threshold sensitivity (0.30–0.50) | ✅ done for v1; redo for v2 in Sprint 1 | `scripts/04_robustness/threshold_sensitivity.py` | Sprint 0.5 / Sprint 1 |
| IV.2 | Inverse-corpus weighting (downweight large docs) | ✅ 25-country v1+v2; KR + IE preserve Cluster 1 across raw/weighted | `scripts/04_robustness/inverse_corpus_weighting.py --corpus full`; `docs/phase2_module1_inverse_weighting.md` | Sprint 1 Phase 2 |
| IV.3 | Leave-one-out per country | ✅ KR survives LOO; IE-01 carries all of IE's signal (key finding for §4.6) | `scripts/04_robustness/leave_one_out.py`; `docs/phase2_module2_loo.md` | Sprint 1 Phase 2 |
| IV.4 | Country-level bootstrap (1,000 iterations) | ✅ KR S08 +27 pp [95% CI 25.5–28.9]; IE +20 pp [18.0–22.7]; IE-01 vs IE-02 asymmetry +21 pp [17.2–25.3] — replicates on v1 | `scripts/04_robustness/bootstrap_ci.py`; `docs/phase2_module3_bootstrap.md` | Sprint 1 Phase 2 |
| IV.5 | Sub-sampling for largest national corpus | ✅ uniform-cap N=500 × 1000 iter: KR 100% / IE 100% Cluster-1 (v1 + v2) | `scripts/04_robustness/uniform_cap.py`; `docs/phase2_module4_uniform_cap.md` | Sprint 1 Phase 2 |
| IV.6 | Pre/post 2024-09 cohort stability | ✅ KR + IE preserved in both cohorts (v1 + v2); 7/9 with both-cohort sample agree; DE+US post→Cluster 1 = bonus temporal-convergence finding | `scripts/04_robustness/temporal_cohort.py`; `docs/phase2_module5_temporal_cohort.md` | Sprint 1 Phase 2 |

## V. Cross-organisational analysis (RQ4)

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| V.1 | UNESCO student × teacher anchor analysis (12 + 5) | 🟥 only student 12 used so far | `scripts/02_pipeline/07_embed_and_align.py --anchor-set all` | Sprint 1 Phase 3 |
| V.2 | UNESCO × OECD/EC domain comparison (4 OECD anchors) | 🟥 | same | Sprint 1 Phase 3 |
| V.3 | EU AI Act education provisions (planning §3 RQ4) | 🟥 — anchor extraction needed | `anchors/eu_ai_act_education_2024.csv` | Sprint 1 Phase 3 |
| V.4 | Compressed-diffusion typology decision rule | 🟥 planning §7.8 | `scripts/03_analysis/compressed_diffusion_typology.py` | Sprint 1 Phase 3 |

## VI. Reporting & open science

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| VI.1 | Open code repository (GitHub) | 🟨 local repo ready; private upload pending Sprint 3 | `ailit-ai-competency-policy-travel/` | Sprint 3 |
| VI.2 | Open data (Zenodo DOI minted at acceptance) | 🟨 `.zenodo.json` prepared | `.zenodo.json` | Sprint 3 |
| VI.3 | CITATION.cff for software citation | ✅ | `CITATION.cff` | Sprint 0 |
| VI.4 | Anonymised mirror for review (anonymous.4open.science) | 🟨 will produce at submission | submission folder | Sprint 3 |
| VI.5 | Replication README with one-line run-all | ✅ | `RUN_ME.md` + `run_sprint*.sh` scripts | Sprint 0 |
| VI.6 | Disclosure: AI assistance used in coding | 🟥 — explicit disclosure needed in §Acknowledgements | manuscript | Sprint 2 |

## VII. Sample size & generalisability

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| VII.1 | Adequate n for cross-national claim (n ≥ 20 typical for cross-national text analysis) | 🟨 25-country target locked | planning §6.1 | Sprint 1 Phase 1 |
| VII.2 | Country sampling justified (typology + availability) | ✅ frontier/fast-follower/receiver categories | planning §6.1 | Sprint 0 |
| VII.3 | Language coverage transparent | ✅ 11 languages documented; multilingual-mpnet supports all | planning §6.3 | Sprint 0 |
| VII.4 | Excluded countries (binding constraint = corpus availability) | 🟥 Sprint 1 Phase 1 task | inventory | Sprint 1 |

## VIII. Theoretical contribution

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| VIII.1 | Hypothesis pre-stated | ✅ planning §3 RQ1–RQ5 | `AILIT_TRAVEL_planning_v1.md` §3 | Sprint 0 |
| VIII.2 | Hypothesis revision (linear asymmetry → 4-pattern bifurcation) documented | ✅ | `docs/sprint0_decision_v4.md` §"four-pattern picture" | Sprint 0.5 |
| VIII.3 | Theoretical framework coherent (promissory legitimacy, compressed diffusion, neo-institutionalism, symbolic adoption) | ✅ planning §4 | `AILIT_TRAVEL_planning_v1.md` §4 | Sprint 0 |
| VIII.4 | Falsifiable claims | ✅ §10.1 gates were strict; v1 failed → method/anchor revised → v2 passes for Korea | Sprint 0/0.5 memos | ongoing |
| VIII.5 | Self-citation chain (prior work and parallel submission; details withheld during anonymous review) | ✅ planning §15 | planning §15 | manuscript |

## IX. Ethics & integrity

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| IX.1 | No human subjects / IRB not needed (policy text only) | ✅ documented in §6 | planning §4.5 | Sprint 0 |
| IX.2 | LLM disclosure (GPT/Claude assistance in coding/drafting) | 🟥 explicit statement in §Acknowledgements | manuscript | Sprint 2 |
| IX.3 | Self-plagiarism guard (Paper C INEE overlap declared) | ✅ planning §9 comparison table | planning §9 | Sprint 0 |
| IX.4 | Reflexive caveat (limits of text-only analysis) | ✅ planning §4.5 | planning §4.5 | manuscript |

## X. C&E house style

| # | C&E expectation | Current status | Where resolved | Sprint |
|---|---|---|---|---|
| X.1 | IMRaD structure | 🟥 manuscript not started | planning §8 outline ready | Sprint 2 |
| X.2 | Word limit 7,000–10,000 (empirical articles) | n/a | manuscript | Sprint 2 |
| X.3 | Structured abstract (150–250 words) | 🟥 | manuscript | Sprint 2 |
| X.4 | Elsevier-Harvard references | 🟥 — currently planning uses Chicago author-date | manuscript | Sprint 2 |
| X.5 | Highlights (3–5 bullets, ≤ 85 char each) | 🟥 | manuscript | Sprint 2 |
| X.6 | Graphical abstract (optional but recommended) | 🟥 | 4-pattern bifurcation figure candidate | Sprint 2 |

---

## Outstanding gaps before Sprint 1 fieldwork begins

🟥 critical (block Sprint 1 Phase 1): none. Phase 1 (corpus expansion) can start now.

🟥 critical (block Sprint 1 Phase 2 robustness analysis): IV.2 – IV.6, I.4, I.5. All have placeholder scripts planned and are scheduled in Phase 2.

🟥 critical (block Sprint 1 Phase 3): V.1 – V.4. Anchor preparation for EU AI Act needed before cross-org analysis.

Risk register: see `docs/sprint1_plan.md` §"Risks".
