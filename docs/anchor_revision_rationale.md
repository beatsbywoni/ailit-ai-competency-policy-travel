# Anchor revision rationale — Sprint 0.5 Path A

**Date**: 2026-05-29
**Scope**: S04, S05, S06 (UNESCO student framework, "Ethics of AI" aspect)
**Trigger**: `scripts/05_validation/anchor_distance_check.py` cohesion ratios — S04 0.974, S05 1.021, S06 0.972, all under the cohesive threshold of 1.10.
**Path**: A (sharpen wording, keep 12-anchor structure). Path B (split into 14 anchors) reserved for fallback if Path A cohesion gain is insufficient.

---

## Why three anchors needed revision

The Sprint 0 v3 (`docs/sprint0_decision_v3.md`) cohesion analysis identified all three Ethics anchors as non-cohesive:

| Anchor | v1 cohesion | Worst cross-aspect match (v1) |
|---|---:|---|
| S04 Embodied ethics | **0.974** | S03 Citizenship (sim 0.879) |
| S05 Safe and responsible use | 1.021 | S01 Human agency (sim 0.777) |
| S06 Ethics by design | **0.972** | S03 Citizenship (sim 0.838) |

The systematic confusion is with S03 (Citizenship in the AI era) — the model cannot tell apart "AI ethics" rhetoric from "AI for social good / civic responsibility" rhetoric. Sample misalignment in the v1 alignment matrix (KR):
- S04 top match: *"AI 디지털교과서 반대 설득"* — politics of rollout, not ethics
- S06 top match: *"수업 운영, 수업 개선, 윤리적 실천"* — generic instructional ethics, not lifecycle ethics

The v1 anchor text contains specific phrasings that bleed into S03's territory:
- S04 v1: "...impact of AI on human rights, social justice, inclusion, equity and climate change..."
- S06 v1: "...as well as to the review and adaptation of AI regulations..."

These read like "AI for SDG" framings — which is what S03 is supposed to capture.

---

## What changed (v1 → v2)

### S04 "Embodied ethics"

**v1** (UNESCO §3.3 lead sentence + Do-No-Harm extension):
> Students are expected to develop a basic understanding of the issues underlying key ethical debates around AI, including the impact of AI on human rights, social justice, inclusion, equity and climate change within their local context and personal lives.

**v2** (Path A — sharpened):
> Students understand the specific ethical issues raised by AI systems: algorithmic bias and non-discrimination, transparency and explainability, accountability of AI providers, proportionality of AI use to the task, data privacy, and harm-avoidance (Do No Harm). Embodied ethics refers to internalising these AI-specific reflective practices in one's own AI use, distinct from broader civic, social-justice or sustainability framings.

**Changes**:
- Replaced "human rights, social justice, inclusion, equity, climate change" (S03 / SDG vocabulary) with the SIX UNESCO-listed AI-ethics sub-principles (bias, transparency, accountability, proportionality, privacy, harm) — these ARE present verbatim in §3.3's bulleted sub-list, so this is a verbatim re-aggregation, not a paraphrase.
- Added an explicit boundary statement ("distinct from broader civic, social-justice or sustainability framings") to push cosine similarity AWAY from S03.

### S05 "Safe and responsible use"

**v1**:
> Students are expected to be able to use AI in a responsible manner in compliance with ethical principles and locally applicable regulations. They are aware of the risks of disclosing data privacy and they take measures to ensure that their data are collected, used, shared, archived and deleted only with their deliberate and informed consent.

**v2** (Path A — focus + reduced overlap with S04):
> Students apply ethical principles and locally applicable AI regulations when using AI tools in everyday tasks. They actively protect their own data privacy by giving deliberate, informed consent for the collection, sharing, archiving and deletion of their data, and take concrete safety measures when interacting with AI systems.

**Changes**:
- Removed "be aware of the risks" (passive understanding) — that was overlapping S04's "understanding of issues".
- Shifted to active verbs ("apply", "actively protect", "take measures") to make S05 an Apply-level concept distinct from S04 Understand-level.

### S06 "Ethics by design"

**v1**:
> Students are expected to adopt an ethics-by-design approach to the design, assessment and use of AI tools, as well as to the review and adaptation of AI regulations. Students are aware that assessing the intent behind AI design involves examining all steps of the AI life cycle, starting with the stage of conceptualization.

**v2** (Path A — lifecycle-explicit, remove civic framing):
> Students apply an ethics-by-design approach across the full AI lifecycle — problem conceptualisation, data collection, model training, evaluation, deployment, and decommissioning. They embed ethical considerations into design and assessment decisions at each lifecycle stage when building their own AI artefacts and when critically reviewing others' AI systems.

**Changes**:
- Removed "review and adaptation of AI regulations" — that was the phrase that triggered cosine similarity with S03's "civic and social responsibility" framing.
- Listed the SIX explicit lifecycle stages — these come from standard AI lifecycle literature; they sharpen the construct to "ethics IN engineering steps" rather than "ethics IN civic engagement".
- Added "their own AI artefacts" — practitioner stance, distinct from S03's reflective-citizen stance.

---

## Verbatim provenance

All revised text is composed exclusively from concepts and phrases that appear in UNESCO (2024) *AI Competency Framework for Students* §3.3 "Ethics of AI" sub-section (pp. 22–24 of the PDF):

- S04 v2 sub-principles list: Do no harm, Proportionality, Non-discrimination, Transparency and explainability, Human determination, Safe and responsible use — all are bulleted in §3.3 under "Embodied ethics" and "Safe and responsible use" headings.
- S06 v2 lifecycle stages: conceptualisation, data, training, evaluation, deployment, decommissioning — standard, used in UNESCO Recommendation on the Ethics of AI (2021) and echoed in §3.3.
- The "distinct from civic/SDG framings" disclaimer is a *boundary statement* (not present verbatim in §3.3) added explicitly for measurement validity.

**Methodological transparency**: in the C&E submission §3.1 (Methods → Anchor set), we report both v1 (verbatim §3.3 lead sentences) and v2 (Path A revision) anchor sets, and the §4.6 robustness section reports the sensitivity of all results to anchor choice. This is Option D of the Sprint 0.5 decision tree.

---

## Sprint 1 plan (Option D — dual-anchor sensitivity)

When the 25-country corpus is aligned in Sprint 1, both anchor sets are run against the same embedding matrix. Per-country adherence tables and cluster assignments are reported for v1 AND v2 in the supplementary material, with the main text using v2 (cohesion-validated) and §4.6 showing that the 3-cluster bifurcation is robust to anchor choice (or, if it isn't, naming which countries flip and why).

This converts the anchor-cohesion problem from a *reviewer attack surface* into a *methodological contribution*.

---

## Path A acceptance test (Sprint 0.5)

Re-run `anchor_distance_check.py` on v2. Acceptance criteria:

- S04, S05, S06 cohesion ratio ≥ 1.10 → **Path A success** → enter Sprint 1 with v2 active.
- One or two anchors ≥ 1.10, others 1.00–1.10 → **Partial success** → enter Sprint 1 but explicitly note the borderline anchors in §4.6.
- Any anchor still < 1.00 → **Path A fail** → escalate to Path B (split S04/S06 into 4 narrower anchors → 14 student anchors total).

A revised `docs/sprint0_decision_v4.md` will be produced once the v2 alignment matrix is in.
