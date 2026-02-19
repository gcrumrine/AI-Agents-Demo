#!/bin/bash

set -euo pipefail

echo "==> Checking health"
curl -sS http://localhost:8000/health | jq . || curl -sS http://localhost:8000/health
echo

echo "==> Calling /v1/assist (OpenAI mode)"
curl -sS -X POST http://localhost:8000/v1/assist \
-H "Content-Type: application/json" \
-d '{"message": "Analyze system performance and list docs", "mode": "openai"}' | jq . || true
echo

