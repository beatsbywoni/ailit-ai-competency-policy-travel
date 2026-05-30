# Anchor cohesion report

21 anchors across 3 frameworks. Cosine similarity from `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`, L2-normalised.

**Interpretation rules**:
- `cohesion_ratio = mean_within_group / mean_between_group`
- `> 1.10`: cohesive anchor — sits closer to in-group anchors than out-group
- `1.00–1.10`: borderline
- `< 1.00`: **OVER_RECRUIT** — anchor blurs into other groups; expect alignment to over-attract foreign-group sentences

## Per-anchor cohesion (UNESCO student aspects)

| Anchor | Group | within | between | ratio | worst cross-group match | flag |
|---|---|---:|---:|---:|---|---|
| AILIT-S01 | Human-centred mindset | 0.8889 | 0.7553 | 1.177 | AILIT-S10 (0.8066) |  |
| AILIT-S02 | Human-centred mindset | 0.8759 | 0.7197 | 1.217 | AILIT-S10 (0.7777) |  |
| AILIT-S03 | Human-centred mindset | 0.865 | 0.7764 | 1.114 | AILIT-S10 (0.8484) |  |
| AILIT-S04 | Ethics of AI | 0.7544 | 0.6513 | 1.158 | AILIT-S01 (0.7418) |  |
| AILIT-S05 | Ethics of AI | 0.7624 | 0.7035 | 1.084 | AILIT-S01 (0.7701) | borderline |
| AILIT-S06 | Ethics of AI | 0.7569 | 0.7273 | 1.041 | AILIT-S10 (0.7702) | borderline |
| AILIT-S07 | AI techniques and applications | 0.8836 | 0.7206 | 1.226 | AILIT-S12 (0.8423) |  |
| AILIT-S08 | AI techniques and applications | 0.8953 | 0.7592 | 1.179 | AILIT-S12 (0.8861) |  |
| AILIT-S09 | AI techniques and applications | 0.8902 | 0.7968 | 1.117 | AILIT-S12 (0.9039) |  |
| AILIT-S10 | AI system design | 0.8171 | 0.7911 | 1.033 | AILIT-S09 (0.8592) | borderline |
| AILIT-S11 | AI system design | 0.8075 | 0.7155 | 1.128 | AILIT-S08 (0.8645) |  |
| AILIT-S12 | AI system design | 0.837 | 0.7837 | 1.068 | AILIT-S09 (0.9039) | borderline |

## Per-anchor cohesion (UNESCO teacher aspects)

| Anchor | Group | within | between | ratio | worst cross-group match | flag |
|---|---|---:|---:|---:|---|---|
| AILIT-T01 | Human-centred mindset | nan | 0.6562 | nan | AILIT-T04 (0.7489) |  |
| AILIT-T02 | Ethics of AI | nan | 0.6016 | nan | AILIT-T04 (0.6467) |  |
| AILIT-T03 | AI foundations and applications | nan | 0.6549 | nan | AILIT-T04 (0.703) |  |
| AILIT-T04 | AI pedagogy | nan | 0.7319 | nan | AILIT-T05 (0.8291) |  |
| AILIT-T05 | AI for professional development | nan | 0.6721 | nan | AILIT-T04 (0.8291) |  |

## Per-anchor cohesion (OECD/EC domains)

| Anchor | Group | within | between | ratio | worst cross-group match | flag |
|---|---|---:|---:|---:|---|---|
| AILIT-O01 | Engaging with AI | nan | 0.7213 | nan | AILIT-O04 (0.7422) |  |
| AILIT-O02 | Creating with AI | nan | 0.7134 | nan | AILIT-O04 (0.7318) |  |
| AILIT-O03 | Managing AI | nan | 0.7199 | nan | AILIT-O01 (0.7305) |  |
| AILIT-O04 | Designing AI | nan | 0.7286 | nan | AILIT-O01 (0.7422) |  |

## Summary

- **Cohesive** (ratio ≥ 1.10): 8
- **Borderline** (1.00 ≤ ratio < 1.10): 4 → AILIT-S05, AILIT-S06, AILIT-S10, AILIT-S12
- **Over-recruiting** (ratio < 1.00): 0 → none

## Action

If any UNESCO student anchor is OVER_RECRUIT, that anchor needs rewording or splitting before Sprint 1. Inflated A2 (Ethics) share in the §10.1 verdict is the most likely artefact.