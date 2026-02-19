import os
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.schemas import AssistRequest
from app.rag import retrieve
from app.llm import DEFAULT_OLLAMA_MODEL, LLMError, run_openai, run_ollama
from app.tools import list_kb_files, call_mcp_tool

app = FastAPI()


@app.exception_handler(LLMError)
def handle_llm_error(_: Request, exc: LLMError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


def resolve_mode(requested_mode: str) -> str:
    if requested_mode != "auto":
        return requested_mode
    return "openai" if os.getenv("OPENAI_API_KEY", "").strip() else "rag_only"


def run_rag_only(message: str, retrieved_docs, tool_trace) -> str:
    summary_lines = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        snippet = " ".join(doc["snippet"].strip().split())
        summary_lines.append(f"{idx}. [{doc['source']}] {snippet[:180]}")

    if not summary_lines:
        summary_lines.append("1. No matching knowledge-base documents were retrieved.")

    tool_lines = []
    for event in tool_trace:
        tool = event.get("tool", "unknown_tool")
        result = event.get("result", {})
        if tool == "system_info":
            cpu = result.get("cpu_percent", "n/a")
            mem = result.get("memory_percent", "n/a")
            plat = result.get("platform", "n/a")
            tool_lines.append(f"- system_info -> platform={plat}, cpu={cpu}%, memory={mem}%")
        else:
            tool_lines.append(f"- {tool} -> {result}")

    if not tool_lines:
        tool_lines.append("- No tools were invoked for this prompt.")

    return "\n".join(
        [
            "RAG-only response (safe default when OpenAI is not configured).",
            "",
            "Summary:",
            *summary_lines,
            "",
            "Tool Observations:",
            *tool_lines,
            "",
            "Next Steps:",
            "- Add OPENAI_API_KEY to enable OpenAI synthesis.",
            "- Or call mode=\"ollama\" to use the local Ollama container.",
        ]
    )


@app.get("/health")
def health():
    default_mode = resolve_mode("auto")
    return {
        "status": "ok",
        "default_mode": default_mode,
        "openai_configured": default_mode == "openai",
    }

@app.post("/v1/assist")
def assist(req: AssistRequest):
    request_id = str(uuid.uuid4())
    retrieved_docs = retrieve(req.message, req.top_k)
    tool_trace = []

    if "list docs" in req.message.lower():
        files = list_kb_files()
        tool_trace.append({"tool": "list_kb_files", "result": files})

    if "analyze system" in req.message.lower():
        result = call_mcp_tool("system_info", {})
        tool_trace.append({"tool": "system_info", "result": result})

    context = "\n\n".join([doc["snippet"] for doc in retrieved_docs])
    full_prompt = f"""
Context:
{context}

User Question:
{req.message}

Respond with:
- Summary
- Action Items
- Risks
- Next Steps
"""

    selected_mode = resolve_mode(req.mode)
    selected_model = req.model

    if selected_mode == "openai":
        output = run_openai(full_prompt, model=req.model)
        selected_model = req.model or os.getenv("OPENAI_MODEL")
    elif selected_mode == "ollama":
        output = run_ollama(full_prompt, model=req.model)
        selected_model = req.model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    elif selected_mode == "rag_only":
        output = run_rag_only(req.message, retrieved_docs, tool_trace)
        selected_model = None
    else:
        raise LLMError(
            code="unsupported_mode",
            message=f"Unsupported mode: {selected_mode}",
            status_code=400,
            details={"supported_modes": ["auto", "openai", "ollama", "rag_only"]},
        )

    return {
        "request_id": request_id,
        "requested_mode": req.mode,
        "mode": selected_mode,
        "model": selected_model,
        "retrieved": retrieved_docs,
        "output": output,
        "tool_trace": tool_trace
    }
