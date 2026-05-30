#!/usr/bin/env bash
# rerun_us01_only.sh — minimal recovery after the run_sprint0_v2.sh bug.
#
# Background: the first v2 run had STEP 4 (US-01 sub-sample) BEFORE STEP 5
# (re-extract), which overwrote the sliced US-01.txt back to the full NDAA.
# The orchestrator now does extract→sub-sample, and 05_extract_corpus.py
# now refuses to overwrite a doc whose *_full.txt backup exists. To recover
# without re-doing the GB strengthening, this script:
#   1) re-applies the US-01 Division E slice
#   2) re-runs sentence-split, embedding, alignment, matrix
#   3) overwrites sprint0_decision_v2.md with the corrected numbers
#
# Usage:
#   bash rerun_us01_only.sh

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

echo "[1/5] US-01 → Division E slice"
python scripts/02_pipeline/05a_subsample_us01.py

echo ""
echo "[2/5] Re-split sentences"
python scripts/02_pipeline/06_sentence_split.py

echo ""
echo "[3/5] Re-embed + align (threshold 0.35)"
python scripts/02_pipeline/07_embed_and_align.py --threshold 0.35

echo ""
echo "[4/5] Adherence matrix"
python scripts/03_analysis/build_adherence_matrix.py
python scripts/03_analysis/build_adherence_matrix.py --by-doc

echo ""
echo "[5/5] Sprint 0 gate v2"
python scripts/03_analysis/sprint0_gate.py
cp docs/sprint0_decision.md docs/sprint0_decision_v2.md
echo ""
echo "[done] Inspect docs/sprint0_decision_v2.md for the corrected numbers."
