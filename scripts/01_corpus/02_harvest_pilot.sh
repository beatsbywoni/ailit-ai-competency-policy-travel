#!/usr/bin/env bash
# 02_harvest_pilot.sh — download all pilot corpus documents.
#
# Reads data/corpus_inventory/pilot_urls.csv and downloads each `url` to
# data/corpus_pilot/raw/{doc_id}.{format}. Skips files already present
# (idempotent). Logs to data/corpus_pilot/raw/_harvest_log.tsv.
#
# Usage:
#   bash scripts/01_corpus/02_harvest_pilot.sh
#   bash scripts/01_corpus/02_harvest_pilot.sh --country KR
#   bash scripts/01_corpus/02_harvest_pilot.sh --force

set -euo pipefail
cd "$(dirname "$0")/../.."

CSV="data/corpus_inventory/pilot_urls.csv"
OUT_DIR="data/corpus_pilot/raw"
LOG="$OUT_DIR/_harvest_log.tsv"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
FILTER_COUNTRY=""
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --country) FILTER_COUNTRY="$2"; shift 2;;
    --force)   FORCE=1; shift;;
    -h|--help) sed -n '1,15p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

mkdir -p "$OUT_DIR"
echo -e "ts\tdoc_id\turl\tstatus\tbytes" > "$LOG"

# Build job list with python (handles quoted CSV fields), then iterate in current shell.
JOB_LIST="$(mktemp)"
python3 - "$CSV" "$FILTER_COUNTRY" > "$JOB_LIST" <<'PY'
import csv, sys
csv_path, filter_country = sys.argv[1], sys.argv[2]
with open(csv_path, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if filter_country and r["iso2"] != filter_country:
            continue
        url = (r.get("url") or "").strip()
        if not url or url == "TBD":
            continue
        print("\t".join([r["doc_id"], r["iso2"], r["format"], url]))
PY

n_total=0; n_ok=0; n_skip=0; n_fail=0; n_manual=0

while IFS=$'\t' read -r doc_id iso2 fmt url; do
  n_total=$((n_total+1))
  out_path="$OUT_DIR/${doc_id}.${fmt}"

  # URLs prefixed with "MANUAL:" require browser download — skip with reminder.
  if [[ "$url" == MANUAL:* ]]; then
    real_url="${url#MANUAL:}"
    if [ -s "$out_path" ]; then
      echo "[ok  ] $doc_id  manual download already in place"
      printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$real_url" "manual_ok" "$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")" >> "$LOG"
      n_ok=$((n_ok+1))
    else
      echo "[MAN ] $doc_id  ←  browser download from: $real_url"
      printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$real_url" "manual_needed" "0" >> "$LOG"
      n_manual=$((n_manual+1))
    fi
    continue
  fi

  if [ -s "$out_path" ] && [ "$FORCE" -eq 0 ]; then
    sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
    echo "[skip] $doc_id (already present, $sz bytes)"
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "skip" "$sz" >> "$LOG"
    n_skip=$((n_skip+1))
    continue
  fi

  echo "[get ] $doc_id  ←  $url"
  http=$(curl -sSL --max-time 60 -A "$UA" -w '%{http_code}' -o "$out_path" "$url" || echo "000")
  if [ -s "$out_path" ]; then
    sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
  else
    sz=0
  fi
  if [ "$http" = "200" ] && [ "$sz" -gt 1024 ]; then
    echo "[ok  ] $doc_id  http=$http  size=$sz"
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "ok" "$sz" >> "$LOG"
    n_ok=$((n_ok+1))
  else
    echo "[fail] $doc_id  http=$http  size=$sz"
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "fail_http${http}" "$sz" >> "$LOG"
    rm -f "$out_path"
    n_fail=$((n_fail+1))
  fi
done < "$JOB_LIST"

rm -f "$JOB_LIST"

echo ""
echo "[summary] total=$n_total  ok=$n_ok  skip=$n_skip  fail=$n_fail  manual_needed=$n_manual"
echo "[log    ] $LOG"

if [ "$n_manual" -gt 0 ] || [ "$n_fail" -gt 0 ]; then
  echo ""
  echo "[manual checklist]"
  awk -F'\t' '$4=="manual_needed" || $4 ~ /^fail/ {printf "  - %-6s  %s\n", $2, $3}' "$LOG"
  echo ""
  echo "After saving files, re-run this script — it skips files already present."
fi
