# Sprint 0 decision memo

**Date**: 2026-05-29
**Threshold**: 0.35 (planning §7.3 default)
**Pilot scope**: 5 countries × 12 UNESCO student anchors
**Source**: `data/adherence_matrix/pilot_5x12_pct.csv`

## Per-country asymmetry table

| Country | Tool-use share (S07–S09, %) | Ethics share (S04–S06, %) | Tool ÷ Ethics | S08 only ÷ Ethics | Total aligned |
|---|---:|---:|---:|---:|---:|
| KR | 37.6 | 33.0 | 1.14 | 0.81 | 3,443 |
| GB | 11.6 | 24.7 | 0.47 | 0.11 | 716 |
| SG | 13.8 | 21.8 | 0.63 | 0.08 | 515 |
| FI | 23.1 | 31.6 | 0.73 | 0.30 | 1,679 |
| US | 20.0 | 27.2 | 0.74 | 0.32 | 3,242 |

**Countries with tool ÷ ethics ≥ 3.0**: 0 / 5
**Countries with S08 alone ÷ ethics ≥ 3.0**: 0 / 5

## Verdict — **RED**

Revisit anchors before scaling. No clear asymmetry signal at threshold 0.35. Check anchor distance matrix, threshold sweep, and whether short landing-page documents (GB-01..04, SG-02, SG-03) are starving the signal.

## Next actions

1. Update `docs/sprint0_progress.md` with this verdict.
2. If GREEN: begin Sprint 1 — full 25-country corpus harvest (§10.2).
3. If YELLOW: run threshold sweep (`04_robustness/threshold_sensitivity.py`), strengthen GB and SG corpora by fetching attached PDFs from landing pages.
4. If RED: revisit anchor wording (consider lifting the OECD 'Managing AI' framing into the primary set, or splitting S08 into separate Application-vs-Workforce sub-anchors).

## Caveat

Sprint 0 pilot uses thin landing-page extraction for several UK and Singapore documents (GB-01..04 each ≤ 1.3KB extracted; SG-02..03 ≤ 4.5KB). Per-country signal for these documents is correspondingly weak and may overstate or understate true alignment patterns. Sprint 1 corpus harvest will fetch attached PDFs from landing pages, which is expected to roughly 10× the per-country sentence count for UK and SG and reduce noise in the asymmetry ratios.