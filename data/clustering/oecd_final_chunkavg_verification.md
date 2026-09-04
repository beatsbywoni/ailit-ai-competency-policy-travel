# OECD–EC final-framework re-run — verification report [oecd_final_chunkavg]
eligibility floor: n_aligned >= 50

## A2 — alignment totals (all 25 countries)
draft : 18,872 aligned sentences
final : 22,386 aligned sentences

eligible under both (n >= 50): 23 countries — excluded: AU(draft n=32, final n=42), AE(draft n=6, final n=6)

## A2 — Table 3 (per-domain adherence share, %, across eligible countries)
| domain | draft mean | draft SD | draft range | final mean | final SD | final range |
|---|---|---|---|---|---|---|
| AILIT-O01 → AILIT-O01F | 25.2 | 6.1 | 14.5–36.8 (IT–SE) | 18.7 | 9.3 | 5.5–50.9 (CA–EE) |
| AILIT-O02 → AILIT-O02F | 14.7 | 5.7 | 3.0–23.2 (IE–IN) | 6.1 | 3.9 | 0.0–16.1 (EE–FI) |
| AILIT-O03 → AILIT-O03F | 31.6 | 13.2 | 8.2–56.6 (IE–EE) | 14.0 | 5.0 | 4.9–25.4 (IE–BR) |
| AILIT-O04 → AILIT-O04F | 28.5 | 14.4 | 3.8–69.0 (EE–IE) | 61.2 | 11.7 | 31.6–82.7 (EE–IE) |
| sum of SDs (old row, for reference) | | 39.4 | | | 29.9 | |

Named values:
  KR: O4 draft 43.4% → final 62.8%   | O3 14.2 → 11.0 | O2 7.4 → 14.7 | O1 35.0 → 11.5
  US: O4 draft 54.7% → final 71.0%   | O3 16.3 → 16.0 | O2 4.7 → 4.5 | O1 24.2 → 8.6
  IE: O4 draft 69.0% → final 82.7%   | O3 8.2 → 4.9 | O2 3.0 → 2.3 | O1 19.8 → 10.1
  FR: O4 draft 22.7% → final 77.2%   | O3 34.1 → 7.5 | O2 14.5 → 3.1 | O1 28.8 → 12.1
  EE: O4 draft 3.8% → final 31.6%   | O3 56.6 → 17.5 | O2 9.4 → 0.0 | O1 30.2 → 50.9
  top final Shape-AI shares: IE 82.7%, FR 77.2%, CA 74.0%, DE 73.5%

## A2 — Hellinger matrix and silhouettes (final anchors)
on-disk Hellinger matrix: same country order = True; max |diff| vs recomputed = 5.00e-05
| linkage | K | silhouette | groups |
|---|---|---|---|
| ward | 2 | 0.5781 | BR,CA,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / EE |
| ward | 3 | 0.2843 | BR,FI,GB,IN,JP,KR,NL,SA,SG,ZA / CA,CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US / EE |
| ward | 4 | 0.2940 | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CA,CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US / EE |
| ward | 5 | 0.3039 | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CA,CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE / EE |
| ward | 6 | 0.2943 | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE / CA / EE |
| average | 2 | 0.5781 | BR,CA,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / EE |
| average | 3 | 0.3033 | BR,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / CA / EE |
| average | 4 | 0.2869 | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / DE,FR,IE / CA / EE |
| average | 5 | 0.1794 | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / DE,FR,IE / CA / EE / SA |
| average | 6 | 0.2245 | FI,KR,SG / BR,CN,ES,GB,IL,IN,IT,JP,MX,NL,NO,SE,US,ZA / DE,FR,IE / CA / EE / SA |

Draft anchors, same eligible set (reference):
  ward K=2 silhouette 0.4827  groups CA,FI,IE,KR,SE,US / BR,CN,DE,EE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SA,SG,ZA
  average K=2 silhouette 0.4827  groups CA,FI,IE,KR,SE,US / BR,CN,DE,EE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SA,SG,ZA

## A3.1 — Estonia excluded (final anchors)
| linkage | K | silhouette | KR&IE together in a minority group? | groups |
|---|---|---|---|---|
| ward | 2 | 0.2972 | no | BR,FI,GB,IN,JP,KR,NL,SA,SG,ZA / CA,CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US |
| ward | 3 | 0.3074 | no | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CA,CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US |
| ward | 4 | 0.3178 | no | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CA,CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE |
| ward | 5 | 0.3076 | no | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE / CA |
| ward | 6 | 0.3346 | no | FI,KR,SG / GB,IN,JP,SA / CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE / CA / BR,NL,ZA |
| average | 2 | 0.3206 | no | BR,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / CA |
| average | 3 | 0.3030 | no | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / DE,FR,IE / CA |
| average | 4 | 0.1875 | no | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / DE,FR,IE / CA / SA |
| average | 5 | 0.2347 | no | FI,KR,SG / BR,CN,ES,GB,IL,IN,IT,JP,MX,NL,NO,SE,US,ZA / DE,FR,IE / CA / SA |
| average | 6 | 0.2901 | no | FI,KR,SG / CN,ES,GB,IL,IN,IT,JP,MX,NO,SE,US / DE,FR,IE / CA / BR,NL,ZA / SA |
→ any K/linkage recovering a KR+IE minority group: False

## A3.2 — eligibility floor n >= 100 (final anchors)
eligible: 21 — dropped vs n>=50: ['CA', 'EE']
| linkage | K | silhouette | KR&IE together in a minority group? | groups |
|---|---|---|---|---|
| ward | 2 | 0.2982 | no | BR,FI,GB,IN,JP,KR,NL,SA,SG,ZA / CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US |
| ward | 3 | 0.3233 | no | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CN,DE,ES,FR,IE,IL,IT,MX,NO,SE,US |
| ward | 4 | 0.3379 | no | FI,KR,SG / BR,GB,IN,JP,NL,SA,ZA / CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE |
| ward | 5 | 0.3661 | no | FI,KR,SG / GB,IN,JP,SA / CN,ES,IL,IT,MX,NO,SE,US / DE,FR,IE / BR,NL,ZA |
| ward | 6 | 0.3515 | no | FI,KR,SG / GB,IN,JP,SA / CN,IT,US / DE,FR,IE / ES,IL,MX,NO,SE / BR,NL,ZA |
| average | 2 | 0.3362 | no | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / DE,FR,IE |
| average | 3 | 0.2145 | no | BR,CN,ES,FI,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / DE,FR,IE / SA |
| average | 4 | 0.2642 | no | FI,KR,SG / BR,CN,ES,GB,IL,IN,IT,JP,MX,NL,NO,SE,US,ZA / DE,FR,IE / SA |
| average | 5 | 0.3213 | no | FI,KR,SG / CN,ES,GB,IL,IN,IT,JP,MX,NO,SE,US / DE,FR,IE / BR,NL,ZA / SA |
| average | 6 | 0.2972 | no | KR / CN,ES,GB,IL,IN,IT,JP,MX,NO,SE,US / FI,SG / DE,FR,IE / BR,NL,ZA / SA |
→ any K/linkage recovering a KR+IE minority group: False

## A3.3 — mean pairwise Hellinger distance (eligible countries)
| anchor set | n countries | mean pairwise Hellinger |
|---|---|---|
| oecd_draft | 23 | 0.186 |
| oecd_final | 23 | 0.146 |
| unesco_student | 23 | 0.256 |
| unesco_student_on_oecd_eligible | 23 | 0.256 |
| unesco_teacher | 22 | 0.204 |
| unesco_teacher_on_oecd_eligible | 23 | 0.206 |
→ draft → final reduction: 21.8%

## A3.3 — distance of KR and IE to the canonical centroid
canonical set = draft Ward K=2 majority cluster, 17 countries: GB,SG,CN,JP,DE,FR,IL,IN,EE,NO,NL,ES,IT,SA,BR,MX,ZA
  KR_draft: 0.246
  IE_draft: 0.383
  canonical_mean_to_centroid_draft: 0.089
  canonical_max_to_centroid_draft: 0.232
  KR_final: 0.139
  IE_final: 0.19
  canonical_mean_to_centroid_final: 0.089
  canonical_max_to_centroid_final: 0.287

