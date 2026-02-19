import os

import requests
from openai import OpenAI

DEFAULT_OLLAMA_MODEL = "llama3.2:1b"
REQUEST_TIMEOUT_SECONDS = 60

class LLMError(Exception):
    def __init__(self, code, message, status_code=500, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def run_openai(prompt, model=None):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    selected_model = (model or os.getenv("OPENAI_MODEL", "")).strip()

    if not api_key:
        raise LLMError(
            code="openai_not_configured",
            message="OPENAI_API_KEY is not set",
            status_code=400,
        )
    if not selected_model:
        raise LLMError(
            code="openai_model_not_configured",
            message="OPENAI_MODEL is not set",
            status_code=400,
        )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise LLMError(
            code="openai_request_failed",
            message="OpenAI request failed",
            status_code=502,
            details={"reason": str(exc)},
        ) from exc

def run_ollama(prompt, model=None):
    base_url = os.getenv("OLLAMA_BASE_URL", "").rstrip("/")
    selected_model = (model or os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL).strip()

    if not base_url:
        raise LLMError(
            code="ollama_not_configured",
            message="OLLAMA_BASE_URL is not set",
            status_code=400,
        )
    if not selected_model:
        raise LLMError(
            code="ollama_model_not_configured",
            message="OLLAMA_MODEL is not set",
            status_code=400,
        )

    try:
        response = requests.post(
            f"{base_url}/api/generate",
            json={"model": selected_model, "prompt": prompt, "stream": False},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(
            code="ollama_request_failed",
            message="Ollama request failed",
            status_code=502,
            details={"reason": str(exc), "base_url": base_url, "model": selected_model},
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise LLMError(
            code="ollama_invalid_json",
            message="Ollama returned non-JSON response",
            status_code=502,
            details={"response_text": response.text[:300]},
        ) from exc

    return payload.get("response", "")
