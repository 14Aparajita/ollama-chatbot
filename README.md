# 🧠 Local SLM Chatbot — Powered by Ollama

> A **production-ready**, fully local AI chatbot with a polished Streamlit UI,  
> streaming responses, persistent chat history, and zero cloud dependencies.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔒 100% local | No API keys. No cloud. No data leaves your machine. |
| ⚡ Streaming | Token-by-token responses just like ChatGPT |
| 💾 Persistent history | Sessions saved as JSON; reload any past chat |
| 🎛 Adjustable settings | Temperature, system prompt, model selector |
| 🖥 Clean UI | Dark-themed Streamlit frontend |
| 🧪 CLI mode | Terminal chat for quick testing |
| 📦 Multi-model | Switch between any Ollama model at runtime |

---

## 📁 Project Structure

```
ollama-chatbot/
├── backend/
│   ├── __init__.py          # Package exports
│   ├── ollama_client.py     # Ollama API wrapper (streaming + sync)
│   └── history_manager.py   # JSON-based chat persistence
├── frontend/
│   └── app.py               # Streamlit UI
├── data/
│   └── chats/               # Auto-created; stores session .json files
├── .streamlit/
│   └── config.toml          # Dark theme & server settings
├── cli.py                   # Optional terminal interface
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1 · Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:** Download installer from [ollama.com](https://ollama.com/download)

### 2 · Start Ollama & Pull a Model

```bash
# Start the daemon (runs on http://localhost:11434)
ollama serve

# In a new terminal — pull a lightweight model
ollama pull llama3.2:3b      # 2 GB  — best balance
ollama pull gemma2:2b         # 1.6 GB — very fast
ollama pull phi3:mini         # 2.3 GB — great for coding
ollama pull mistral:7b        # 4.1 GB — high quality
```

### 3 · Set Up the Python Environment

```bash
# Clone / enter the project
cd ollama-chatbot

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4 · Run the App

**Streamlit UI (recommended):**
```bash
streamlit run frontend/app.py
```
Open → [http://localhost:8501](http://localhost:8501)

**CLI (terminal):**
```bash
python cli.py
python cli.py --model mistral:7b --temperature 0.5
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and set:

```env
OLLAMA_HOST=http://localhost:11434   # Change if running Ollama remotely
DEFAULT_MODEL=llama3.2:3b
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.35.0 | Frontend UI framework |
| `ollama` | 0.3.3 | Official Ollama Python SDK |
| `httpx` | 0.27.0 | HTTP client (used by ollama SDK) |
| `python-dateutil` | 2.9.0 | Date parsing for session metadata |
| `python-dotenv` | 1.0.1 | `.env` file support |
| `rich` *(optional)* | 13.7.1 | Pretty CLI output |
| `watchdog` *(optional)* | 4.0.1 | Faster Streamlit hot-reload |

Install all:
```bash
pip install -r requirements.txt
```

---

## 🗂 Chat History

Sessions are stored in `data/chats/<session_id>.json`:

```json
{
  "id": "20240415_143022",
  "title": "First 60 chars of your first message…",
  "model": "llama3.2:3b",
  "system": "You are a helpful assistant.",
  "created_at": "2024-04-15T14:30:22",
  "updated_at": "2024-04-15T14:35:10",
  "messages": [
    {"role": "user",      "content": "Hello!"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

Sessions auto-load from the sidebar. Delete any session with the 🗑 button.

---

## 🧪 Testing the Backend Directly

```python
from backend.ollama_client import OllamaClient

client = OllamaClient()
print(client.is_running())          # True
print(client.list_local_models())   # ['llama3.2:3b', ...]

# Non-streaming
reply = client.chat("llama3.2:3b", [{"role":"user","content":"Hello!"}])
print(reply)

# Streaming
for chunk in client.chat_stream("llama3.2:3b", [{"role":"user","content":"Tell me a joke"}]):
    print(chunk, end="", flush=True)
```

---

## 💡 Resume-Worthy Improvements

| Idea | Impact |
|---|---|
| **RAG (Retrieval-Augmented Generation)** | Add `chromadb` + `sentence-transformers` to chat with your own docs/PDFs |
| **LangChain / LlamaIndex integration** | Enable tool use, agents, and multi-step reasoning |
| **Docker + docker-compose** | One-command setup: `docker-compose up` |
| **FastAPI backend** | Decouple the UI from the model server; expose a REST API |
| **WebSocket streaming** | Replace polling with true real-time streaming |
| **SQLite storage** | Replace JSON files with a proper DB for search and filtering |
| **Authentication** | Add `streamlit-authenticator` for multi-user support |
| **Model benchmarking tab** | Compare models side-by-side on the same prompt |
| **Voice I/O** | Add `whisper.cpp` for speech-to-text input |
| **Eval harness** | Log responses + user thumbs-up/down for fine-tuning later |

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| "Ollama is not running" | Run `ollama serve` in a terminal |
| Model not found | Run `ollama pull <model-name>` |
| Port 11434 in use | `OLLAMA_HOST=http://localhost:11435 ollama serve` |
| Slow responses | Try a smaller model: `gemma2:2b` or `llama3.2:1b` |
| GPU not used | Ensure CUDA/Metal drivers are installed; check `ollama ps` |

---

## 📄 License

MIT — use freely, hack freely, ship freely.
