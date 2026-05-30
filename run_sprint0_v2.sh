#!/usr/bin/env bash
# run_sprint0_v2.sh — Sprint 0 v2 robustness/diagnostics pipeline.
#
# Runs the four post-RED-verdict items in sequence:
#   1) Anchor cohesion check (21×21 cosine, identify over-recruiting anchors)
#   2) Threshold sweep (0.30 / 0.35 / 0.40 / 0.45 / 0.50)
#   3) UK gov.uk inner-page strengthening (4 new GB-XX_full documents)
#   4) US-01 sub-sampling to Division E (NAI Act of 2020 only)
#   5) Re-run alignment + matrix + gate with the strengthened corpus
#   6) Emit sprint0_decision_v2.md
#
# Each step writes its own outputs into data/validation, data/robustness,
# data/corpus_pilot, and data/adherence_matrix. The script aborts on any
# step's error code so the user can inspect midway.
#
# Usage:
#   bash run_sprint0_v2.sh
#   bash run_sprint0_v2.sh --skip-harvest    # skip step 3 download
#   bash run_sprint0_v2.sh --threshold 0.40  # override final alignment threshold

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

THRESHOLD="0.35"
SKIP_HARVEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2;;
    --skip-harvest) SKIP_HARVEST=1; shift;;
    -h|--help) sed -n '1,20p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

echo "==============================================="
echo "Sprint 0 v2 — robustness + corpus strengthening"
echo "==============================================="

echo ""
echo "▶ STEP 1/6: anchor cohesion check"
python scripts/05_validation/anchor_distance_check.py

echo ""
echo "▶ STEP 2/6: threshold sweep (uses already-split sentences)"
python scripts/04_robustness/threshold_sensitivity.py

if [ "$SKIP_HARVEST" -eq 0 ]; then
  echo ""
  echo "▶ STEP 3/6: GB inner-page strengthening"
  bash scripts/01_corpus/03_harvest_gb_full.sh
else
  echo ""
  echo "▶ STEP 3/6: SKIPPED by --skip-harvest"
fi

echo ""
echo "▶ STEP 4/6: re-extract (picks up new GB docs; preserves US-01 sub-sample if any)"
python scripts/02_pipeline/05_extract_corpus.py

echo ""
echo "▶ STEP 5/6: US-01 sub-sample to Division E, then split + embed + align"
python scripts/02_pipeline/05a_subsample_us01.py
python scripts/02_pipeline/06_sentence_split.py
python scripts/02_pipeline/07_embed_and_align.py --threshold "$THRESHOLD"
python scripts/03_analysis/build_adherence_matrix.py
python scripts/03_analysis/build_adherence_matrix.py --by-doc

echo ""
echo "▶ STEP 6/6: write Sprint 0 v2 decision memo"
python scripts/03_analysis/sprint0_gate.py
# Move v1 → v1, save as v2
if [ -f docs/sprint0_decision.md ]; then
  cp docs/sprint0_decision.md docs/sprint0_decision_v2.md
fi

echo ""
echo "==============================================="
echo "Done. Inspect in order:"
echo "  data/validation/anchor_cohesion_report.md"
echo "  data/robustness/threshold_sweep_report.md"
echo "  data/adherence_matrix/pilot_5x12_pct.csv"
echo "  docs/sprint0_decision_v2.md"
echo "==============================================="
