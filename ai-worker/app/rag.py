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

