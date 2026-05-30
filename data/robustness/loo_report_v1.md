# Leave-one-out per country — Phase 2 robustness module 2

Source: `sprint1_alignment_full_v1.jsonl`. For each country with ≥ 2 documents, drop the largest single document and reassign to either Cluster 1 ({KR, IE}) or Cluster 2 (canonical) by closest Hellinger-centroid.

## Per-country table

| iso | drop_doc | drop_n | kept_n | orig_dom | loo_dom | orig_cluster | loo_cluster | flipped |
|---|---|---:|---:|---|---|---:|---:|---|
| AE | AE-02 | 5 | 2 | A2 Ethics | A2 Ethics | 2 | 2 | no |
| AU | AU-01 | 35 | 9 | A1 HCM | A4 SysDes | 2 | 1 | Y |
| BR | BR-03 | 564 | 150 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| CA | CA-02 | 44 | 31 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| CN | CN-01 | 389 | 1 | A4 SysDes | A2 Ethics | 2 | 1 | Y |
| DE | DE-01 | 502 | 189 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| EE | EE-02 | 64 | 3 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| ES | ES-02 | 147 | 65 | A4 SysDes | A1 HCM | 2 | 2 | no |
| FI | FI-01 | 1644 | 35 | A2 Ethics | A2 Ethics | 2 | 1 | Y |
| FR | FR-03 | 1210 | 436 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| GB | GB-02_full | 572 | 123 | A4 SysDes | A2 Ethics | 2 | 2 | no |
| IE | IE-01 | 854 | 458 | A1 HCM | A2 Ethics | 1 | 2 | Y |
| IL | IL-01 | 895 | 120 | A4 SysDes | A2 Ethics | 2 | 2 | no |
| IN | IN-01 | 1153 | 610 | A4 SysDes | A2 Ethics | 2 | 2 | no |
| IT | IT-02 | 574 | 506 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| JP | JP-01 | 544 | 225 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| KR | KR-02 | 3072 | 371 | A3 Tech | A3 Tech | 1 | 1 | no |
| MX | MX-01 | 1256 | 55 | A2 Ethics | A2 Ethics | 2 | 2 | no |
| NL | NL-01 | 948 | 4 | A4 SysDes | A1 HCM | 2 | 1 | Y |
| NO | NO-01 | 1031 | 7 | A2 Ethics | A4 SysDes | 2 | 2 | no |
| SA | SA-01 | 216 | 32 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| SE | SE-02 | 261 | 127 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| SG | SG-01 | 482 | 20 | A4 SysDes | A1 HCM | 2 | 1 | Y |
| US | US-04 | 1582 | 1660 | A2 Ethics | A4 SysDes | 2 | 2 | no |
| ZA | ZA-01 | 1249 | 113 | A2 Ethics | A4 SysDes | 2 | 2 | no |

## Interpretation

- 6 / 25 countries flipped cluster assignment after LOO.
- KR LOO outcome: preserved in Cluster 1
- IE LOO outcome: lost Cluster 1

If KR and IE preserve Cluster 1 *and* no canonical country joins, the K=2 partition is robust to single-document dominance — the main empirical claim of the manuscript stands.