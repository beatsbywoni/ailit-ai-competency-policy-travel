#!/usr/bin/env bash
# run_phase3_step1.sh — Cross-organisational anchor analysis (Phase 3 §4.5.2 + §4.5.3).
#
# Re-runs the 25-country alignment with two additional anchor frameworks:
#   - UNESCO teacher framework (5 anchors)
#   - OECD AI Literacy / EC AI Literacy 2025 (4 anchors)
#
# Then builds matrices and Hellinger clustering for each, so we can compare
# whether the K=2 partition {KR, IE} replicates across all three frameworks.
# This is the critical Phase 3 evidence that strengthens the manuscript's
# main claim: the Tool-use deviating cluster is a property of national
# policy text, not of any single anchor system.
#
# Cost: ~15-25 min on Mac CPU (two full embed passes over 36k sentences;
# anchors are pre-cached; corpus model is HF-cached from Phase 1).

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

echo "==============================================="
echo "Phase 3 step 1 — cross-org anchor replication"
echo "==============================================="

echo ""
echo "▶ 1/6  align corpus to UNESCO teacher anchors (5)"
python scripts/02_pipeline/07_embed_and_align.py --corpus full --threshold 0.35 \
    --anchor-set teacher --tag teacher

echo ""
echo "▶ 2/6  align corpus to OECD AILit anchors (4)"
python scripts/02_pipeline/07_embed_and_align.py --corpus full --threshold 0.35 \
    --anchor-set oecd --tag oecd

echo ""
echo "▶ 3/6  build 25 × 5 teacher matrix"
python scripts/03_analysis/build_adherence_matrix.py --corpus full \
    --tag teacher --anchor-set teacher
python scripts/03_analysis/build_adherence_matrix.py --corpus full \
    --tag teacher --anchor-set teacher --by-doc

echo ""
echo "▶ 4/6  build 25 × 4 OECD matrix"
python scripts/03_analysis/build_adherence_matrix.py --corpus full \
    --tag oecd --anchor-set oecd
python scripts/03_analysis/build_adherence_matrix.py --corpus full \
    --tag oecd --anchor-set oecd --by-doc

echo ""
echo "▶ 5/6  Hellinger clustering on teacher matrix (5-anchor)"
python scripts/03_analysis/hellinger_cluster.py --tag teacher \
    --corpus sprint1_25x5

echo ""
echo "▶ 6/6  Hellinger clustering on OECD matrix (4-anchor)"
python scripts/03_analysis/hellinger_cluster.py --tag oecd \
    --corpus sprint1_25x4

echo ""
echo "==============================================="
echo "Done. Inspect in order:"
echo "  data/adherence_matrix/sprint1_25x5_pct_teacher.csv"
echo "  data/adherence_matrix/sprint1_25x4_pct_oecd.csv"
echo "  data/clustering/clusters_teacher_ward_K2.csv"
echo "  data/clustering/clusters_oecd_ward_K2.csv"
echo "  data/clustering/dendrogram_teacher_ward.png"
echo "  data/clustering/dendrogram_oecd_ward.png"
echo "==============================================="
