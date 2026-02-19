# Project Notes: AI Agents Demo

These notes capture practical decisions and operational tips that help during demos and day‑to‑day development.

## Architecture Highlights
- Dockerized micro‑stack with isolated services and clear boundaries.
- FastAPI ai-worker exposes `/v1/assist` which:
  - Retrieves top‑K relevant snippets from local Markdown docs (RAG).
  - Optionally calls MCP‑style tools for environment/system context.
  - Synthesizes a structured answer via OpenAI or Ollama.
- MCP server offers a `system_info` tool (platform, CPU%, memory%) to simulate tool calling.

## RAG Details
- Embeddings model: `all-MiniLM-L6-v2` via `sentence-transformers`.
- Similarity: cosine similarity over document‑level vectors.
- Retrieval unit: Entire files; future improvement could split by sections.
- Snippet size: first 300 characters of each top hit.

## LLM Backends
- OpenAI: set `OPENAI_API_KEY` and `OPENAI_MODEL` in `.env`.
- Ollama: set `OLLAMA_BASE_URL` (default `http://ollama:11434`) and ensure a `llama3` model is available.
- Switch backends via request field `"mode": "openai"` or `"mode": "ollama"`.

## Common Demo Flow
1. Ask to “list docs” to demonstrate tool usage and KB visibility.
2. Ask to “analyze system performance” to invoke the MCP server tool.
3. Ask an onboarding question (e.g., “How do I run the stack?”) to show RAG snippets.

## Future Enhancements
- Chunking + per‑chunk embeddings for finer retrieval.
- Persistent vector DB (e.g., pgvector) using `postgres` service.
- Additional MCP tools: file I/O, HTTP fetch, time, shell commands (scoped).
- Streaming responses and tool traces in the API.

