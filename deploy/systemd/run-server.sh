#!/usr/bin/env bash
set -euo pipefail

cd "${ADPARSER_PROJECT_DIR}"
exec "${ADPARSER_UV}" run uvicorn src.server:app \
  --host 0.0.0.0 \
  --port "${ADPARSER_PORT:-8000}"
