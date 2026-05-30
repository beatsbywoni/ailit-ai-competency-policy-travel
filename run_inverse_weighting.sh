#!/usr/bin/env bash
# run_inverse_weighting.sh — Sprint 1 robustness IV.2 wrapper.
#
# Sources venv, runs inverse_corpus_weighting.py against the v2 active anchor
# alignment by default. Override with --tag v1 to run on the archived anchors.
#
# Usage:
#   bash run_inverse_weighting.sh                 # v2 default (active)
#   bash run_inverse_weighting.sh --tag v1        # v1 archived comparison
#   bash run_inverse_weighting.sh --tag v2        # explicit

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

# default to v2 if --tag is not provided
HAS_TAG=0
for arg in "$@"; do
  [ "$arg" = "--tag" ] && HAS_TAG=1
done

if [ "$HAS_TAG" -eq 0 ]; then
  set -- --tag v2 "$@"
fi

"$PY" scripts/04_robustness/inverse_corpus_weighting.py "$@"
