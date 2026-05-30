#!/usr/bin/env bash
# 03_harvest_gb_full.sh — strengthen GB corpus by fetching full-body HTML.
#
# Each gov.uk publication landing page links to a "full document" inner page
# at /government/publications/{slug}/{slug-body}. The inner page contains the
# substantive policy text, not the landing-page summary.
#
# This script downloads those inner pages and appends them as GB-XX_full to
# pilot_urls.csv + data/corpus_pilot/raw/.

set -euo pipefail
cd "$(dirname "$0")/../.."

RAW="data/corpus_pilot/raw"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 14.0) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"

declare -a JOBS=(
  "GB-01_full|https://www.gov.uk/government/publications/generative-artificial-intelligence-in-education/generative-artificial-intelligence-ai-in-education"
  "GB-02_full|https://www.gov.uk/government/publications/national-ai-strategy/national-ai-strategy-html-version"
  "GB-03_full|https://www.gov.uk/government/consultations/generative-artificial-intelligence-in-education-call-for-evidence/outcome/generative-artificial-intelligence-genai-in-education-call-for-evidence-government-response"
  "GB-04_full|https://www.gov.uk/government/publications/generative-ai-product-safety-expectations/generative-ai-product-safety-expectations"
)

mkdir -p "$RAW"
echo "[harvest] gov.uk inner-page bodies"
for job in "${JOBS[@]}"; do
  IFS='|' read -r doc_id url <<< "$job"
  out="$RAW/${doc_id}.html"
  if [ -s "$out" ]; then
    echo "[skip] $doc_id (already present)"
    continue
  fi
  echo "[get ] $doc_id  ←  $url"
  http=$(curl -sSL --max-time 60 -A "$UA" -w '%{http_code}' -o "$out" "$url" || echo "000")
  sz=$( [ -s "$out" ] && (stat -f%z "$out" 2>/dev/null || stat -c%s "$out") || echo 0 )
  if [ "$http" = "200" ] && [ "$sz" -gt 2000 ]; then
    echo "[ok  ] $doc_id  http=$http  size=$sz"
  else
    echo "[fail] $doc_id  http=$http  size=$sz — check URL"
    rm -f "$out"
  fi
done

# Add rows to pilot_urls.csv (only if not present)
CSV="data/corpus_inventory/pilot_urls.csv"
python3 - <<'PY'
import csv
from pathlib import Path
csv_path = Path("data/corpus_inventory/pilot_urls.csv")
with csv_path.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
    cols = list(rows[0].keys())
existing_ids = {r["doc_id"] for r in rows}

additions = [
    ("GB-01_full", "Generative AI in education — full body",
     "https://www.gov.uk/government/publications/generative-artificial-intelligence-in-education/generative-artificial-intelligence-ai-in-education",
     "2023-10-26", "pre", "guidance"),
    ("GB-02_full", "National AI Strategy — full HTML body",
     "https://www.gov.uk/government/publications/national-ai-strategy/national-ai-strategy-html-version",
     "2021-09-22", "pre", "strategy"),
    ("GB-03_full", "Generative AI call for evidence — government response",
     "https://www.gov.uk/government/consultations/generative-artificial-intelligence-in-education-call-for-evidence/outcome/generative-artificial-intelligence-genai-in-education-call-for-evidence-government-response",
     "2024-11", "post", "guidance"),
    ("GB-04_full", "Generative AI: product safety expectations — full body",
     "https://www.gov.uk/government/publications/generative-ai-product-safety-expectations/generative-ai-product-safety-expectations",
     "2025-01-22", "post", "guidance"),
]

for doc_id, title, url, date, cohort, genre in additions:
    if doc_id in existing_ids:
        continue
    row = {c: "" for c in cols}
    row.update({
        "country": "UK",
        "iso2": "GB",
        "language": "en",
        "doc_id": doc_id,
        "document_title": title,
        "issuing_body": "UK Department for Education / Office for AI",
        "publication_date": date,
        "unesco_cohort": cohort,
        "genre": genre,
        "format": "html",
        "url": url,
        "notes": "Full-body inner page, added by 03_harvest_gb_full.sh for Sprint 0 v2 GB strengthening",
    })
    rows.append(row)

with csv_path.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    w.writerows(rows)
print(f"[csv] {csv_path} — {len(rows)} total rows after additions")
PY

echo ""
echo "[done] Re-run extract + sentence-split + align to incorporate the new GB documents."
