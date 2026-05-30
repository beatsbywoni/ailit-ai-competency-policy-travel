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
| AILIT-S01 | Human-centred mindset | 0.8889 | 0.7743 | 1.148 | AILIT-S04 (0.8453) |  |
| AILIT-S02 | Human-centred mindset | 0.8759 | 0.737 | 1.188 | AILIT-S06 (0.7869) |  |
| AILIT-S03 | Human-centred mindset | 0.865 | 0.8038 | 1.076 | AILIT-S04 (0.879) | borderline |
| AILIT-S04 | Ethics of AI | 0.7444 | 0.7646 | 0.974 | AILIT-S03 (0.879) | OVER_RECRUIT |
| AILIT-S05 | Ethics of AI | 0.7208 | 0.7057 | 1.021 | AILIT-S01 (0.7768) | borderline |
| AILIT-S06 | Ethics of AI | 0.7451 | 0.7666 | 0.972 | AILIT-S03 (0.8379) | OVER_RECRUIT |
| AILIT-S07 | AI techniques and applications | 0.8836 | 0.7376 | 1.198 | AILIT-S12 (0.8423) |  |
| AILIT-S08 | AI techniques and applications | 0.8953 | 0.7804 | 1.147 | AILIT-S12 (0.8861) |  |
| AILIT-S09 | AI techniques and applications | 0.8902 | 0.8096 | 1.1 | AILIT-S12 (0.9039) | borderline |
| AILIT-S10 | AI system design | 0.8171 | 0.8085 | 1.011 | AILIT-S09 (0.8592) | borderline |
| AILIT-S11 | AI system design | 0.8075 | 0.7256 | 1.113 | AILIT-S08 (0.8645) |  |
| AILIT-S12 | AI system design | 0.837 | 0.7963 | 1.051 | AILIT-S09 (0.9039) | borderline |

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

- **Cohesive** (ratio ≥ 1.10): 6
- **Borderline** (1.00 ≤ ratio < 1.10): 5 → AILIT-S03, AILIT-S05, AILIT-S09, AILIT-S10, AILIT-S12
- **Over-recruiting** (ratio < 1.00): 2 → AILIT-S04, AILIT-S06

## Action

If any UNESCO student anchor is OVER_RECRUIT, that anchor needs rewording or splitting before Sprint 1. Inflated A2 (Ethics) share in the §10.1 verdict is the most likely artefact.