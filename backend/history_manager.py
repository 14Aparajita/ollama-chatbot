"""
backend/history_manager.py
──────────────────────────
Handles saving and loading chat sessions to/from disk (JSON).

Each session is stored as a single .json file inside  data/chats/.
Schema per file:
{
    "id":         "20240415_143022",      # session ID = timestamp
    "title":      "First message preview",
    "model":      "llama3.2:3b",
    "system":     "You are a helpful assistant.",
    "created_at": "2024-04-15T14:30:22",
    "updated_at": "2024-04-15T14:35:10",
    "messages": [
        {"role": "user",      "content": "Hello"},
        {"role": "assistant", "content": "Hi! How can I help?"}
    ]
}
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─── Constants ────────────────────────────────────────────────────────────────

DATA_DIR = Path(__file__).parent.parent / "data" / "chats"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TITLE_MAX_LEN = 60  # chars to use for auto-generated title


# ─── HistoryManager ───────────────────────────────────────────────────────────

class HistoryManager:
    """
    Manages persistent chat sessions on the local filesystem.
    All methods are static/class-level — no instance state needed.
    """

    # ── Session lifecycle ─────────────────────────────────────────────────────

    @classmethod
    def new_session_id(cls) -> str:
        """Generate a unique session ID based on the current timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    @classmethod
    def save_session(
        cls,
        session_id: str,
        messages: list[dict],
        model: str,
        system_prompt: str = "",
        title: Optional[str] = None,
    ) -> None:
        """
        Persist a chat session to disk.
        Creates or overwrites  data/chats/<session_id>.json.
        """
        path = DATA_DIR / f"{session_id}.json"

        # Auto-generate title from first user message if not provided
        if not title:
            title = cls._auto_title(messages)

        # Preserve created_at if file already exists
        created_at = datetime.now().isoformat()
        if path.exists():
            try:
                existing = json.loads(path.read_text(encoding="utf-8"))
                created_at = existing.get("created_at", created_at)
            except (json.JSONDecodeError, OSError):
                pass

        session = {
            "id": session_id,
            "title": title,
            "model": model,
            "system": system_prompt,
            "created_at": created_at,
            "updated_at": datetime.now().isoformat(),
            "messages": messages,
        }
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load_session(cls, session_id: str) -> Optional[dict]:
        """Load and return a session dict, or None if not found."""
        path = DATA_DIR / f"{session_id}.json"
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

    @classmethod
    def delete_session(cls, session_id: str) -> bool:
        """Delete a session file. Returns True on success."""
        path = DATA_DIR / f"{session_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    # ── Listing ───────────────────────────────────────────────────────────────

    @classmethod
    def list_sessions(cls) -> list[dict]:
        """
        Return all sessions sorted newest-first.
        Each item: {"id", "title", "model", "updated_at", "message_count"}
        """
        sessions = []
        for fp in sorted(DATA_DIR.glob("*.json"), reverse=True):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                sessions.append(
                    {
                        "id": data.get("id", fp.stem),
                        "title": data.get("title", "Untitled"),
                        "model": data.get("model", "unknown"),
                        "updated_at": data.get("updated_at", ""),
                        "message_count": len(data.get("messages", [])),
                    }
                )
            except (json.JSONDecodeError, OSError):
                continue
        return sessions

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _auto_title(messages: list[dict]) -> str:
        """Derive a title from the first user message."""
        for msg in messages:
            if msg.get("role") == "user":
                text = msg.get("content", "").strip()
                if text:
                    return text[:TITLE_MAX_LEN] + ("…" if len(text) > TITLE_MAX_LEN else "")
        return "New Chat"

    @classmethod
    def rename_session(cls, session_id: str, new_title: str) -> bool:
        """Rename a session's title in place. Returns True on success."""
        session = cls.load_session(session_id)
        if not session:
            return False
        session["title"] = new_title.strip() or "Untitled"
        path = DATA_DIR / f"{session_id}.json"
        path.write_text(json.dumps(session, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
