# AI‑Agents‑Demo

A production‑style, dockerized AI Agent demo showcasing a FastAPI worker with local RAG (embeddings), multi‑LLM backends (OpenAI + Ollama), and an MCP‑style tool server — designed for clean local runs, VS Code development, and a simple smoke test.

---

## What This Demonstrates
- Containerized AI micro‑stack you can run end‑to‑end with `docker compose up --build`.
- Retrieval‑Augmented Generation over a local Markdown knowledge base.
- Pluggable LLM backends: OpenAI (default) or Ollama.
- MCP‑style tool calling via a lightweight FastAPI service.
- A tidy repo layout that works well with VS Code.

---

## Architecture Overview
- `ai-worker` (FastAPI, port 8000)
  - `/health` — liveness probe
  - `/v1/assist` — RAG + optional tool calls + LLM synthesis
  - Mounts `ai-worker/data` for local Markdown knowledge
  - Uses `sentence-transformers` (`all-MiniLM-L6-v2`) for embeddings
- `mcp-server` (FastAPI, port 9000)
  - `/tool` — MCP‑style endpoint supporting `system_info`
  - Returns `platform`, `cpu_percent`, `memory_percent`
- `postgres` (Port 5432)
  - Placeholder for future persistence (pgvector, traces, etc.). Not required by the demo today.

Networking: Containers share a compose network; `ai-worker` calls the MCP server at `http://mcp-server:9000/tool`.

---

## How RAG Works Here
- All Markdown files in `ai-worker/data/knowledge_base/` are loaded at startup.
- Entire documents are embedded with `all-MiniLM-L6-v2`.
- Query embeddings are compared via cosine similarity.
- Top‑K (default 3) results are returned with a 300‑char snippet for context.
- The context is prepended to the user prompt for the LLM backend.

You can add or update `.md` files in that directory and restart `ai-worker` to refresh the in‑memory index.

---

## MCP‑Style Tools
The `mcp-server` exposes a single example tool:
- `system_info`: returns basic system telemetry to demonstrate tool‑augmented prompts.

The `ai-worker` auto‑invokes:
- `list_kb_files` if the user prompt contains “list docs”.
- `system_info` if the user prompt contains “analyze system”.

Tool calls are captured in a simple `tool_trace` array in the API response.

---

## Getting Started

1) Copy environment variables
```
cp .env.example .env
```
Edit `.env` as needed. Important variables:
- `OPENAI_API_KEY` (required for OpenAI mode)
- `OPENAI_MODEL` (e.g., `gpt-4o-mini`)
- `OLLAMA_BASE_URL` (if using Ollama; e.g., `http://localhost:11434` or `http://ollama:11434`)

2) Build and run
```
docker compose up --build
```

3) Verify health
```
curl http://localhost:8000/health
```

---

## Example Requests

OpenAI mode (requires `OPENAI_API_KEY`):
```
curl -X POST http://localhost:8000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"Analyze system performance and list docs","mode":"openai"}'
```

Ollama mode (requires a running Ollama with `llama3` model available):
```
curl -X POST http://localhost:8000/v1/assist \
  -H "Content-Type: application/json" \
  -d '{"message":"What does onboarding recommend for week 1?","mode":"ollama"}'
```

Tip: To use a host‑running Ollama from inside Docker on macOS/Windows, set `OLLAMA_BASE_URL=http://host.docker.internal:11434` in `.env`.

---

## Smoke Test

After the stack is up:
```
./scripts/smoke_test.sh
```
This exercises `/health` and a sample `/v1/assist` call. If you haven’t set `OPENAI_API_KEY`, the request may fail — switch to `"mode":"ollama"` or set the key.

---

## Demo Flow (Live Presentation)
- Introduce the architecture (3 services) and show `docker-compose.yml`.
- Show the knowledge base in `ai-worker/data/knowledge_base/` and explain RAG.
- Run `./scripts/smoke_test.sh` to confirm health and a basic assist call.
- Prompt ideas:
  - “List docs and analyze system performance” (triggers tool calls).
  - “How do I run the stack locally?” (pulls from `onboarding.md`).
  - “What’s the incident response template?” (pulls from `incident_template.md`).
- Flip between `mode: "openai"` and `mode: "ollama"` to highlight backend portability.
- Discuss extensions: chunked RAG, pgvector in Postgres, richer MCP tools.

---

## Repository Layout
```
.
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── ai-worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── rag.py
│   │   ├── llm.py
│   │   ├── tools.py
│   │   └── schemas.py
│   └── data/
│       └── knowledge_base/
│           ├── onboarding.md
│           ├── incident_template.md
│           └── project_notes.md
├── mcp-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
└── scripts/
    └── smoke_test.sh
```

---

## Troubleshooting
- Build takes a while: The first run downloads Python wheels and the embedding model.
- 500 from `/v1/assist` on OpenAI mode: Ensure `OPENAI_API_KEY` and `OPENAI_MODEL` are set.
- Ollama connection errors: Verify `OLLAMA_BASE_URL` is reachable from inside the container.
- Missing `.env` error in compose: Ensure you created `.env` (see Getting Started).

