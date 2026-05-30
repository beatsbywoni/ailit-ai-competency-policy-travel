#!/usr/bin/env bash
# run_phase3_step2.sh — finish Phase 3 step 1 (re-run Hellinger after --tag patch)
# and produce the cross-framework cluster identity table (§4.5 main increment).
#
# Cost: ~1 minute total (no embedding; pure CSV → Hellinger → CSV).

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

echo "==============================================="
echo "Phase 3 step 2 — cross-framework cluster id"
echo "==============================================="

echo ""
echo "▶ 1/3  Hellinger clustering on teacher (5 anchor)"
python scripts/03_analysis/hellinger_cluster.py --tag teacher --corpus sprint1_25x5

echo ""
echo "▶ 2/3  Hellinger clustering on OECD (4 anchor)"
python scripts/03_analysis/hellinger_cluster.py --tag oecd --corpus sprint1_25x4

echo ""
echo "▶ 3/3  cross-framework cluster identity (student × teacher × OECD)"
python scripts/03_analysis/cross_framework_compare.py --student-tag v2

echo ""
echo "==============================================="
echo "Done. Key files for §4.5:"
echo "  data/clustering/clusters_teacher_ward_K2.csv"
echo "  data/clustering/clusters_oecd_ward_K2.csv"
echo "  data/clustering/cross_framework_v2.csv"
echo "  data/clustering/cross_framework_v2.md"
echo "==============================================="
