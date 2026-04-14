from __future__ import annotations

import requests

LM_STUDIO_CHAT_URL = "http://localhost:1234/v1/chat/completions"
LM_STUDIO_MODEL = "local-model"


def _call_llm(prompt: str, max_tokens: int = 220) -> str:
    try:
        response = requests.post(
            LM_STUDIO_CHAT_URL,
            json={
                "model": LM_STUDIO_MODEL,
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": "You are a concise literary analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except (requests.RequestException, KeyError, IndexError, TypeError, ValueError):
        return ""


def generate_summary(description: str, existing_summary: str = "") -> str:
    if existing_summary.strip():
        return existing_summary
    prompt = (
        "Write exactly three sentences summarizing this book description:\n\n"
        f"{description}"
    )
    summary = _call_llm(prompt, max_tokens=180)
    if summary:
        return summary
    # Fallback keeps upload flow working even when LM Studio is unavailable.
    text = (description or "").strip()
    if not text:
        return "Summary unavailable."
    shortened = text[:420].strip()
    return f"{shortened}." if not shortened.endswith(".") else shortened


def classify_genre(description: str, existing_genre: str = "") -> str:
    if existing_genre.strip():
        return existing_genre
    prompt = (
        "Return exactly one genre word for this book. "
        "Examples: fantasy, thriller, romance, history, science, mystery.\n\n"
        f"{description}"
    )
    genre = _call_llm(prompt, max_tokens=12)
    if genre:
        return genre.split()[0].strip(".,;:").lower()
    return "unknown"
