# 🧠 Local SLM Chatbot — Powered by Ollama

> A **production-ready**, fully local AI chatbot with a polished Streamlit UI,  
> streaming responses, persistent chat history, and zero cloud dependencies (unless you want them!).

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔒 **100% local** | No API keys. No cloud. No data leaves your machine. |
| ⚡ **Streaming** | Token-by-token responses just like ChatGPT. |
| 💾 **Persistent history** | Sessions saved as JSON; reload any past chat. |
| 🌐 **Cloud-Ready** | deploy UI to Streamlit Cloud while running models locally via Ngrok. |
| 🎛 **Adjustable settings** | Temperature, system prompt, model selector. |
| 🖥 **Clean UI** | Dark-themed, responsive Streamlit frontend. |
| 📦 **Multi-model** | Switch between any Ollama model at runtime instantly. |

---

## 🚀 Quick Start (Local Setup)

### 1 · Install Ollama

**Windows:** Download the installer from [ollama.com](https://ollama.com/download)  
**macOS / Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2 · Start Ollama & Pull a Model

```bash
# Start the daemon (runs on http://localhost:11434)
ollama serve

# In a new terminal — pull a lightweight model
ollama pull llama3.2:3b      # 2 GB  — best balance
ollama pull gemma2:2b        # 1.6 GB — very fast
ollama pull mistral:7b       # 4.1 GB — high quality
```

### 3 · Set Up the Python Environment

```bash
# Clone / enter the project
cd ollama-chatbot

# Create a virtual environment (recommended)
python -m venv .venv

# Activate:
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt
```

### 4 · Run the App

**Streamlit UI (recommended):**
```bash
streamlit run frontend/app.py
```
*Open → [http://localhost:8501](http://localhost:8501)*

**CLI (terminal):**
```bash
python cli.py
```

---

## 🌐 Deploying Live (Streamlit Cloud + Ngrok)

Want to host your UI on the web for others to use, but run the heavy AI models for free on your local hardware? You can tunnel your local Ollama connection up to Streamlit Cloud!

1. **Configure Ollama for external connections:**
   By default, Ollama blocks external requests. On your local machine, set an environment variable to allow origins:
   - **Windows PowerShell:** `[Environment]::SetEnvironmentVariable('OLLAMA_ORIGINS', '*', 'User')`
   - **Mac/Linux:** `export OLLAMA_ORIGINS="*"`
   *(Make sure to completely quit and restart your Ollama app/service after setting this!)*

2. **Start Ngrok:**
   Download [ngrok](https://ngrok.com/), authenticate your account, and expose your Ollama port:
   ```bash
   ngrok http 11434
   ```
   *Copy the forwarded `https://...ngrok.app` URL.*

3. **Deploy the Streamlit UI to the Cloud:**
   - Commit and push your code to your GitHub repository.
   - Go to [share.streamlit.io](https://share.streamlit.io/) and deploy your repository (Main file: `frontend/app.py`).

4. **Connect the App:**
   - On Streamlit Community Cloud, navigate to **Settings > Secrets**.
   - Add your Ngrok URL:
     ```toml
     OLLAMA_HOST = "https://<your-ngrok-url.ngrok.app>"
     ```
   - Hit **Save**. Your cloud app will now generate text securely using your local machine.

---

## ⚙️ Configuration & Project Structure

Copy `.env.example` to `.env` and set:

```env
OLLAMA_HOST=http://localhost:11434   # Can be overridden by Streamlit Secrets
DEFAULT_MODEL=llama3.2:3b
```

```
ollama-chatbot/
├── backend/
│   ├── __init__.py          
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

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| "Ollama is not running" | Run `ollama serve` in a terminal or start the background app. |
| Model not found | Run `ollama pull <model-name>`. |
| Streamlit Cloud fails to connect | Check if your local ngrok terminal is running, you fully restarted Ollama after setting `OLLAMA_ORIGINS`, and verify your Streamlit Cloud Secrets have the correct `OLLAMA_HOST`. |

---

## 📄 License

MIT — use freely, hack freely, ship freely.
