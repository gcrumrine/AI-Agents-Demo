#!/bin/bash
set -euo pipefail

AI="${AI_URL:-http://localhost:18000}"
MCP="${MCP_URL:-http://localhost:19000}"

echo "==> health"
curl -sS "$AI/health" | (command -v jq >/dev/null && jq || cat)
echo

echo "==> mcp tool"
curl -sS -X POST "$MCP/tool" \
  -H "Content-Type: application/json" \
  -d '{"tool":"system_info","payload":{}}' | (command -v jq >/dev/null && jq || cat)
echo

echo "==> assist (safe default: openai if OPENAI_API_KEY is set, otherwise rag_only)"
curl -sS -X POST "$AI/v1/assist" \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze system performance and list docs. Also summarize our deployment process with source references.","top_k":3}' | (command -v jq >/dev/null && jq || cat)
echo
