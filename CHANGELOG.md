# CHANGELOG

## 2026-09-04 — OECD–EC final-framework re-run (post-hoc, additive)

- **Added** `anchors/oecd_ai_literacy_2026_final.csv`: the four domain-definition paragraphs of the OECD–EC *AI Literacy Framework* as published on 18 June 2026 (DOI 10.1787/65cd27d4-en, pp. 26/32/36/40; domains Engage with AI, Create with AI, Manage AI, Shape AI). The May 2025 review-draft anchors (`anchors/oecd_ai_literacy_2025.csv`) remain the pre-specified third anchor set and are unchanged.
- **Added** `scripts/06_oecd_final/run_oecd_final.py` (+ `RUN_ME.md`): self-contained re-run of embed → align (threshold 0.35) → 25×4 adherence → Hellinger → Ward/average → K=2–6 silhouette on the identical frozen corpus (28–30 May 2026 harvest; no documents added or removed). Does not modify the existing pipeline scripts.
- **Added outputs** with suffix `_oecd_final`: `data/adherence_matrix/sprint1_25x4_{counts,pct}_oecd_final.csv`, `sprint1_by_doc_{counts,pct}_oecd_final.csv`; `data/clustering/hellinger_dist_oecd_final.csv`, `clusters_oecd_final_{ward,average}_K{2..6}.csv`, `silhouette_oecd_final.csv`, `dendrogram_oecd_final_ward.png`, `oecd_draft_vs_final_comparison.csv`. The per-sentence alignment file `sprint1_alignment_full_oecd_final.jsonl` is generated locally and git-ignored like the other `*alignment_full*.jsonl` files.
- **Result:** under the final anchors the K = 2 Ward partition is degenerate (Estonia singleton vs 22 countries; silhouette 0.669 driven by the singleton). The fourth domain's redefinition from *Designing AI* (draft) to *Shape AI* (final) removes the axis that discriminated the Korea–Ireland pair under the draft anchors (O4 cross-country SD 14.1 → 3.8; KR O4 43.4% → 3.3%; mass migrates to Manage AI and Create with AI). Reported in the manuscript as a within-framework invariance test.
- **Added** threshold-invariance sweep (0.35–0.55) for the UNESCO student anchors, computed from the retained per-sentence scores; see manuscript Supporting Information, appendix E, Table E1.
- README: journal name withheld during review; language count corrected to 8; framework citations updated (teacher framework = Miao & Cukurova 2024).

## 2026-05-30 — Initial release

- Pre-specified pipeline (UNESCO student v1/v2, UNESCO teacher, OECD–EC draft anchors), six-module robustness battery, cross-framework replication.
