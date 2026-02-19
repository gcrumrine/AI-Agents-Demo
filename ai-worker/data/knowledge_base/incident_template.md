# Incident Template (P0/P1)

Use this template during live incidents to capture the essential details. Keep updates timestamped and factual. This format enables fast post‑mortems and trains the RAG system with useful operational knowledge.

## Summary
- Severity: P0 | P1 | P2
- Impact: User‑facing | Internal only
- Duration: <start> to <end> (UTC)
- Services: ai-worker | mcp-server | postgres | external LLM

## Timeline (UTC)
- T0 — Detection: Who/what raised the alert? Pager/Logs/User.
- T+5m — Initial triage: Hypothesis and immediate mitigations.
- T+15m — Escalations: Who joined, what changed.
- T+30m — Mitigation: Actions taken and observed outcomes.
- T+60m — Status: Current blast radius and user comms.

## Key Metrics
- ai-worker 5xx rate:
- mcp-server latency (p95):
- Token usage spikes (OpenAI/Ollama):
- CPU/Memory utilization:

## Root Cause Analysis
- Primary cause:
- Contributing factors:
- Why detection didn’t happen sooner:
- Why it took time to mitigate:

## Remediation Actions
- Short‑term fixes:
- Long‑term fixes:
- Test and automation gaps:

## Artifacts
- Links to dashboards, logs, PRs:
- Representative requests/responses (sanitized):

## Lessons Learned
- What worked well:
- What to change for next time:

