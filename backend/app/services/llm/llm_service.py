"""
LLM abstraction layer.

Swap providers by changing LLM_BACKEND in .env:
  - "ollama"  → Ollama (local, default)
  - "openai"  → OpenAI API
"""

from abc import ABC, abstractmethod

import httpx

from app.core.config import get_settings

settings = get_settings()


# ── Abstract Interface

class LLMService(ABC):
    @abstractmethod
    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
        """Return the model's text completion."""


# ── Prompt Templates

BOOK_SUMMARY_SYSTEM = (
    "You are a professional librarian and literary analyst. "
    "Your task is to produce concise, informative book summaries. "
    "Focus on themes, writing style, and reader appeal. "
    "Keep your summary under 300 words."
)

REVIEW_CONSENSUS_SYSTEM = (
    "You are a sentiment analyst for a library platform. "
    "Given a list of reader reviews, synthesise a neutral, balanced consensus paragraph "
    "that captures overall sentiment, recurring praise, and common criticisms. "
    "Keep the consensus under 200 words."
)


def build_summary_prompt(title: str, author: str, content_excerpt: str) -> str:
    return (
        f"Book: '{title}' by {author}\n\n"
        f"Content excerpt:\n{content_excerpt[:3000]}\n\n"
        "Write an engaging summary of this book."
    )


def build_review_consensus_prompt(book_title: str, reviews: list[dict]) -> str:
    formatted = "\n".join(
        f"- Rating {r['rating']}/5: {r['body']}" for r in reviews[:30]
    )
    return (
        f"Book: {book_title}\n\n"
        f"Reader reviews:\n{formatted}\n\n"
        "Write a consensus summary of reader sentiment."
    )


#Ollama Implementation

class OllamaLLMService(LLMService):
    def __init__(self) -> None:
        self._base_url = settings.OLLAMA_BASE_URL
        self._model = settings.OLLAMA_MODEL

    async def complete(self, system_prompt: str, user_prompt: str, max_tokens: int = 512) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "stream": False,
                    "options": {"num_predict": max_tokens},
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"]



#Factory

def get_llm_service() -> LLMService:
    """FastAPI dependency – returns the configured LLM backend."""
    backend = settings.LLM_BACKEND
    if backend == "ollama":
        return OllamaLLMService()
    if backend == "openai":
        # Placeholder for future OpenAI implementation
        raise NotImplementedError("OpenAI backend not implemented yet.")
    raise ValueError(f"Unknown LLM_BACKEND: {backend}")

