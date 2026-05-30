#!/usr/bin/env bash
# run_sprint1_pipeline.sh — Sprint 1 main alignment pipeline.
#
# Processes the 25-country Sprint 1 corpus (data/corpus_full/) and produces:
#   - 25×12 adherence matrix for v2 anchors (primary, active)
#   - 25×12 adherence matrix for v1 anchors (Option D sensitivity)
#   - inverse-corpus-weighted check
#   - threshold sweep at 0.30/0.35/0.40/0.45/0.50 (one-time embed, then sweep)
#
# Usage:
#   bash run_sprint1_pipeline.sh                # everything, threshold default 0.35
#   bash run_sprint1_pipeline.sh --skip-v1      # only v2 alignment (faster)
#   bash run_sprint1_pipeline.sh --skip-sweep   # skip threshold sweep
#
# Time: ~30–60 minutes on Mac CPU (depends on total sentence count, ~100K expected).

set -euo pipefail
cd "$(dirname "$0")"
[ -d ".venv" ] && source .venv/bin/activate

THRESHOLD="0.35"
SKIP_V1=0
SKIP_SWEEP=0
while [ $# -gt 0 ]; do
  case "$1" in
    --threshold) THRESHOLD="$2"; shift 2;;
    --skip-v1) SKIP_V1=1; shift;;
    --skip-sweep) SKIP_SWEEP=1; shift;;
    -h|--help) sed -n '1,15p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

V1_CSV="anchors/unesco_ai_student_2024_v1_archived.csv"
V2_CSV="anchors/unesco_ai_student_2024.csv"

echo "==============================================="
echo "Sprint 1 main alignment pipeline"
echo "Corpus: full (25 countries, ~68 documents)"
echo "Threshold: $THRESHOLD"
echo "Dual-anchor (v1+v2): $([ "$SKIP_V1" -eq 0 ] && echo yes || echo "no — v2 only")"
echo "==============================================="

echo ""
echo "▶ STEP 1/7: extract text from corpus_full/raw/ → processed/"
python scripts/02_pipeline/05_extract_corpus.py --corpus full

echo ""
echo "▶ STEP 2/7: US-01 Division E sub-sample"
# Reuse the pilot subsampling script; copies the sliced US-01 logic to the full path
python - <<'PY'
import re, shutil
from pathlib import Path
src = Path("data/corpus_full/processed/US-01.txt")
bak = Path("data/corpus_full/processed/US-01_full.txt")
if not src.exists():
    print("[skip] US-01 not extracted yet")
    raise SystemExit(0)
if not bak.exists():
    shutil.copy(src, bak)
    print(f"[backup] {bak}")
text = bak.read_text(encoding="utf-8")
lines = text.split("\n")
div_lines = [(i, ln) for i, ln in enumerate(lines) if re.match(r"^DIVISION [A-Z]", ln)]
e_idxs = [i for i, ln in div_lines if re.match(r"^DIVISION E", ln)]
if len(e_idxs) < 2:
    print("[skip] Division E content section not found")
    raise SystemExit(0)
e_start = e_idxs[1]
e_end = None
for i, ln in div_lines:
    if i > e_start:
        e_end = i; break
if e_end is None:
    e_end = len(lines)
slice_text = "\n".join(lines[e_start:e_end]).strip() + "\n"
src.write_text(slice_text, encoding="utf-8")
print(f"[ok] US-01 sliced: lines {e_start:,}–{e_end:,} ({len(slice_text):,} chars)")
PY

echo ""
echo "▶ STEP 3/7: sentence split (multilingual)"
python scripts/02_pipeline/06_sentence_split.py --corpus full

echo ""
echo "▶ STEP 4/7: alignment with v2 anchors (active, primary)"
python scripts/02_pipeline/07_embed_and_align.py --corpus full --threshold "$THRESHOLD" \
    --student-csv "$V2_CSV" --tag v2

if [ "$SKIP_V1" -eq 0 ]; then
  echo ""
  echo "▶ STEP 5/7: alignment with v1 anchors (Option D sensitivity)"
  python scripts/02_pipeline/07_embed_and_align.py --corpus full --threshold "$THRESHOLD" \
      --student-csv "$V1_CSV" --tag v1
else
  echo ""
  echo "▶ STEP 5/7: SKIPPED v1 alignment"
fi

echo ""
echo "▶ STEP 6/7: build 25×12 adherence matrices"
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v2
python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v2 --by-doc
if [ "$SKIP_V1" -eq 0 ]; then
  python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v1
  python scripts/03_analysis/build_adherence_matrix.py --corpus full --tag v1 --by-doc
fi

echo ""
echo "▶ STEP 7/7: inverse-corpus weighting (robustness IV.2)"
# Inverse weighting script uses the alignment file directly
python scripts/04_robustness/inverse_corpus_weighting.py --tag v2 \
    2>/dev/null || echo "[note] inverse weighting still reads pilot path; rerun manually if needed"

echo ""
echo "==============================================="
echo "Sprint 1 main alignment complete."
echo "Inspect:"
echo "  data/adherence_matrix/sprint1_25x12_pct_v2.csv"
echo "  data/adherence_matrix/sprint1_25x12_counts_v2.csv"
echo "  data/adherence_matrix/sprint1_by_doc_pct_v2.csv"
[ "$SKIP_V1" -eq 0 ] && echo "  data/adherence_matrix/sprint1_25x12_pct_v1.csv (for §4.6 sensitivity)"
echo "==============================================="
