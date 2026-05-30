#!/usr/bin/env bash
# run_sprint0_pipeline.sh — full Sprint 0 pipeline (extract → split → embed → matrix → gate).
#
# Usage:
#   bash run_sprint0_pipeline.sh
#   bash run_sprint0_pipeline.sh --threshold 0.40
#
# Prerequisites:
#   - bash setup_venv.sh  (already done)
#   - bash scripts/01_corpus/02_harvest_pilot.sh  (already done)
#   - data/corpus_pilot/raw/ contains 20 documents
#
# First run will download the multilingual-mpnet model (~470 MB, one-time).

set -euo pipefail
cd "$(dirname "$0")"

if [ -d ".venv" ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
fi

THRESHOLD="0.35"
while [ $# -gt 0 ]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2;;
    -h|--help) sed -n '1,15p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

echo "==============================================="
echo "Sprint 0 pipeline — threshold $THRESHOLD"
echo "==============================================="
echo ""

echo "[1/5] Extracting text from PDF/HTML corpus..."
python scripts/02_pipeline/05_extract_corpus.py
echo ""

echo "[2/5] Splitting into sentences (40–600 chars)..."
python scripts/02_pipeline/06_sentence_split.py
echo ""

echo "[3/5] Embedding + 12-anchor alignment (this may take 5–15 min on CPU)..."
python scripts/02_pipeline/07_embed_and_align.py --threshold "$THRESHOLD"
echo ""

echo "[4/5] Building 5×12 country × anchor adherence matrix..."
python scripts/03_analysis/build_adherence_matrix.py
echo ""
python scripts/03_analysis/build_adherence_matrix.py --by-doc
echo ""

echo "[5/5] Evaluating Sprint 0 decision gate (planning §10.1)..."
python scripts/03_analysis/sprint0_gate.py
echo ""

echo "==============================================="
echo "Done. Open these to inspect:"
echo "  data/adherence_matrix/pilot_5x12_pct.csv"
echo "  data/adherence_matrix/pilot_by_doc_pct.csv"
echo "  docs/sprint0_decision.md"
echo "==============================================="
