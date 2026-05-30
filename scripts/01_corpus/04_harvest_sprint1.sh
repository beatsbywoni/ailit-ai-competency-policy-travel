#!/usr/bin/env bash
# 04_harvest_sprint1.sh — Sprint 1 25-country corpus harvest.
#
# Same idempotent pattern as 02_harvest_pilot.sh, but:
# - reads data/corpus_inventory/sprint1_urls.csv (25 countries)
# - writes to data/corpus_full/raw/{doc_id}.{format}
# - logs to data/corpus_full/raw/_harvest_log.tsv
# - URLs prefixed with "TBD-Phase1" are skipped with a [TODO] mark
# - --country filter still supported
#
# Usage:
#   bash scripts/01_corpus/04_harvest_sprint1.sh                  # all rows
#   bash scripts/01_corpus/04_harvest_sprint1.sh --country JP
#   bash scripts/01_corpus/04_harvest_sprint1.sh --force          # re-download
#   bash scripts/01_corpus/04_harvest_sprint1.sh --status         # just print which doc_ids still need URLs

set -euo pipefail
cd "$(dirname "$0")/../.."

CSV="data/corpus_inventory/sprint1_urls.csv"
OUT_DIR="data/corpus_full/raw"
LOG="$OUT_DIR/_harvest_log.tsv"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
FILTER_COUNTRY=""
FORCE=0
STATUS_ONLY=0

while [ $# -gt 0 ]; do
  case "$1" in
    --country) FILTER_COUNTRY="$2"; shift 2;;
    --force)   FORCE=1; shift;;
    --status)  STATUS_ONLY=1; shift;;
    -h|--help) sed -n '1,20p' "$0"; exit 0;;
    *) echo "[error] unknown arg: $1" >&2; exit 1;;
  esac
done

mkdir -p "$OUT_DIR"

if [ "$STATUS_ONLY" -eq 1 ]; then
  python3 - "$CSV" "$FILTER_COUNTRY" <<'PY'
import csv, sys
csv_path, filt = sys.argv[1], sys.argv[2]
total = ready = tbd = manual = 0
by_iso_total = {}
by_iso_ready = {}
with open(csv_path, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if filt and r["iso2"] != filt:
            continue
        total += 1
        iso = r["iso2"]
        by_iso_total[iso] = by_iso_total.get(iso, 0) + 1
        url = (r.get("url") or "").strip()
        if url.startswith("TBD"):
            tbd += 1
        elif url.startswith("MANUAL"):
            manual += 1
        else:
            ready += 1
            by_iso_ready[iso] = by_iso_ready.get(iso, 0) + 1

print(f"Inventory snapshot ({csv_path}):")
print(f"  total rows           : {total}")
print(f"  URLs ready (auto)    : {ready}")
print(f"  URLs ready (manual)  : {manual}")
print(f"  TBD (Phase-1 search) : {tbd}")
print()
print(f"{'ISO':<4} {'docs':>4} {'ready':>5}  pending")
for iso in sorted(by_iso_total):
    pend = by_iso_total[iso] - by_iso_ready.get(iso, 0)
    mark = "" if pend == 0 else f"  ({pend} TBD)"
    print(f"{iso:<4} {by_iso_total[iso]:>4} {by_iso_ready.get(iso, 0):>5}{mark}")
PY
  exit 0
fi

echo -e "ts\tdoc_id\turl\tstatus\tbytes" > "$LOG"

JOB_LIST="$(mktemp)"
python3 - "$CSV" "$FILTER_COUNTRY" > "$JOB_LIST" <<'PY'
import csv, sys
csv_path, filt = sys.argv[1], sys.argv[2]
with open(csv_path, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if filt and r["iso2"] != filt:
            continue
        url = (r.get("url") or "").strip()
        if not url or url.startswith("TBD") or url == "TBD":
            continue
        print("\t".join([r["doc_id"], r["iso2"], r["format"], url]))
PY

n_total=0; n_ok=0; n_skip=0; n_fail=0; n_manual=0

while IFS=$'\t' read -r doc_id iso2 fmt url; do
  n_total=$((n_total+1))
  out_path="$OUT_DIR/${doc_id}.${fmt}"

  if [[ "$url" == MANUAL:* ]]; then
    real_url="${url#MANUAL:}"
    if [ -s "$out_path" ]; then
      sz=$(stat -f%z "$out_path" 2>/dev/null || stat -c%s "$out_path")
      echo "[ok  ] $doc_id  manual_in_place  $sz B"
      printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$real_url" "manual_ok" "$sz" >> "$LOG"
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
    echo "[skip] $doc_id  ($sz B)"
    printf '%s\t%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$doc_id" "$url" "skip" "$sz" >> "$LOG"
    n_skip=$((n_skip+1))
    continue
  fi

  echo "[get ] $doc_id  ←  $url"
  # Default attempt: HTTP/2 with browser UA, 120s for large PDFs.
  http=$(curl -sSL --max-time 120 -A "$UA" -w '%{http_code}' -o "$out_path" "$url" || echo "000")
  # Retry once with --http1.1 if HTTP/2 stream errored or returned 0.
  # education.gov.au and a few other Cloudflare-fronted .gov sites mis-frame
  # responses over h2, returning curl error 92 (INTERNAL_ERROR).
  if [ "$http" = "000" ] || [ ! -s "$out_path" ]; then
    http=$(curl -sSL --max-time 120 --http1.1 -A "$UA" -w '%{http_code}' -o "$out_path" "$url" || echo "000")
  fi
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
  awk -F'\t' '$4=="manual_needed" || $4 ~ /^fail/ {printf "  - %-12s  %s\n", $2, $3}' "$LOG"
fi
