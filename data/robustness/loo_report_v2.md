# Leave-one-out per country — Phase 2 robustness module 2

Source: `sprint1_alignment_full_v2.jsonl`. For each country with ≥ 2 documents, drop the largest single document and reassign to either Cluster 1 ({KR, IE}) or Cluster 2 (canonical) by closest Hellinger-centroid.

## Per-country table

| iso | drop_doc | drop_n | kept_n | orig_dom | loo_dom | orig_cluster | loo_cluster | flipped |
|---|---|---:|---:|---|---|---:|---:|---|
| AE | AE-02 | 5 | 2 | A1 HCM | A1 HCM | 2 | 1 | Y |
| AU | AU-01 | 33 | 9 | A1 HCM | A4 SysDes | 2 | 1 | Y |
| BR | BR-03 | 555 | 139 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| CA | CA-02 | 44 | 31 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| CN | CN-01 | 386 | 1 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| DE | DE-01 | 496 | 188 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| EE | EE-02 | 63 | 3 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| ES | ES-02 | 145 | 65 | A4 SysDes | A1 HCM | 2 | 2 | no |
| FI | FI-01 | 1622 | 34 | A2 Ethics | A3 Tech | 2 | 1 | Y |
| FR | FR-03 | 1192 | 434 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| GB | GB-02_full | 565 | 122 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| IE | IE-01 | 840 | 450 | A1 HCM | A1 HCM | 1 | 2 | Y |
| IL | IL-01 | 877 | 119 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| IN | IN-01 | 1135 | 583 | A4 SysDes | A2 Ethics | 2 | 2 | no |
| IT | IT-02 | 566 | 500 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| JP | JP-01 | 528 | 223 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| KR | KR-02 | 2930 | 367 | A3 Tech | A3 Tech | 1 | 1 | no |
| MX | MX-01 | 1198 | 55 | A1 HCM | A2 Ethics | 2 | 2 | no |
| NL | NL-01 | 930 | 4 | A4 SysDes | A1 HCM | 2 | 1 | Y |
| NO | NO-01 | 967 | 7 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| SA | SA-01 | 202 | 32 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| SE | SE-02 | 259 | 126 | A4 SysDes | A4 SysDes | 2 | 2 | no |
| SG | SG-01 | 473 | 20 | A4 SysDes | A1 HCM | 2 | 1 | Y |
| US | US-04 | 1549 | 1662 | A1 HCM | A4 SysDes | 2 | 2 | no |
| ZA | ZA-01 | 1225 | 109 | A1 HCM | A4 SysDes | 2 | 2 | no |

## Interpretation

- 6 / 25 countries flipped cluster assignment after LOO.
- KR LOO outcome: preserved in Cluster 1
- IE LOO outcome: lost Cluster 1

If KR and IE preserve Cluster 1 *and* no canonical country joins, the K=2 partition is robust to single-document dominance — the main empirical claim of the manuscript stands.