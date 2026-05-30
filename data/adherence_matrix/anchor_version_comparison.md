# Anchor v1 vs v2 — side-by-side comparison

Sprint 0.5 Path A verification. Generated from `data/validation/anchor_cohesion_v{1,2}.csv` and `data/adherence_matrix/pilot_5x12_pct_v{1,2}.csv`.

## Cohesion change (UNESCO student anchors)

| Anchor | Aspect | v1 ratio | v2 ratio | Δ | v2 flag |
|---|---|---:|---:|---:|---|
| AILIT-S01 | A1 HCM | 1.148 | 1.177 | +0.029 | ✓ |
| AILIT-S02 | A1 HCM | 1.188 | 1.217 | +0.029 | ✓ |
| AILIT-S03 | A1 HCM | 1.076 | 1.114 | +0.038 | ✓ |
| AILIT-S04 | A2 Ethics | 0.974 | 1.158 | +0.184 | ✓ |
| AILIT-S05 | A2 Ethics | 1.021 | 1.084 | +0.063 | borderline |
| AILIT-S06 | A2 Ethics | 0.972 | 1.041 | +0.069 | borderline |
| AILIT-S07 | A3 Tech | 1.198 | 1.226 | +0.028 | ✓ |
| AILIT-S08 | A3 Tech | 1.147 | 1.179 | +0.032 | ✓ |
| AILIT-S09 | A3 Tech | 1.100 | 1.117 | +0.017 | ✓ |
| AILIT-S10 | A4 SysDes | 1.011 | 1.033 | +0.022 | borderline |
| AILIT-S11 | A4 SysDes | 1.113 | 1.128 | +0.015 | ✓ |
| AILIT-S12 | A4 SysDes | 1.051 | 1.068 | +0.017 | borderline |

## Per-country bifurcation — dominant aspect v1 vs v2

| Country | v1 dominant | v1 % | v2 dominant | v2 % | T÷E v1 | T÷E v2 |
|---|---|---:|---|---:|---:|---:|
| FI | A2 Ethics | 31.6 | A2 Ethics | 28.7 | 0.73 | 0.85 |
| GB | A4 SysDes | 41.1 | A4 SysDes | 44.9 | 0.47 | 0.83 |
| KR | A3 Tech | 37.6 | A3 Tech | 42.8 | 1.14 | 4.30 |
| SG | A4 SysDes | 39.2 | A4 SysDes | 40.7 | 0.63 | 0.96 |
| US | A2 Ethics | 27.2 | A1 HCM ⚠ FLIP | 32.5 | 0.74 | 1.22 |

## Verdict

PARTIAL — Path A succeeded for some but not all Ethics anchors. Enter Sprint 1 with v2 anchors active; report borderline anchors in §4.6 robustness.

- S04/S05/S06 cohesion-pass count (ratio ≥ 1.10): **1 / 3**
- S04/S05/S06 still OVER_RECRUIT (ratio < 1.00): **0 / 3**
- Country dominant-aspect flips between v1 and v2: **1 / 5**

Interpretation:
- 0 cluster flips → 3-cluster bifurcation is robust to anchor revision (manuscript §4.6 robustness).
- 1–2 flips → noteworthy but acceptable; describe which countries flip and why (likely anchor-cohesion-driven).
- 3+ flips → unstable; reconsider both anchor wording AND cluster interpretation.