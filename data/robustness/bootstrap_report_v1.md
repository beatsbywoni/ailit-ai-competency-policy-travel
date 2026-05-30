# Bootstrap 95 % CI — focal anchor AILIT-S08, n_boot = 1000

Source: `sprint1_alignment_full_v1.jsonl`. Resampling unit = aligned sentence; iteration count = 1000; seed = 20260530.

## Per-country focal-anchor share

| iso | n | mean % | 95 % CI |
|---|---:|---:|---|
| AE | 7 | 0.0 | [0.0, 0.0] |
| AU | 44 | 0.0 | [0.0, 0.0] |
| BR | 714 | 0.98 | [0.28, 1.82] |
| CA | 75 | 2.67 | [0.0, 6.67] |
| CN | 390 | 1.79 | [0.51, 3.08] |
| DE | 691 | 2.75 | [1.59, 4.05] |
| EE | 67 | 0.0 | [0.0, 0.0] |
| ES | 212 | 0.0 | [0.0, 0.0] |
| FI | 1679 | 9.41 | [8.04, 10.9] |
| FR | 1646 | 1.52 | [0.97, 2.13] |
| GB | 695 | 2.59 | [1.58, 3.88] |
| IE | 1312 | 22.26 | [20.05, 24.39] |
| IL | 1015 | 3.05 | [2.07, 4.14] |
| IN | 1763 | 2.5 | [1.82, 3.23] |
| IT | 1080 | 1.85 | [1.11, 2.69] |
| JP | 769 | 3.64 | [2.34, 5.07] |
| KR | 3443 | 26.84 | [25.33, 28.41] |
| MX | 1311 | 3.2 | [2.29, 4.27] |
| NL | 952 | 2.84 | [1.89, 3.99] |
| NO | 1038 | 4.14 | [2.99, 5.49] |
| SA | 248 | 2.02 | [0.4, 4.03] |
| SE | 388 | 2.06 | [0.77, 3.61] |
| SG | 502 | 1.39 | [0.4, 2.39] |
| US | 3242 | 8.67 | [7.68, 9.65] |
| ZA | 1362 | 1.69 | [1.03, 2.42] |

## Effect sizes

| contrast | point % | 95 % CI | note |
|---|---:|---|---|
| canonical_mean | 2.81 | [2.53, 3.11] | mean across 21 canonical countries |
| IE − canonical_mean | 19.42 | [17.16, 21.59] | effect size for the Cluster-1 deviation |
| KR − canonical_mean | 24.02 | [22.52, 25.6] | effect size for the Cluster-1 deviation |
| IE-01 − IE-02 (intra-IE asymmetry) | 21.11 | [17.17, 24.96] | n_IE-01=854, n_IE-02=458 |

## Interpretation

- If the *contrast* row "KR − canonical_mean" has a 95 % CI that does NOT include zero, KR's Tool-use deviation is statistically distinguishable from the canonical signature at this resolution.
- Similarly for IE.
- The "IE-01 − IE-02" row quantifies the intra-IE asymmetry: if the CI excludes zero, the §4.5 LOO finding (IE-01 carries the tool-use signal) is supported by bootstrap inference, not just by point estimates.