#!/bin/bash
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR"

echo 'export PYTHONPATH="."' >> "$CLAUDE_ENV_FILE"

pip install -q -r requirements.txt
pip install -q pytest ruff
