# Discriminant validity — module 6 (v2 anchors, θ = 0.35)

Construct-validity test: alignment rate (% of sentences crossing the θ = 0.35 cosine threshold to at least one UNESCO student anchor) on three corpora.

## Aggregate result

| corpus | n_total | n_aligned | rate % |
|---|---:|---:|---:|
| positive | 36098 | 24070 | 66.7 |
| hard-neg | 328 | 226 | 68.9 |
| off-domain | 3271 | 1 | 0.0 |

## Per-document detail

| corpus | doc_id | n_sents | n_aligned | rate % |
|---|---|---:|---:|---:|
| positive | AE-01 | 3 | 2 | 66.67 |
| positive | AE-02 | 6 | 5 | 83.33 |
| positive | AU-01 | 44 | 33 | 75.0 |
| positive | AU-02 | 6 | 6 | 100.0 |
| positive | AU-03 | 4 | 3 | 75.0 |
| positive | BR-01 | 2 | 0 | 0.0 |
| positive | BR-02 | 254 | 139 | 54.72 |
| positive | BR-03 | 897 | 555 | 61.87 |
| positive | CA-01 | 20 | 15 | 75.0 |
| positive | CA-02 | 47 | 44 | 93.62 |
| positive | CA-03 | 17 | 16 | 94.12 |
| positive | CN-01 | 469 | 386 | 82.3 |
| positive | CN-02 | 4 | 1 | 25.0 |
| positive | CN-03 | 0 | 0 | 0.0 |
| positive | DE-01 | 623 | 496 | 79.61 |
| positive | DE-02 | 19 | 16 | 84.21 |
| positive | DE-03 | 198 | 172 | 86.87 |
| positive | EE-01 | 3 | 3 | 100.0 |
| positive | EE-02 | 85 | 63 | 74.12 |
| positive | ES-01 | 332 | 65 | 19.58 |
| positive | ES-02 | 201 | 145 | 72.14 |
| positive | FI-01 | 2944 | 1622 | 55.1 |
| positive | FI-02 | 6 | 4 | 66.67 |
| positive | FI-03 | 12 | 12 | 100.0 |
| positive | FI-04 | 21 | 18 | 85.71 |
| positive | FR-01 | 385 | 272 | 70.65 |
| positive | FR-02 | 181 | 162 | 89.5 |
| positive | FR-03 | 1791 | 1192 | 66.55 |
| positive | GB-01_full | 125 | 114 | 91.2 |
| positive | GB-02_full | 688 | 565 | 82.12 |
| positive | GB-03 | 3 | 3 | 100.0 |
| positive | GB-04_full | 5 | 5 | 100.0 |
| positive | IE-01 | 1032 | 840 | 81.4 |
| positive | IE-02 | 511 | 450 | 88.06 |
| positive | IL-01 | 1196 | 877 | 73.33 |
| positive | IL-02 | 144 | 119 | 82.64 |
| positive | IN-01 | 1826 | 1135 | 62.16 |
| positive | IN-02 | 1183 | 497 | 42.01 |
| positive | IN-03 | 120 | 86 | 71.67 |
| positive | IT-01 | 658 | 500 | 75.99 |
| positive | IT-02 | 745 | 566 | 75.97 |
| positive | JP-01 | 1047 | 528 | 50.43 |
| positive | JP-02 | 271 | 196 | 72.32 |
| positive | JP-03 | 31 | 27 | 87.1 |
| positive | KR-01 | 122 | 93 | 76.23 |
| positive | KR-02 | 4041 | 2930 | 72.51 |
| positive | KR-03 | 124 | 104 | 83.87 |
| positive | KR-04 | 131 | 117 | 89.31 |
| positive | KR-05 | 76 | 53 | 69.74 |
| positive | MX-01 | 2177 | 1198 | 55.03 |
| positive | MX-02 | 74 | 55 | 74.32 |
| positive | NL-01 | 1360 | 930 | 68.38 |
| positive | NL-02 | 4 | 4 | 100.0 |
| positive | NO-01 | 1844 | 967 | 52.44 |
| positive | NO-02 | 10 | 7 | 70.0 |
| positive | SA-01 | 298 | 202 | 67.79 |
| positive | SA-02 | 35 | 32 | 91.43 |
| positive | SE-01 | 156 | 126 | 80.77 |
| positive | SE-02 | 325 | 259 | 79.69 |
| positive | SG-01 | 749 | 473 | 63.15 |
| positive | SG-02 | 8 | 7 | 87.5 |
| positive | SG-03 | 14 | 13 | 92.86 |
| positive | US-01 | 438 | 267 | 60.96 |
| positive | US-02 | 1653 | 1349 | 81.61 |
| positive | US-03 | 56 | 46 | 82.14 |
| positive | US-04 | 2085 | 1549 | 74.29 |
| positive | ZA-01 | 1934 | 1225 | 63.34 |
| positive | ZA-02 | 225 | 109 | 48.44 |
| hard-neg | HARD-02 | 2 | 1 | 50.0 |
| hard-neg | HARD-03 | 23 | 22 | 95.65 |
| hard-neg | HARD-04 | 303 | 203 | 67.0 |
| off-domain | OFF-01 | 2071 | 1 | 0.05 |
| off-domain | OFF-02 | 709 | 0 | 0.0 |
| off-domain | OFF-03 | 491 | 0 | 0.0 |

## Interpretation

- Positive (25-country education-policy corpus) alignment rate: **66.7 %**
- Off-domain negative (fiction + Wikipedia non-AI) alignment rate: **0.0 %**
- Hard-negative (AI policy in health/defence/corporate domains) alignment rate: **68.9 %**

Expected pattern: positive ≫ hard-negative ≫ off-domain.

If both negative rates are substantially below the positive rate (e.g. > 20 pp gap), the 12 UNESCO student anchors are measuring something *specific* to AI-in-education policy text — not a generic 'is this English-language formal prose' signal. This is the C&E I.4 (off-domain discriminant) + I.5 (hard-negative discriminant) checklist requirement.

If the gap is small (< 10 pp), the anchors are over-general and §3.3 (anchor cohesion) needs further sharpening — and the manuscript's construct-validity claim collapses.