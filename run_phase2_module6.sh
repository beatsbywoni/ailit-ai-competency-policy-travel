#!/usr/bin/env bash
# run_phase2_module6.sh — discriminant validity (off-domain + hard-negative).
#
# Pipeline: harvest negative corpus URLs → extract → split → discriminant
# alignment. The positive corpus is reused from data/corpus_full/processed/
# (no re-extract / no re-embed; we just measure alignment rate per doc using
# the same model + threshold).
#
# Cost: ~3-5 min on Mac CPU (model load + ~few thousand neg-corpus sentences).

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

echo "==============================================="
echo "Phase 2 module 6 — discriminant validity"
echo "==============================================="

mkdir -p data/corpus_negative/raw data/corpus_negative/processed

echo ""
echo "▶ 1/4  harvest negative corpus (off-domain + hard-negative)"
bash scripts/05_validation/harvest_negative.sh

echo ""
echo "▶ 2/4  extract text from negative corpus"
python scripts/02_pipeline/05_extract_corpus.py --corpus negative

echo ""
echo "▶ 3/4  sentence split (negative corpus only)"
python scripts/02_pipeline/06_sentence_split.py --corpus negative

echo ""
echo "▶ 4/4  discriminant-validity alignment (v2 + v1)"
python scripts/05_validation/discriminant_validity.py --tag v2
python scripts/05_validation/discriminant_validity.py --tag v1

echo ""
echo "==============================================="
echo "Done. Inspect:"
echo "  data/robustness/discriminant_validity_v2.csv"
echo "  data/robustness/discriminant_report_v2.md"
echo "==============================================="
