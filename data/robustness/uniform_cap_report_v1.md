# Uniform-cap N = 500 sub-sampling — Phase 2 robustness module 4

Source: `sprint1_alignment_full_v1.jsonl` (v1). Resampling: every country capped at N = 500 aligned sentences per iteration; 1000 iterations; seed = 20260530.

## Per-country Cluster-1 assignment rate

| iso | n (full) | Cluster-1 rate | Full-data cluster | Top dominant aspect | Rate |
|---|---:|---:|---:|---|---:|
| AE | 7 | 4.1 % | 2 | A2 Ethics | 100.0 % |
| AU | 44 | 0.0 % | 2 | A1 HCM | 100.0 % |
| BR | 714 | 0.0 % | 2 | A4 SysDes | 86.9 % |
| CA | 75 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| CN | 390 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| DE | 691 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| EE | 67 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| ES | 212 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| FI | 1679 | 0.0 % | 2 | A2 Ethics | 99.7 % |
| FR | 1646 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| GB | 695 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IE | 1312 | 100.0 % | 1 | A1 HCM | 79.5 % |
| IL | 1015 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IN | 1763 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| IT | 1080 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| JP | 769 | 0.0 % | 2 | A4 SysDes | 98.2 % |
| KR | 3443 | 100.0 % | 1 | A3 Tech | 91.5 % |
| MX | 1311 | 0.0 % | 2 | A2 Ethics | 100.0 % |
| NL | 952 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| NO | 1038 | 0.0 % | 2 | A2 Ethics | 96.4 % |
| SA | 248 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| SE | 388 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| SG | 502 | 0.0 % | 2 | A4 SysDes | 100.0 % |
| US | 3242 | 0.0 % | 2 | A2 Ethics | 46.7 % |
| ZA | 1362 | 0.0 % | 2 | A2 Ethics | 99.4 % |

## Partition stability

- Full-data K = 2 partition matched in **959/1000 (95.9 %)** of uniform-cap resamples.
- KR stays in Cluster 1: **100.0 %** of iterations.
- IE stays in Cluster 1: **100.0 %** of iterations.

## Interpretation

Uniform-cap is the most aggressive size-equalisation in the IV battery (more so than IV.2 inverse weighting and IV.3 LOO combined). If KR maintains Cluster 1 assignment under uniform cap, the Tool-use deviating signature is *not* an artefact of corpus size. The IE assignment rate quantifies how borderline IE actually is — under aggressive resampling, the IE-01 single-document dependency may push IE's Cluster-1 rate down below KR's.