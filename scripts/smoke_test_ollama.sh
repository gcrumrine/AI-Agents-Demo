#!/bin/bash
set -euo pipefail

AI="${AI_URL:-http://localhost:18000}"
OLLAMA_MODEL_VALUE="${OLLAMA_MODEL:-llama3.2:1b}"

echo "==> ensuring ollama model is available (model=${OLLAMA_MODEL_VALUE})"
if command -v docker >/dev/null 2>&1; then
  docker compose exec -T ollama ollama pull "${OLLAMA_MODEL_VALUE}" >/dev/null
else
  echo "docker command not found; continuing without model pull"
fi

echo "==> ollama mode (model=${OLLAMA_MODEL_VALUE})"
curl -sS -X POST "$AI/v1/assist" \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"Analyze system performance and list docs. Call out one concrete risk and one next step.\",\"mode\":\"ollama\",\"model\":\"${OLLAMA_MODEL_VALUE}\",\"top_k\":3}" \
  | (command -v jq >/dev/null && jq || cat)
echo
