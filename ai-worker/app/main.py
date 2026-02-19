import uuid
from fastapi import FastAPI
from app.schemas import AssistRequest
from app.rag import retrieve
from app.llm import run_openai, run_ollama
from app.tools import list_kb_files, call_mcp_tool

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

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

    if req.mode == "openai":
        output = run_openai(full_prompt)
    else:
        output = run_ollama(full_prompt)

    return {
        "request_id": request_id,
        "retrieved": retrieved_docs,
        "output": output,
        "tool_trace": tool_trace
    }

