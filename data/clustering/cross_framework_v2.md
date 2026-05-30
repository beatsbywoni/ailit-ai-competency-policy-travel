# Cross-framework cluster identity — Phase 3 §4.5

Source matrices: `sprint1_25x12_pct_v2.csv` (student 12), `sprint1_25x5_pct_teacher.csv` (teacher 5), `sprint1_25x4_pct_oecd.csv` (OECD 4). Each country is assigned to cluster 1 (closer to KR + IE centroid) or 2 (closer to canonical centroid) by Hellinger distance, with `--min-aligned 50` filter (0 = excluded).

## Per-country cluster across frameworks

| iso | student | teacher | oecd | rep_score | note |
|---|:-:|:-:|:-:|:-:|---|
| KR | 1 | 1 | 1 | 3 | anchor of cluster |
| GB | 2 | 2 | 2 | 0 |  |
| SG | 2 | 2 | 2 | 0 |  |
| FI | 2 | 2 | 1 | 1 |  |
| US | 2 | 1 | 1 | 2 | REPLICATES deviating signature |
| CN | 2 | 2 | 2 | 0 |  |
| JP | 2 | 2 | 2 | 0 |  |
| DE | 2 | 2 | 1 | 1 |  |
| FR | 2 | 2 | 2 | 0 |  |
| CA | 2 | 2 | 1 | 1 |  |
| AU | 0 | 0 | 0 | 0 | all small-n |
| IL | 2 | 2 | 2 | 0 |  |
| IN | 2 | 2 | 2 | 0 |  |
| EE | 2 | 0 | 2 | 0 |  |
| NO | 2 | 2 | 1 | 1 |  |
| SE | 2 | 2 | 1 | 1 |  |
| NL | 2 | 2 | 2 | 0 |  |
| IE | 1 | 1 | 1 | 3 | anchor of cluster |
| ES | 2 | 2 | 2 | 0 |  |
| IT | 2 | 2 | 2 | 0 |  |
| AE | 0 | 0 | 0 | 0 | all small-n |
| SA | 2 | 2 | 2 | 0 |  |
| BR | 2 | 2 | 2 | 0 |  |
| MX | 2 | 2 | 2 | 0 |  |
| ZA | 2 | 2 | 2 | 0 |  |

## Framework-pair agreement (n = 23 eligible countries)

| pair | agreement |
|---|---:|
| student ↔ teacher | 21/23 (91 %) |
| student ↔ oecd | 17/23 (74 %) |
| teacher ↔ oecd | 17/23 (74 %) |

## Interpretation

- KR and IE were defined as Cluster 1 in the student analysis (§4.5.1). The question for §4.5.2-3 is whether they remain in Cluster 1 (the {KR, IE} centroid) when teacher / OECD frameworks are substituted.
- A country with `rep_score = 3` is in the deviating cluster across all three frameworks. A country with `rep_score = 2` replicates in two of three. The deviating signature is *framework-replicable* for the country.
- If agreement between framework pairs is high (≥ 70 %), the cluster partition is largely framework-invariant. Lower agreement indicates framework-specific structure — interesting in its own right, but weakens the §4.5 main claim.