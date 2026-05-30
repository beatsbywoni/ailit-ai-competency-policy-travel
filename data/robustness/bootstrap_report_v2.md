# Bootstrap 95 % CI — focal anchor AILIT-S08, n_boot = 1000

Source: `sprint1_alignment_full_v2.jsonl`. Resampling unit = aligned sentence; iteration count = 1000; seed = 20260530.

## Per-country focal-anchor share

| iso | n | mean % | 95 % CI |
|---|---:|---:|---|
| AE | 7 | 0.0 | [0.0, 0.0] |
| AU | 42 | 0.0 | [0.0, 0.0] |
| BR | 694 | 1.15 | [0.43, 2.02] |
| CA | 75 | 2.67 | [0.0, 6.67] |
| CN | 387 | 1.81 | [0.52, 3.36] |
| DE | 684 | 2.78 | [1.61, 4.09] |
| EE | 66 | 0.0 | [0.0, 0.0] |
| ES | 210 | 0.0 | [0.0, 0.0] |
| FI | 1656 | 10.08 | [8.63, 11.47] |
| FR | 1626 | 1.54 | [0.98, 2.15] |
| GB | 687 | 2.91 | [1.75, 4.22] |
| IE | 1290 | 23.33 | [21.16, 25.74] |
| IL | 996 | 3.21 | [2.11, 4.32] |
| IN | 1718 | 2.91 | [2.15, 3.73] |
| IT | 1066 | 1.88 | [1.13, 2.72] |
| JP | 751 | 3.86 | [2.53, 5.2] |
| KR | 3297 | 30.24 | [28.6, 31.85] |
| MX | 1253 | 3.75 | [2.71, 4.87] |
| NL | 934 | 3.0 | [1.93, 4.07] |
| NO | 974 | 4.93 | [3.59, 6.37] |
| SA | 234 | 2.14 | [0.43, 4.27] |
| SE | 385 | 2.08 | [0.78, 3.64] |
| SG | 493 | 2.03 | [0.81, 3.25] |
| US | 3211 | 9.37 | [8.35, 10.43] |
| ZA | 1334 | 1.95 | [1.2, 2.7] |

## Effect sizes

| contrast | point % | 95 % CI | note |
|---|---:|---|---|
| canonical_mean | 3.05 | [2.78, 3.37] | mean across 21 canonical countries |
| IE − canonical_mean | 20.33 | [18.04, 22.74] | effect size for the Cluster-1 deviation |
| KR − canonical_mean | 27.19 | [25.53, 28.89] | effect size for the Cluster-1 deviation |
| IE-01 − IE-02 (intra-IE asymmetry) | 21.16 | [17.24, 25.32] | n_IE-01=840, n_IE-02=450 |

## Interpretation

- If the *contrast* row "KR − canonical_mean" has a 95 % CI that does NOT include zero, KR's Tool-use deviation is statistically distinguishable from the canonical signature at this resolution.
- Similarly for IE.
- The "IE-01 − IE-02" row quantifies the intra-IE asymmetry: if the CI excludes zero, the §4.5 LOO finding (IE-01 carries the tool-use signal) is supported by bootstrap inference, not just by point estimates.