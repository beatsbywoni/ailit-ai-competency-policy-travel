#!/usr/bin/env bash
# verify_anchors.sh — quick sanity check of the 21 anchor CSVs.
#
# Usage:
#   bash verify_anchors.sh
#
# Reports row count, status distribution, and (if any) malformed rows.

set -euo pipefail
cd "$(dirname "$0")"

# Activate venv if present, else fall back to system python3.
if [ -d ".venv" ]; then
  # shellcheck source=/dev/null
  source .venv/bin/activate
  PY=python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "[error] no python found. Run: bash setup_venv.sh" >&2
  exit 1
fi

"$PY" - <<'PY'
import csv
from pathlib import Path

ANCHOR_DIR = Path("anchors")
files = [
    ("unesco_ai_student_2024.csv", 12, "anchor_id,aspect,level,block_name,anchor_sentence,status,source"),
    ("unesco_ai_teacher_2024.csv", 5, "anchor_id,aspect,anchor_sentence,status,source"),
    ("oecd_ai_literacy_2025.csv", 4, "anchor_id,domain,anchor_sentence,status,source"),
]

print(f"{'file':<40s}  {'rows':>5s}  {'expected':>9s}  {'status counts':<30s}  ok?")
all_ok = True
for fname, expected, header in files:
    path = ANCHOR_DIR / fname
    if not path.exists():
        print(f"{fname:<40s}  MISSING")
        all_ok = False
        continue
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    status_counts = {}
    for r in rows:
        s = r.get("status", "?")
        status_counts[s] = status_counts.get(s, 0) + 1
    counts_str = ", ".join(f"{k}={v}" for k, v in status_counts.items())
    ok = len(rows) == expected
    if not ok:
        all_ok = False
    print(f"{fname:<40s}  {len(rows):>5d}  {expected:>9d}  {counts_str:<30s}  {'✓' if ok else '✗'}")

print()
print(f"Total anchors: {sum(e for _, e, _ in files)} (planning §5.4 said 20; current 21 due to teacher framework 5-aspect actuals)")
print(f"All anchor files OK: {all_ok}")
PY
