# OECD–EC final-framework re-run — verification report
eligibility floor: n_aligned >= 50

## A2 — alignment totals (all 25 countries)
draft : 18,872 aligned sentences
final : 19,509 aligned sentences

eligible under both (n >= 50): 23 countries — excluded: AU(draft n=32, final n=37), AE(draft n=6, final n=6)

## A2 — Table 3 (per-domain adherence share, %, across eligible countries)
| domain | draft mean | draft SD | draft range | final mean | final SD | final range |
|---|---|---|---|---|---|---|
| AILIT-O01 → AILIT-O01F | 25.2 | 6.1 | 14.5–36.8 (IT–SE) | 25.2 | 7.8 | 15.3–49.1 (US–EE) |
| AILIT-O02 → AILIT-O02F | 14.7 | 5.7 | 3.0–23.2 (IE–IN) | 22.8 | 7.8 | 0.0–36.3 (EE–CN) |
| AILIT-O03 → AILIT-O03F | 31.6 | 13.2 | 8.2–56.6 (IE–EE) | 45.6 | 6.4 | 33.0–58.5 (SA–BR) |
| AILIT-O04 → AILIT-O04F | 28.5 | 14.4 | 3.8–69.0 (EE–IE) | 6.4 | 5.1 | 1.0–25.3 (SA–IE) |
| sum of SDs (old row, for reference) | | 39.4 | | | 27.1 | |

Named values:
  KR: O4 draft 43.4% → final 9.5%   | O3 14.2 → 43.3 | O2 7.4 → 31.3 | O1 35.0 → 15.9
  US: O4 draft 54.7% → final 10.6%   | O3 16.3 → 55.9 | O2 4.7 → 18.2 | O1 24.2 → 15.3
  IE: O4 draft 69.0% → final 25.3%   | O3 8.2 → 37.3 | O2 3.0 → 12.2 | O1 19.8 → 25.2
  FR: O4 draft 22.7% → final 10.4%   | O3 34.1 → 39.5 | O2 14.5 → 21.2 | O1 28.8 → 28.9
  EE: O4 draft 3.8% → final 3.8%   | O3 56.6 → 47.2 | O2 9.4 → 0.0 | O1 30.2 → 49.1
  top final Shape-AI shares: IE 25.3%, US 10.6%, FR 10.4%, NO 10.1%

## A2 — Hellinger matrix and silhouettes (final anchors)
on-disk Hellinger matrix: same country order = True; max |diff| vs recomputed = 4.99e-05
| linkage | K | silhouette | groups |
|---|---|---|---|
| ward | 2 | 0.6507 | BR,CA,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / EE |
| ward | 3 | 0.2879 | BR,CA,CN,ES,FI,FR,IE,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG / EE |
| ward | 4 | 0.2987 | BR,CA,CN,ES,FI,FR,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG / EE / IE |
| ward | 5 | 0.3636 | CN,FI,KR / DE,GB,IL,IT,JP,NL,SA,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / EE / IE |
| ward | 6 | 0.3605 | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / EE / IE / SA |
| average | 2 | 0.6507 | BR,CA,CN,DE,ES,FI,FR,GB,IE,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / EE |
| average | 3 | 0.4683 | BR,CA,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / EE / IE |
| average | 4 | 0.3183 | BR,CA,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / EE / IE / SA |
| average | 5 | 0.2548 | CN,FI,KR / BR,CA,DE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SE,SG,US,ZA / EE / IE / SA |
| average | 6 | 0.3605 | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / EE / IE / SA |

Draft anchors, same eligible set (reference):
  ward K=2 silhouette 0.4827  groups CA,FI,IE,KR,SE,US / BR,CN,DE,EE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SA,SG,ZA
  average K=2 silhouette 0.4827  groups CA,FI,IE,KR,SE,US / BR,CN,DE,EE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SA,SG,ZA

## A3.1 — Estonia excluded (final anchors)
| linkage | K | silhouette | KR&IE together in a minority group? | groups |
|---|---|---|---|---|
| ward | 2 | 0.3010 | no | BR,CA,CN,ES,FI,FR,IE,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG |
| ward | 3 | 0.3122 | no | BR,CA,CN,ES,FI,FR,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG / IE |
| ward | 4 | 0.3801 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SA,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / IE |
| ward | 5 | 0.3769 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / IE / SA |
| ward | 6 | 0.3911 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / CA,FR,IN,MX,NO,SE,US / IE / BR,ES,ZA / SA |
| average | 2 | 0.4896 | no | BR,CA,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / IE |
| average | 3 | 0.3328 | no | BR,CA,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / IE / SA |
| average | 4 | 0.2664 | no | CN,FI,KR / BR,CA,DE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SE,SG,US,ZA / IE / SA |
| average | 5 | 0.3769 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / BR,CA,ES,FR,IN,MX,NO,SE,US,ZA / IE / SA |
| average | 6 | 0.3911 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / CA,FR,IN,MX,NO,SE,US / IE / BR,ES,ZA / SA |
→ any K/linkage recovering a KR+IE minority group: False

## A3.2 — eligibility floor n >= 100 (final anchors)
eligible: 21 — dropped vs n>=50: ['CA', 'EE']
| linkage | K | silhouette | KR&IE together in a minority group? | groups |
|---|---|---|---|---|
| ward | 2 | 0.2914 | no | BR,CN,ES,FI,FR,IE,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG |
| ward | 3 | 0.3005 | no | BR,CN,ES,FI,FR,IN,KR,MX,NO,SE,US,ZA / DE,GB,IL,IT,JP,NL,SA,SG / IE |
| ward | 4 | 0.3782 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SA,SG / BR,ES,FR,IN,MX,NO,SE,US,ZA / IE |
| ward | 5 | 0.3888 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SA,SG / FR,IN,MX,NO,SE,US / IE / BR,ES,ZA |
| ward | 6 | 0.4041 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / FR,IN,MX,NO,SE,US / IE / BR,ES,ZA / SA |
| average | 2 | 0.4843 | no | BR,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SA,SE,SG,US,ZA / IE |
| average | 3 | 0.3203 | no | BR,CN,DE,ES,FI,FR,GB,IL,IN,IT,JP,KR,MX,NL,NO,SE,SG,US,ZA / IE / SA |
| average | 4 | 0.2728 | no | CN,FI,KR / BR,DE,ES,FR,GB,IL,IN,IT,JP,MX,NL,NO,SE,SG,US,ZA / IE / SA |
| average | 5 | 0.3752 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / BR,ES,FR,IN,MX,NO,SE,US,ZA / IE / SA |
| average | 6 | 0.3318 | no | CN,FI,KR / DE,GB,IL,IT,JP,NL,SG / US / BR,ES,FR,IN,MX,NO,SE,ZA / IE / SA |
→ any K/linkage recovering a KR+IE minority group: False

## A3.3 — mean pairwise Hellinger distance (eligible countries)
| anchor set | n countries | mean pairwise Hellinger |
|---|---|---|
| oecd_draft | 23 | 0.186 |
| oecd_final | 23 | 0.144 |
| unesco_student | 23 | 0.256 |
| unesco_student_on_oecd_eligible | 23 | 0.256 |
| unesco_teacher | 22 | 0.204 |
| unesco_teacher_on_oecd_eligible | 23 | 0.206 |
→ draft → final reduction: 22.6%

## A3.3 — distance of KR and IE to the canonical centroid
canonical set = draft Ward K=2 majority cluster, 17 countries: GB,SG,CN,JP,DE,FR,IL,IN,EE,NO,NL,ES,IT,SA,BR,MX,ZA
  KR_draft: 0.246
  IE_draft: 0.383
  canonical_mean_to_centroid_draft: 0.089
  canonical_max_to_centroid_draft: 0.232
  KR_final: 0.122
  IE_final: 0.227
  canonical_mean_to_centroid_final: 0.091
  canonical_max_to_centroid_final: 0.362

