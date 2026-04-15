#!/usr/bin/env python3
"""
cli.py
──────
Terminal-based chat interface — useful for quick testing without Streamlit.

Usage:
    python cli.py
    python cli.py --model mistral:7b --temperature 0.5
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from backend.ollama_client import OllamaClient, RECOMMENDED_MODELS
from backend.history_manager import HistoryManager

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    RICH = True
except ImportError:
    RICH = False


def _print(text: str, style: str = "") -> None:
    if RICH:
        console.print(text, style=style)
    else:
        print(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local SLM CLI Chat")
    parser.add_argument("--model", default=RECOMMENDED_MODELS[0], help="Ollama model tag")
    parser.add_argument("--temperature", type=float, default=0.7, help="Sampling temperature")
    parser.add_argument("--system", default="You are a helpful assistant.", help="System prompt")
    args = parser.parse_args()

    global console
    if RICH:
        console = Console()
        console.print(Panel.fit(
            f"[bold #7C6AF7]Local SLM Chat[/] — model: [cyan]{args.model}[/]  temp: [yellow]{args.temperature}[/]\n"
            "[dim]Type 'exit' or Ctrl+C to quit. Type '/clear' to reset history.[/]",
            border_style="#2A2A3A",
        ))
    else:
        print(f"\n=== Local SLM Chat | model: {args.model} ===")
        print("Type 'exit' to quit, '/clear' to reset.\n")

    client = OllamaClient()
    if not client.is_running():
        _print("❌  Ollama is not running. Start it with: ollama serve", "bold red")
        sys.exit(1)

    session_id = HistoryManager.new_session_id()
    messages: list[dict] = []

    try:
        while True:
            # ── User input ──────────────────────────────────────────────
            if RICH:
                user_input = Prompt.ask("\n[bold #7C6AF7]You[/]")
            else:
                user_input = input("\nYou: ").strip()

            if not user_input.strip():
                continue
            if user_input.lower() in ("exit", "quit", "/exit"):
                _print("Goodbye! 👋", "dim")
                break
            if user_input.lower() == "/clear":
                messages = []
                session_id = HistoryManager.new_session_id()
                _print("Chat cleared.", "yellow")
                continue

            messages.append({"role": "user", "content": user_input})

            # ── Stream response ─────────────────────────────────────────
            if RICH:
                console.print("\n[bold #4ADE80]Assistant[/]")
            else:
                print("\nAssistant: ", end="", flush=True)

            full_response = ""
            for chunk in client.chat_stream(
                model=args.model,
                messages=messages,
                system_prompt=args.system,
                temperature=args.temperature,
            ):
                full_response += chunk
                if RICH:
                    # reprint with rich markdown on each chunk
                    console.print(chunk, end="", highlight=False)
                else:
                    print(chunk, end="", flush=True)

            print()  # newline after stream ends
            messages.append({"role": "assistant", "content": full_response})

            # ── Persist ─────────────────────────────────────────────────
            HistoryManager.save_session(
                session_id=session_id,
                messages=messages,
                model=args.model,
                system_prompt=args.system,
            )

    except KeyboardInterrupt:
        _print("\nInterrupted. Goodbye!", "dim")


if __name__ == "__main__":
    main()
