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

