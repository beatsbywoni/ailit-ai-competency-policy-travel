# Uniform-cap N = 500 sub-sampling — Phase 2 robustness module 4

Source: `sprint1_alignment_full_v2.jsonl` (v2). Resampling: every country capped at N = 500 aligned sentences per iteration; 1000 iterations; seed = 20260530.

## Per-country Cluster-1 assignment rate

| iso | n (full) | Cluster-1 rate | Full-data cluster | Top dominant aspect | Rate |
|---|---:|---:|---:|---|---:|
| AE | 7 | 0.0 % | 2 | A1 HCM | 100.0 % |
| AU | 42 | 0.0 % | 2 | A1 HCM | 100.0 % |
| BR | 694 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| CA | 75 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| CN | 387 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| DE | 684 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| EE | 66 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| ES | 210 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| FI | 1656 | 0.0 % | 2 | A2 Ethics | 91.8 % |
| FR | 1626 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| GB | 687 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IE | 1290 | 100.0 % | 1 | A1 HCM | 99.4 % |
| IL | 996 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IN | 1718 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IT | 1066 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| JP | 751 | 0.0 % | 2 | A4 SysDes | 72.8 % |
| KR | 3297 | 100.0 % | 1 | A3 Tech | 100.0 % |
| MX | 1253 | 0.0 % | 2 | A1 HCM | 100.0 % |
| NL | 934 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| NO | 974 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| SA | 234 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| SE | 385 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| SG | 493 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| US | 3211 | 0.1 % | 2 | A1 HCM | 83.4 % |
| ZA | 1334 | 0.0 % | 2 | A1 HCM | 99.7 % |

## Partition stability

- Full-data K = 2 partition matched in **999/1000 (99.9 %)** of uniform-cap resamples.
- KR stays in Cluster 1: **100.0 %** of iterations.
- IE stays in Cluster 1: **100.0 %** of iterations.

## Interpretation

Uniform-cap is the most aggressive size-equalisation in the IV battery (more so than IV.2 inverse weighting and IV.3 LOO combined). If KR maintains Cluster 1 assignment under uniform cap, the Tool-use deviating signature is *not* an artefact of corpus size. The IE assignment rate quantifies how borderline IE actually is — under aggressive resampling, the IE-01 single-document dependency may push IE's Cluster-1 rate down below KR's.