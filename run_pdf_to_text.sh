#!/usr/bin/env bash
# run_pdf_to_text.sh — convert all PDFs in data/source_pdfs/ to UTF-8 text.
#
# Usage:
#   bash run_pdf_to_text.sh                 # default: all PDFs in data/source_pdfs/
#   bash run_pdf_to_text.sh path/to/foo.pdf # specific files
#
# Assumes setup_venv.sh has been run.

set -euo pipefail
cd "$(dirname "$0")"

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

"$PY" scripts/02_pipeline/04_pdf_to_text.py "$@"
