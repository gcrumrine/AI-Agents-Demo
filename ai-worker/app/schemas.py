from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

class AssistRequest(BaseModel):
    message: str
    mode: Literal["auto", "openai", "ollama", "rag_only"] = "auto"
    model: Optional[str] = None
    top_k: int = 3

class RetrievedDoc(BaseModel):
    source: str
    score: float
    snippet: str

class AssistResponse(BaseModel):
    request_id: str
    retrieved: List[RetrievedDoc]
    output: str
    mode: str
    requested_mode: str
    model: Optional[str]
    tool_trace: List[Dict[str, Any]]
