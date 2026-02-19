from pydantic import BaseModel
from typing import List, Dict

class AssistRequest(BaseModel):
    message: str
    mode: str = "openai"
    top_k: int = 3

class RetrievedDoc(BaseModel):
    source: str
    score: float
    snippet: str

class AssistResponse(BaseModel):
    request_id: str
    retrieved: List[RetrievedDoc]
    output: Dict

