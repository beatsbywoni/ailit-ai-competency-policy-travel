#!/usr/bin/env bash
# run_phase2_step1.sh — ZA-02 incremental align + matrix/Hellinger/IV.2 refresh.
#
# Prereq: data/corpus_full/raw/ZA-02.pdf placed (manual ISC download).
#
# Cost: ~3-5 min on Mac CPU (model load + ~1k ZA-02 sentences embed only;
# all other docs are skipped since their .alignment*.jsonl already exists
# and 07b_align_one rewrites only the named doc).
set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

echo "==============================================="
echo "Phase 2 step 1 — ZA-02 incremental + refresh"
echo "==============================================="

echo ""
echo "▶ 1/8  extract ZA-02 (other docs skipped via sentinel/idempotency)"
python scripts/02_pipeline/05_extract_corpus.py --corpus full --country ZA

echo ""
echo "▶ 2/8  sentence split (skips existing)"
python scripts/02_pipeline/06_sentence_split.py --corpus full

echo ""
echo "▶ 3/8  ZA-02 v2 alignment + append to full"
python scripts/02_pipeline/07b_align_one.py --doc-id ZA-02 --tag v2 \
    --student-csv anchors/unesco_ai_student_2024.csv

echo ""
echo "▶ 4/8  ZA-02 v1 alignment + append to full"
python scripts/02_pipeline/07b_align_one.py --doc-id ZA-02 --tag v1 \
    --student-csv anchors/unesco_ai_student_2024_v1_archived.csv

echo ""
echo "▶ 5/8  rebuild 25×12 + by-doc matrices (v2)"
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v2
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v2 --by-doc

echo ""
echo "▶ 6/8  rebuild 25×12 + by-doc matrices (v1)"
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v1
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v1 --by-doc

echo ""
echo "▶ 7/8  Hellinger clustering (v2, v1)"
python scripts/03_analysis/hellinger_cluster.py --tag v2
python scripts/03_analysis/hellinger_cluster.py --tag v1

echo ""
echo "▶ 8/8  inverse-corpus weighting 25-country (v2, v1)"
python scripts/04_robustness/inverse_corpus_weighting.py --corpus full --tag v2
python scripts/04_robustness/inverse_corpus_weighting.py --corpus full --tag v1

echo ""
echo "==============================================="
echo "Done. Inspect in order:"
echo "  data/adherence_matrix/sprint1_25x12_pct_v2.csv          (ZA row updated)"
echo "  data/clustering/dendrogram_v2_ward.png                  (post-ZA-02)"
echo "  data/robustness/inverse_weighted_summary_v2.csv         (25 countries)"
echo "==============================================="
