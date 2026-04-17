"""
backend/ollama_client.py
────────────────────────
Core interface to the Ollama API.
Handles model listing, streaming chat, and non-streaming chat.
"""

from __future__ import annotations

import time
from typing import Generator, Iterator

import ollama
from ollama import ResponseError


# ─── Available lightweight models (shown in UI picker) ────────────────────────
RECOMMENDED_MODELS = [
    "llama3.2:3b",
    "llama3.2:1b",
    "mistral:7b",
    "gemma2:2b",
    "phi3:mini",
    "qwen2.5:3b",
    "deepseek-r1:1.5b",
]


# ─── OllamaClient ─────────────────────────────────────────────────────────────

class OllamaClient:
    """
    Thin, stateless wrapper around the `ollama` Python SDK.

    All chat state lives in the caller (Streamlit session_state);
    this class is purely responsible for network calls.
    """

    def __init__(self, host: str = None) -> None:
        import os
        if host is None:
            host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=host, headers={"ngrok-skip-browser-warning": "1"})

    # ── Connectivity ──────────────────────────────────────────────────────────

    def is_running(self) -> bool:
        """Return True if the local Ollama daemon is reachable."""
        try:
            self.client.list()
            return True
        except Exception:
            return False

    # ── Model management ─────────────────────────────────────────────────────

    def list_local_models(self) -> list[str]:
        """Return model tag strings for every model pulled locally."""
        try:
            response = self.client.list()
            return [m.model for m in response.models]
        except Exception:
            return []

    def pull_model(self, model: str) -> Iterator[dict]:
        """
        Pull a model from the Ollama registry.
        Yields progress dicts: {"status": str, "completed": int, "total": int}
        """
        try:
            for progress in self.client.pull(model, stream=True):
                yield {
                    "status": progress.status or "",
                    "completed": progress.completed or 0,
                    "total": progress.total or 0,
                }
        except ResponseError as exc:
            raise RuntimeError(f"Pull failed: {exc}") from exc

    # ── Chat ──────────────────────────────────────────────────────────────────

    def chat_stream(
        self,
        model: str,
        messages: list[dict],
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """
        Send a chat request and stream token chunks back.

        Args:
            model:         Ollama model tag, e.g. "llama3.2:3b"
            messages:      List of {"role": "user"|"assistant", "content": str}
            system_prompt: Optional system message prepended to the conversation.
            temperature:   Sampling temperature (0.0 – 2.0).

        Yields:
            Successive string chunks as they arrive from the model.
        """
        payload = self._build_payload(messages, system_prompt)

        try:
            stream = self.client.chat(
                model=model,
                messages=payload,
                stream=True,
                options={"temperature": temperature},
            )
            for chunk in stream:
                token = chunk.message.content
                if token:
                    yield token
        except ResponseError as exc:
            raise RuntimeError(f"Chat error ({model}): {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected error: {exc}") from exc

    def chat(
        self,
        model: str,
        messages: list[dict],
        system_prompt: str = "",
        temperature: float = 0.7,
    ) -> str:
        """
        Non-streaming chat. Returns the full assistant reply as a string.
        Useful for testing / CLI usage.
        """
        payload = self._build_payload(messages, system_prompt)
        try:
            response = self.client.chat(
                model=model,
                messages=payload,
                options={"temperature": temperature},
            )
            return response.message.content or ""
        except ResponseError as exc:
            raise RuntimeError(f"Chat error ({model}): {exc}") from exc

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _build_payload(
        messages: list[dict], system_prompt: str
    ) -> list[dict]:
        """Prepend the system message (if any) to the messages list."""
        payload: list[dict] = []
        if system_prompt.strip():
            payload.append({"role": "system", "content": system_prompt.strip()})
        payload.extend(messages)
        return payload
