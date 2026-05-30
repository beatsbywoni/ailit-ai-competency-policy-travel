#!/usr/bin/env bash
# harvest_negative.sh — fetch off-domain and hard-negative corpora for
# discriminant-validity testing (C&E checklist I.4 + I.5).
#
# Same conventions as scripts/01_corpus/04_harvest_sprint1.sh: skip existing,
# retry on HTTP/2 stream errors with --http1.1, log per-doc outcome.

set -euo pipefail
cd "$(dirname "$0")/../.."

OUT_DIR="data/corpus_negative/raw"
LOG="$OUT_DIR/_harvest_log.tsv"
INVENTORY="data/corpus_inventory/negative_urls.csv"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

mkdir -p "$OUT_DIR"
[ -f "$LOG" ] || echo -e "timestamp\tdoc_id\turl\tstatus\tsize_bytes" > "$LOG"

n_total=0; n_ok=0; n_skip=0; n_fail=0

# Read CSV without header line; columns: domain,doc_id,title,body,date,kind,fmt,url,notes
python3 <<'PY' > /tmp/neg_rows.tsv
import csv, sys
with open("data/corpus_inventory/negative_urls.csv") as f:
    for r in csv.DictReader(f):
        url = r["url"]
        if url.startswith(("MANUAL:", "DROP:")):
            continue
        print("\t".join([r["doc_id"], r["format"], url]))
PY

while IFS=$'\t' read -r doc_id fmt url; do
  n_total=$((n_total+1))
  out_path="$OUT_DIR/${doc_id}.${fmt}"

  if [ -s "$out_path" ]; then
    sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
    echo "[skip] $doc_id  ($sz B)"
    n_skip=$((n_skip+1))
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "skip" "$sz" >> "$LOG"
    continue
  fi

  echo "[get ] $doc_id  ←  $url"
  http=$(curl -sSL --max-time 60 -A "$UA" -w '%{http_code}' -o "$out_path" "$url" || echo "000")
  if [ "$http" = "000" ] || [ ! -s "$out_path" ]; then
    http=$(curl -sSL --max-time 60 -A "$UA" --http1.1 -w '%{http_code}' -o "$out_path" "$url" || echo "000")
  fi
  if [ "$http" = "200" ] || [ "$http" = "201" ]; then
    sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
    echo "[ok  ] $doc_id  http=$http  size=$sz"
    n_ok=$((n_ok+1))
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "ok_http=$http" "$sz" >> "$LOG"
  else
    sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
    echo "[fail] $doc_id  http=$http  size=$sz"
    n_fail=$((n_fail+1))
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "fail_http=$http" "$sz" >> "$LOG"
  fi
done < /tmp/neg_rows.tsv

echo ""
echo "[summary] total=$n_total  ok=$n_ok  skip=$n_skip  fail=$n_fail"
echo "[log    ] $LOG"
