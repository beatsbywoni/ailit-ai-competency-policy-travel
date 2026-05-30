#!/usr/bin/env bash
# run_sprint0_5.sh — Sprint 0.5 dual-anchor verification + Sprint 1 prep.
#
# Steps:
#  1. Cohesion check on v1 (archived) anchors  → anchor_cohesion_report_v1.md
#  2. Cohesion check on v2 (active) anchors    → anchor_cohesion_report_v2.md
#  3. Pilot align with v1 anchors (uses same corpus + embedding) → pilot_alignment_full_v1.jsonl
#  4. Pilot align with v2 anchors                                  → pilot_alignment_full_v2.jsonl
#  5. Build 5×12 adherence matrices for v1 and v2
#  6. compare_anchor_versions.py → docs / matrix comparison + Path A verdict
#  7. Emit run summary
#
# Usage:
#   bash run_sprint0_5.sh
#   bash run_sprint0_5.sh --threshold 0.40

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

THRESHOLD="0.35"
while [ $# -gt 0 ]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2;;
    -h|--help) sed -n '1,15p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

V1_CSV="anchors/unesco_ai_student_2024_v1_archived.csv"
V2_CSV="anchors/unesco_ai_student_2024.csv"

if [ ! -s "$V1_CSV" ]; then
  echo "[error] $V1_CSV missing. Sprint 0.5 setup incomplete." >&2
  exit 1
fi

echo "==============================================="
echo "Sprint 0.5 — dual-anchor verification (v1 vs v2)"
echo "threshold = $THRESHOLD"
echo "==============================================="

echo ""
echo "▶ STEP 1/6: cohesion check (v1 archived)"
python scripts/05_validation/anchor_distance_check.py --student-csv "$V1_CSV" --tag v1

echo ""
echo "▶ STEP 2/6: cohesion check (v2 active)"
python scripts/05_validation/anchor_distance_check.py --student-csv "$V2_CSV" --tag v2

echo ""
echo "▶ STEP 3/6: pilot alignment with v1 anchors"
python scripts/02_pipeline/07_embed_and_align.py --threshold "$THRESHOLD" \
    --student-csv "$V1_CSV" --tag v1

echo ""
echo "▶ STEP 4/6: pilot alignment with v2 anchors"
python scripts/02_pipeline/07_embed_and_align.py --threshold "$THRESHOLD" \
    --student-csv "$V2_CSV" --tag v2

echo ""
echo "▶ STEP 5/6: build adherence matrices (v1, v2)"
python scripts/03_analysis/build_adherence_matrix.py --tag v1
python scripts/03_analysis/build_adherence_matrix.py --tag v2

echo ""
echo "▶ STEP 6/6: side-by-side comparison + Path A verdict"
python scripts/03_analysis/compare_anchor_versions.py

echo ""
echo "==============================================="
echo "Done. Inspect in order:"
echo "  data/validation/anchor_cohesion_report_v2.md"
echo "  data/adherence_matrix/pilot_5x12_pct_v2.csv"
echo "  data/adherence_matrix/anchor_version_comparison.md"
echo "==============================================="
