# Temporal cohort split (pre/post UNESCO 2024-09) — Module 5

Source: `sprint1_alignment_full_v1.jsonl` (v1). Cohort assigned per `data/corpus_inventory/sprint1_urls.csv` `unesco_cohort` column. Country-level matrices built separately for each cohort; Hellinger clustering with K = 2 reference centroids (KR + IE vs canonical, with `--min-aligned 50` filter).

## Per-country pre vs post cohort cluster

| iso | pre n | pre cluster | post n | post cluster | full cluster | note |
|---|---:|---:|---:|---:|---:|---|
| AE | 2 | - | 5 | - | 2 | pre n=2<50; post n=5<50 |
| AU | 38 | - | 6 | - | 2 | pre n=38<50; post n=6<50 |
| BR | 564 | 2 | 150 | 2 | 2 | agree |
| CA | 31 | - | 44 | - | 2 | pre n=31<50; post n=44<50 |
| CN | 390 | 2 | 0 | - | 2 | post n=0<50 |
| DE | 518 | 2 | 173 | 1 | 2 | DISAGREE |
| EE | 3 | - | 64 | 2 | 2 | pre n=3<50 |
| ES | 65 | 2 | 147 | 2 | 2 | agree |
| FI | 1644 | 2 | 35 | - | 2 | post n=35<50 |
| FR | 274 | 2 | 1372 | 2 | 2 | agree |
| GB | 687 | 2 | 8 | - | 2 | post n=8<50 |
| IE | 854 | 1 | 458 | 1 | 1 | agree |
| IL | 120 | 2 | 895 | 2 | 2 | agree |
| IN | 1763 | 2 | 0 | - | 2 | post n=0<50 |
| IT | 0 | - | 1080 | 2 | 2 | pre n=0<50 |
| JP | 544 | 2 | 225 | 2 | 2 | agree |
| KR | 3168 | 1 | 275 | 1 | 1 | agree |
| MX | 1311 | 2 | 0 | - | 2 | post n=0<50 |
| NL | 952 | 2 | 0 | - | 2 | post n=0<50 |
| NO | 1031 | 2 | 7 | - | 2 | post n=7<50 |
| SA | 248 | 2 | 0 | - | 2 | post n=0<50 |
| SE | 388 | 2 | 0 | - | 2 | post n=0<50 |
| SG | 489 | 2 | 13 | - | 2 | post n=13<50 |
| US | 1614 | 2 | 1628 | 1 | 2 | DISAGREE |
| ZA | 0 | - | 1362 | 2 | 2 | pre n=0<50 |

## Summary

- KR pre-cohort = Cluster 1, post-cohort = Cluster 1
- IE pre-cohort = Cluster 1, post-cohort = Cluster 1
- 7/9 countries with ≥ 50 sentences in both cohorts preserve their cluster assignment across the temporal split.

## Interpretation

If KR and IE preserve Cluster 1 in *both* the pre and post sub-corpora, the K = 2 partition is not a timing artefact. Countries whose policy texts predate UNESCO 2024-09 cannot reference the framework's vocabulary, so any signal that survives the pre cohort comes from independent national choices — and likewise for the post cohort. Agreement in both directions is the test we want.