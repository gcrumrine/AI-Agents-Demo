#!/bin/bash
set -euo pipefail

AI="${AI_URL:-http://localhost:18000}"
OPENAI_MODEL_VALUE="${OPENAI_MODEL:-gpt-4o-mini}"

if [[ ! -f .env ]] || ! awk -F= '$1=="OPENAI_API_KEY" && length($2)>0 {found=1} END{exit(found?0:1)}' .env; then
  echo "OPENAI_API_KEY is not set in .env. Skipping OpenAI smoke test."
  exit 0
fi

echo "==> openai mode (model=${OPENAI_MODEL_VALUE})"
curl -sS -X POST "$AI/v1/assist" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Analyze system performance and list docs. Give 2 specific action items.\",\"mode\":\"openai\",\"model\":\"${OPENAI_MODEL_VALUE}\",\"top_k\":3}" \
  | (command -v jq >/dev/null && jq || cat)
echo
