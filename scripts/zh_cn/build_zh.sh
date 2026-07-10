#!/usr/bin/env bash
# Usage:
#   bash scripts/zh_cn/build_zh.sh
#
# Build the Simplified Chinese futurecoder course data.
#
# Prerequisites:
#   - Python 3.12.1
#   - Poetry with project dependencies installed (`poetry install`)
#   - Node.js/npm dependencies installed separately under `frontend/`

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PO_FILE="$ROOT_DIR/translations/locales/zh/LC_MESSAGES/futurecoder.po"
MO_FILE="$ROOT_DIR/translations/locales/zh/LC_MESSAGES/futurecoder.mo"

cd "$ROOT_DIR"

if ! command -v poetry >/dev/null 2>&1; then
  echo "ERROR: poetry is not installed or not available in PATH." >&2
  exit 1
fi

if [[ ! -f "$PO_FILE" ]]; then
  echo "ERROR: Chinese PO file not found: $PO_FILE" >&2
  exit 1
fi

echo "[1/3] Checking Chinese translations and compiling futurecoder.mo..."
poetry run python scripts/zh_cn/check_po_placeholders.py "$PO_FILE" --compile

if [[ ! -f "$MO_FILE" ]]; then
  echo "ERROR: MO compilation did not produce: $MO_FILE" >&2
  exit 1
fi

echo "[2/3] Generating Chinese frontend course data..."
FIX_CORE_IMPORTS=1 \
FUTURECODER_LANGUAGE=zh \
poetry run python -m scripts.generate_static_files

echo "[3/3] Chinese build completed."
echo
echo "Next commands:"
echo "  cd frontend"
echo "  npm ci                 # only needed for first install or lockfile changes"
echo "  npm start"
echo
echo "Then open: http://localhost:3000/course/"
