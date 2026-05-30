#!/usr/bin/env bash
# 05b_ocr_mx01.sh — OCR MX-01 PDF (font CID broken) page-by-page.
#
# Run once. Outputs to /tmp/mx01_ocr_txt/p-*.txt, then concatenates
# into data/corpus_full/processed/MX-01.txt overwriting the broken
# pdfminer extract.
set -euo pipefail
cd "$(dirname "$0")/../.."

PDF="data/corpus_full/raw/MX-01.pdf"
IMG_DIR="/tmp/mx01_ocr_full"
TXT_DIR="/tmp/mx01_ocr_txt"
OUT="data/corpus_full/processed/MX-01.txt"
BAK="data/corpus_full/processed/MX-01_pdfminer.txt"

if [ ! -d "$IMG_DIR" ] || [ "$(ls -1 $IMG_DIR/p-*.ppm 2>/dev/null | wc -l)" -lt 143 ]; then
  mkdir -p "$IMG_DIR"
  echo "[step1] pdftoppm → 143 ppm images at 150 dpi"
  pdftoppm -r 150 "$PDF" "$IMG_DIR/p"
fi

mkdir -p "$TXT_DIR"
DONE=$(ls -1 $TXT_DIR/p-*.txt 2>/dev/null | wc -l)
TOTAL=$(ls -1 $IMG_DIR/p-*.ppm | wc -l)
echo "[step2] tesseract OCR — already done: $DONE / $TOTAL"

# OCR remaining pages in parallel (8-way)
ls $IMG_DIR/p-*.ppm | while read img; do
  base=$(basename "$img" .ppm)
  out="$TXT_DIR/$base.txt"
  if [ ! -s "$out" ]; then
    echo "$img"
  fi
done | xargs -n1 -P8 -I{} bash -c '
  img={}
  base=$(basename "$img" .ppm)
  tesseract "$img" "/tmp/mx01_ocr_txt/$base" 2>/dev/null
'

DONE=$(ls -1 $TXT_DIR/p-*.txt 2>/dev/null | wc -l)
echo "[step3] OCR complete: $DONE / $TOTAL pages"

# Backup pdfminer result
if [ ! -f "$BAK" ] && [ -f "$OUT" ]; then
  cp "$OUT" "$BAK"
fi

# Concatenate in order
echo "[step4] concatenate → $OUT"
ls -1 $TXT_DIR/p-*.txt | sort | xargs cat | python3 -c "
import sys, re
text = sys.stdin.read()
# collapse runs of blank lines, strip per-line whitespace
text = text.replace('\r\n','\n').replace('\r','\n')
lines = [ln.strip() for ln in text.split('\n')]
text = '\n'.join(lines)
while '\n\n\n' in text:
    text = text.replace('\n\n\n','\n\n')
sys.stdout.write(text.strip() + '\n')
" > "$OUT"

echo "[done] $OUT $(wc -c < $OUT) chars"
