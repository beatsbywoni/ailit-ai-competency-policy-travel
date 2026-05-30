# Sprint 1 plan — 25-country corpus expansion + robustness + cross-organisational

**Start**: 2026-05-30
**Target end**: 2026-07-11 (6 weeks)
**Hard upper bound**: 2026-07-25 (± 2-week slip)
**Anchor regime**: v2 active for primary results; v1 archived for §4.6 sensitivity (Option D)
**Owner**: [Author withheld during anonymous peer review]
**Decision gates**: end of each phase

---

## Why this exists

Sprint 0/0.5 closed with a clean **4-pattern bifurcation** finding at n = 5. Sprint 1 expands to n = 25 to test whether the pattern (i) generalises, (ii) fragments into more clusters, or (iii) collapses. Sprint 1's outputs are the empirical core of the Computers & Education submission.

Every phase is sequenced so that any sub-output is publishable at its own granularity even if subsequent phases slip.

---

## Phase 1 — Corpus expansion (Week 1–2, target 2026-06-12)

### Goals
- 20 new countries added to inventory with verified URLs (≥ 1 doc/country in priority genres 1–3).
- Idempotent harvest infrastructure scaled from 20 to 50–80 documents.
- Inventory + provenance log complete.

### Deliverables
1. `data/corpus_inventory/sprint1_urls.csv` — 25 countries × 2–4 docs each, ~60–80 rows.
2. `scripts/01_corpus/04_harvest_sprint1.sh` — same idempotent pattern as pilot script; supports `--country` filter.
3. `data/corpus_full/raw/` — downloaded documents.
4. `data/corpus_inventory/excluded.md` — countries / docs we couldn't find, with reason.

### Country list (20 new)

| Region | Countries |
|---|---|
| East Asia frontier / fast follower | China, Japan |
| Europe frontier | Germany, France |
| Western frontier | Canada, Australia |
| Frontier (other) | Israel, India |
| Nordic | Norway, Sweden |
| EU continental | Estonia, Netherlands, Ireland, Spain, Italy |
| Middle East | UAE, Saudi Arabia |
| Latin America | Brazil, Mexico |
| Africa | South Africa |

### Phase 1 decision gate
- ≥ 22/25 countries with ≥ 1 priority-genre document → enter Phase 2.
- 18–21/25 → expand search; allow 1-week slip.
- < 18/25 → escalate; reconsider sampling frame.

---

## Phase 2 — Robustness battery (Week 3–4, target 2026-06-26)

### Goals
Complete planning §7.9 robustness checks at scale and the §7.10 construct-validity battery.

### Deliverables
1. `scripts/04_robustness/inverse_corpus_weighting.py` — re-weight per document by 1/sentence-count.
2. `scripts/04_robustness/leave_one_out.py` — drop one country at a time; report 4-pattern stability.
3. `scripts/04_robustness/bootstrap.py` — country-level resampling × 1,000.
4. `scripts/04_robustness/sub_sample.py` — for documents > 5,000 sentences, sample 2,000 and recompute.
5. `scripts/04_robustness/temporal_cohort_check.py` — pre/post 2024-09 split, report cohort-specific matrix.
6. `scripts/05_validation/build_negative_corpus.py` — Wikipedia astronomy / cuisine / sports; report anchor over-match rate ≤ 5% target.
7. `scripts/05_validation/build_hard_negative_corpus.py` — Wikipedia AI history + tech journalism; report ≤ 15% over-match target.
8. `scripts/05_validation/discriminant_validity_check.py` — combined report.
9. Robustness composite figure (Sprint 2 input).

### Phase 2 decision gate
- 4-pattern bifurcation persists in ≥ 4 of 5 robustness checks → enter Phase 3.
- Pattern persists in 2–3 of 5 → enter Phase 3 but flag which checks weaken signal.
- Pattern fails in ≥ 4 of 5 → halt, revisit anchors or sampling.

---

## Phase 3 — Cross-organisational + RQ analysis (Week 5, target 2026-07-04)

### Goals
RQ3 (temporal), RQ4 (cross-org), RQ5 (compressed-diffusion typology) all analysed against the 25-country matrix.

### Deliverables
1. `anchors/eu_ai_act_education_2024.csv` — EU AI Act education provisions extracted verbatim (3–5 anchors).
2. Run alignment against all anchor sets (UNESCO student 12 + teacher 5 + OECD 4 + EU 3–5 = ~25 anchors).
3. `scripts/03_analysis/cross_org_alignment.py` — per-country dominant-framework report.
4. `scripts/03_analysis/temporal_cohort_diff.py` — pre/post 2024-09 change per anchor per country.
5. `scripts/03_analysis/compressed_diffusion_typology.py` — planning §7.8 decision-rule classification.
6. Clustering: Hellinger + Ward, 4-cluster solution, dendrogram + cluster table.
7. `docs/sprint1_decision.md` — Sprint 1 verdict + manuscript-headline candidates.

### Phase 3 decision gate
- All four RQ deliverables present and interpretable → enter Phase 4.

---

## Phase 4 — Manuscript prep + Sprint 2 handoff (Week 6, target 2026-07-11)

### Goals
Convert Sprint 1 outputs into manuscript skeleton and prepare Sprint 2 (drafting) entry.

### Deliverables
1. `manuscript/manuscript_v0.md` — IMRaD outline filled with Sprint 1 numbers.
2. `manuscript/figures/` — 6 candidate figures (per-country heatmap, domain stacked bars, temporal scatter, cross-org radar, dendrogram, robustness composite).
3. `manuscript/highlights.md` — 5 bullets, ≤ 85 char each.
4. `docs/sprint1_progress.md` — final cumulative log.
5. Updated `docs/ce_rigour_checklist.md` with Sprint 1 status.
6. `planning_v2.md` — updated planning doc with revised hypotheses, 21-anchor structure, four-pattern framework.

### Phase 4 decision gate
- Manuscript skeleton + figures + Sprint 2 plan ready → Sprint 2 begins.

---

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | URL discovery for 5+ countries fails (closed government sites, paywalls) | Medium | Medium | Backup: OECD AI Observatory inventory; UNESCO IIEP reports; AI4SDG; bilateral donor reports |
| R2 | Languages with weak multilingual-mpnet support (Portuguese for Brazil, Arabic for UAE/SA) | Low | Low | Cross-language sanity check; for very weak signal, supplement with English-summary version |
| R3 | Single mega-document distorting per-country signal again (similar to KR-02) | High | Medium | IV.2 inverse-corpus weighting; reported in §4.6 |
| R4 | EU AI Act anchor extraction non-trivial (regulation, not framework) | Medium | Low | Use Article 4 (AI literacy) + Recital 56 (education) text only; document choice |
| R5 | Reviewer demands sentence-level human inter-rater κ | Medium | Medium | Defence: Paper C precedent (Bromley/Nachtigal/Kijima 2024 Comp Ed) + construct-validity argument |
| R6 | Scoop risk: another team publishes UNESCO Framework reception baseline | Medium | High | Stay on 2026-11-15 submission target; if scooped, pivot to "first cross-organisational reception" framing |
| R7 | OECD AILit framework final version differs from May 2025 draft | Low | Low | Re-extract anchors at Sprint 2 freeze |
| R8 | C&E reviewer flags v2 anchor revision as ex-post-hoc adjustment | Medium | High | Mitigation: anchor cohesion was measured BEFORE revision; revision rationale doc is pre-registered logically; report both v1 and v2 results in §4.6 |

---

## Phase-1-now starter pack

1. `data/corpus_inventory/sprint1_urls.csv` skeleton with all 25 country headers and pilot 5 rows pre-filled.
2. First-batch URL searches scheduled for: China, Japan, Germany, France, Canada, Australia.
3. `scripts/01_corpus/04_harvest_sprint1.sh` modelled on the pilot harvest with `--country` filter and `corpus_full/raw/` target.

The starter pack is shipped at the same time as this plan; see corresponding files.

---

## Sprint 2 preview

Sprint 2 (~Week 7–12) is manuscript drafting against the Sprint 1 results:
- Manuscript v1 → v3
- Figures finalised
- Korean reference draft (`manuscript_ko.md`)
- Submission preparation begins at week 11

Sprint 3 (~Week 13–15) is submission packaging.

Total to target submission **2026-11-15**: ~24 weeks from now. Slack ≈ 3 weeks if Sprint 1 stays on schedule.
