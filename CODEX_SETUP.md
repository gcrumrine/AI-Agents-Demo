# AI-Agents-Demo: Full Repository Build Instructions

You are Codex operating in a fresh clone of:

https://github.com/gcrumrine/AI-Agents-Demo.git

Your task is to generate the full working repository for a production-style AI Agent demo with:

- Dockerized architecture
- FastAPI AI Worker
- RAG (local embeddings)
- OpenAI + Ollama support
- MCP-style tool server
- Clean structure for VSCode usage
- Smoke test script
- Example knowledge base docs

This must be fully runnable with:

docker compose up --build

---

# REQUIRED PROJECT STRUCTURE

Create the following structure exactly:

AI-Agents-Demo/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
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
│
├── mcp-server/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── server.py
│
└── scripts/
    └── smoke_test.sh

---

# FILE CONTENTS

---

## .gitignore

```
__pycache__/
*.pyc
.env
.env.*
node_modules/
.vscode/
.idea/
.DS_Store
```

---

## .env.example

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
OLLAMA_BASE_URL=http://ollama:11434

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=ai_agents
```

---

## docker-compose.yml

```
version: "3.9"

services:
  ai-worker:
    build: ./ai-worker
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./ai-worker/data:/app/data
    depends_on:
      - mcp-server

  mcp-server:
    build: ./mcp-server
    ports:
      - "9000:9000"

  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    ports:
      - "5432:5432"
```

---

# AI WORKER

---

## ai-worker/requirements.txt

```
fastapi
uvicorn
pydantic
sentence-transformers
numpy
scikit-learn
requests
openai
```

---

## ai-worker/Dockerfile

```
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ai-worker/app/schemas.py

```
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
```

---

## ai-worker/app/rag.py

```
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

KB_PATH = "data/knowledge_base"

def load_documents():
    docs = []
    for file in os.listdir(KB_PATH):
        if file.endswith(".md"):
            with open(os.path.join(KB_PATH, file), "r") as f:
                content = f.read()
                docs.append({"source": file, "text": content})
    return docs

documents = load_documents()
embeddings = model.encode([doc["text"] for doc in documents])

def retrieve(query, top_k=3):
    query_embedding = model.encode([query])
    scores = cosine_similarity(query_embedding, embeddings)[0]
    ranked = sorted(
        zip(documents, scores), key=lambda x: x[1], reverse=True
    )[:top_k]

    return [
        {
            "source": doc["source"],
            "score": float(score),
            "snippet": doc["text"][:300]
        }
        for doc, score in ranked
    ]
```

---

## ai-worker/app/tools.py

```
import os
import requests

def list_kb_files():
    return os.listdir("data/knowledge_base")

def call_mcp_tool(tool_name, payload):
    response = requests.post(
        "http://mcp-server:9000/tool",
        json={"tool": tool_name, "payload": payload}
    )
    return response.json()
```

---

## ai-worker/app/llm.py

```
import os
from openai import OpenAI
import requests

def run_openai(prompt):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def run_ollama(prompt):
    response = requests.post(
        f"{os.getenv('OLLAMA_BASE_URL')}/api/generate",
        json={"model": "llama3", "prompt": prompt}
    )
    return response.json().get("response", "")
```

---

## ai-worker/app/main.py

```
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
```

---

# MCP SERVER

---

## mcp-server/requirements.txt

```
fastapi
uvicorn
psutil
platformdirs
```

---

## mcp-server/Dockerfile

```
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY server.py .
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9000"]
```

---

## mcp-server/server.py

```
from fastapi import FastAPI
import platform
import psutil

app = FastAPI()

@app.post("/tool")
def run_tool(request: dict):
    tool = request.get("tool")

    if tool == "system_info":
        return {
            "platform": platform.system(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent
        }

    return {"error": "unknown tool"}
```

---

# KNOWLEDGE BASE FILE CONTENT

Populate realistic deployment and incident info inside:

- onboarding.md
- incident_template.md
- project_notes.md

Make content meaningful so RAG visibly works.

---

# scripts/smoke_test.sh

```
#!/bin/bash

curl http://localhost:8000/health

curl -X POST http://localhost:8000/v1/assist \
-H "Content-Type: application/json" \
-d '{"message": "Analyze system performance and list docs", "mode": "openai"}'
```

Make script executable.

---

# README.md REQUIREMENTS

Write a polished README explaining:

1. What this project demonstrates
2. Architecture overview
3. How RAG works here
4. How MCP-style tools work
5. How to run it
6. Example curl commands
7. Demo flow instructions for a live presentation

Make it professional and clean.

---

# FINAL INSTRUCTION

Generate all files.
Ensure indentation and YAML formatting are correct.
Ensure docker compose builds successfully.
Do not leave placeholder text.
Make everything runnable.

End of instructions.
