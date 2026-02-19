# Engineering Onboarding Guide

Welcome to the AI Agents team! This document outlines the fastest way to become productive in this repository and in our production‑style demo stack.

## Goals for Week 1
- Ship your first change to the demo stack (docs or code).
- Run the full environment with `docker compose up --build`.
- Understand the RAG data flow and how to add new knowledge.

## Local Environment
- Prereqs: Docker Desktop (or Docker Engine), `curl`.
- Optional: Python 3.11 for running services locally without Docker.
- IDE: VS Code with Python and Docker extensions.

## Services Overview
- ai-worker (FastAPI): Hosts `/health` and `/v1/assist`. Performs RAG retrieval + LLM calls.
- mcp-server (FastAPI): Simple MCP‑style tool endpoint `/tool` with `system_info`.
- postgres: Placeholder DB for future persistence (not required for the demo).

## Development Workflow
1. Copy `.env.example` to `.env` and fill values as needed.
2. Start stack: `docker compose up --build`.
3. Verify health: `curl http://localhost:8000/health`.
4. Run smoke test: `scripts/smoke_test.sh`.

## Adding Knowledge for RAG
- Place Markdown files in `ai-worker/data/knowledge_base/`.
- Keep content factual and concise. Use headings and bullet lists.
- The RAG component embeds full file text and returns ~300‑char snippets.

## Code Style
- Python 3.11.
- Keep modules small and readable.
- Prefer explicit names and docstrings on non‑trivial functions.

## Common Issues
- Missing `.env`: The `ai-worker` service uses `env_file: .env`. Ensure it exists.
- No OpenAI key: Use `mode=ollama` or set `OPENAI_API_KEY` and `OPENAI_MODEL`.
- Model download time: The first startup downloads `all-MiniLM-L6-v2`.

## Support
- Open a GitHub issue with logs and reproduction steps.
- Share `docker compose` service logs and your `.env` (with secrets redacted).

