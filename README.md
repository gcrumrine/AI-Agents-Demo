# AI-Agents-Demo

A dockerized AI-agent demo with a FastAPI worker, local RAG over Markdown docs, an MCP-style tool server, and two LLM backends (OpenAI + Ollama).

## What this demonstrates
- End-to-end local stack with `docker compose up --build`
- Retrieval-Augmented Generation (RAG) from local knowledge-base files
- Tool-augmented responses via MCP-style server calls
- Runtime model/backend switching between OpenAI and Ollama
- A safe default mode for reproducible demos

## Terms used in this repo
- `RAG` = Retrieval-Augmented Generation: retrieve relevant local docs first, then ground the response with that context.
- `MCP` = Model Context Protocol: a standardized way for agents/models to call tools and external capabilities.

## You need these prereqs
1. Docker with Compose support
- macOS/Windows: install Docker Desktop: https://docs.docker.com/desktop/
- Linux: install Docker Engine + Docker Compose plugin: https://docs.docker.com/engine/install/
- Verify with `docker --version` and `docker compose version`

2. Git
- Install from https://git-scm.com/downloads
- Verify with `git --version`

3. `curl` and `jq` (for test commands)
- macOS (Homebrew): `brew install curl jq`
- Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y curl jq`
- Verify with `curl --version` and `jq --version`

4. Optional OpenAI API key (only for OpenAI mode)
- Create API key: https://platform.openai.com/api-keys
- If unset, safe default mode automatically falls back to `rag_only`

## Safe default mode behavior
`/v1/assist` defaults to `mode: "auto"`.

- If `OPENAI_API_KEY` is set: default resolved mode is `openai`
- If `OPENAI_API_KEY` is missing: default resolved mode is `rag_only`

This keeps the demo usable in fresh clones without forcing cloud keys.

## Architecture
- `ai-worker` (FastAPI, container port `8000`, host port `18000`)
  - `GET /health`
  - `POST /v1/assist`
  - Performs RAG retrieval, optional tool calls, and synthesis
- `mcp-server` (FastAPI, container port `9000`, host port `19000`)
  - `POST /tool`
  - Includes `system_info` demo tool
- `ollama` (Ollama, port `11434`)
  - Local model runtime for offline-ish local inference
- `ollama-init` (one-shot helper)
  - Pulls `OLLAMA_MODEL` automatically on startup
- `postgres` (container port `5432`, host port `15432`)
  - Placeholder for future persistence/tracing

## Quick start
1. Copy env file
```bash
cp .env.example .env
```

2. Optional: set OpenAI key (if you want OpenAI mode)
```bash
# edit .env
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini
```

3. Build and run
```bash
docker compose up --build
```

4. Health check
```bash
curl -sS http://localhost:18000/health | jq
```

Host ports intentionally use `18000`, `19000`, and `15432` to reduce collisions with other local services that often bind to default ports.

## Model and mode selection
Request fields:
- `mode`: `auto` | `openai` | `ollama` | `rag_only`
- `model`: optional model override for selected backend

Defaults:
- OpenAI model from `OPENAI_MODEL`
- Ollama model from `OLLAMA_MODEL` (default: `llama3.2:1b`)

### Safe default request (recommended for demos)
```bash
curl -sS -X POST http://localhost:18000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze system performance and list docs","top_k":3}' | jq
```

### Force OpenAI mode
```bash
curl -sS -X POST http://localhost:18000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize onboarding in 3 bullets","mode":"openai","model":"gpt-4o-mini"}' | jq
```

### Force Ollama mode
```bash
curl -sS -X POST http://localhost:18000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"Summarize onboarding in 3 bullets","mode":"ollama","model":"llama3.2:1b"}' | jq
```

### Force deterministic fallback (no LLM calls)
```bash
curl -sS -X POST http://localhost:18000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze system performance and list docs","mode":"rag_only"}' | jq
```

## Smoke tests
After the stack is running:

```bash
./scripts/smoke_test.sh
```
- Uses safe default mode (`auto`) to avoid hard failures in fresh clones

```bash
./scripts/smoke_test_openai.sh
```
- Explicit OpenAI test (skips if `OPENAI_API_KEY` is not set)

```bash
./scripts/smoke_test_ollama.sh
```
- Explicit Ollama test
- Ensures selected Ollama model is pulled before request

These separate tests let you quickly swap back and forth between OpenAI and Ollama during demos.

## "Something cool" demo prompts
Use prompts that trigger both retrieval and tools:
- `"Analyze system performance and list docs. Also summarize deployment process."`
- `"List docs and call out incident-response risks."`

You will see:
- `retrieved` docs with similarity-ranked snippets
- `tool_trace` entries (for `system_info` and KB listing)
- `mode` and `model` used for the response

## Why this is useful
- Shows how to keep agent demos resilient when API credentials are absent
- Demonstrates backend portability without changing business logic
- Gives a practical pattern for combining RAG + tool calls + LLM synthesis
- Helps teams prototype production agent patterns with reproducible local infra

## Repository layout
```text
.
├── README.md
├── docker-compose.yml
├── .env.example
├── ai-worker/
│   ├── app/
│   │   ├── main.py
│   │   ├── llm.py
│   │   ├── rag.py
│   │   ├── tools.py
│   │   └── schemas.py
│   └── data/knowledge_base/
├── mcp-server/
└── scripts/
    ├── smoke_test.sh
    ├── smoke_test_openai.sh
    └── smoke_test_ollama.sh
```

## Troubleshooting
- `ollama_request_failed`: make sure compose stack is up and `ollama` is healthy
- OpenAI 400 config errors: set `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`
- First run is slow: embeddings/model downloads happen on initial startup

## Next improvements (multi-agent + skills + MCP)
1. Multi-agent coordinator service
- Add an `agent-orchestrator` service that routes work to specialized agents (`research`, `planner`, `executor`) and merges outputs.
- Persist per-agent traces in Postgres for replay/debugging.

2. Tool/skill registry
- Add a registry file for tools and skills with capability metadata (`input schema`, `cost`, `latency`, `risk level`).
- Let the worker select tools dynamically based on user intent and policy.

3. MCP server expansion
- Split tools into multiple MCP servers (`filesystem`, `tickets`, `monitoring`, `knowledge`).
- Use Docker Compose profiles to run only required MCP servers per scenario.

4. Docker Desktop integration
- Publish compose profiles and healthchecks so developers can toggle stacks visually in Docker Desktop.
- Use Desktop extensions or local integrations for logs, traces, and container resource monitoring during demos.

5. Safer production posture
- Add auth between worker and MCP servers.
- Add rate limits, request validation, and PII-safe logging policies.
