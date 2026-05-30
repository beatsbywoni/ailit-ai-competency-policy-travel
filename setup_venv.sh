#!/usr/bin/env bash
# setup_venv.sh — one-shot local Python environment setup for AILIT_TRAVEL.
#
# Usage (run once, from repo root):
#   bash setup_venv.sh
#
# Creates a .venv/, upgrades pip, installs requirements.txt, prints next step.
# Idempotent: rerunning only re-installs missing packages.

set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_DIR=".venv"

if ! command -v "$PYTHON" >/dev/null 2>&1; then
  echo "[error] python3 not found. Install Python 3.11+ first." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "[setup] creating virtual environment in $VENV_DIR/"
  "$PYTHON" -m venv "$VENV_DIR"
fi

# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

echo "[setup] upgrading pip / wheel / setuptools"
python -m pip install --upgrade pip wheel setuptools -q

echo "[setup] installing requirements.txt"
pip install -r requirements.txt -q

echo ""
echo "[done] environment ready."
echo "       Activate with:  source $VENV_DIR/bin/activate"
echo "       Next step:      bash run_pdf_to_text.sh"
