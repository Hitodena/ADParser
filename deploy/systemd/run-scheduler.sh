#!/usr/bin/env bash
set -euo pipefail

cd "${ADPARSER_PROJECT_DIR}"

args=(
  run python main.py
  -u "${ADPARSER_USERNAME}"
  -p "${ADPARSER_PASSWORD}"
  -o "${ADPARSER_OUTPUT:-output.csv}"
  --scheduled
  --time "${ADPARSER_SCHEDULE_TIME:-02:00}"
  --headless
)

if [[ "${ADPARSER_WAREHOUSE:-0}" == "1" ]]; then
  args+=(
    -w
    -ow "${ADPARSER_OUTPUT_WAREHOUSE:-warehouse.csv}"
  )
fi

exec "${ADPARSER_UV}" "${args[@]}"
