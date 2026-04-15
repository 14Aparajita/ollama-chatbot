"""
frontend/app.py
───────────────
Streamlit UI for the Local SLM Chatbot.

Run with:
    streamlit run frontend/app.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import streamlit as st

# ── make sure the project root is on sys.path ──────────────────────────────
ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.ollama_client import OllamaClient, RECOMMENDED_MODELS
from backend.history_manager import HistoryManager

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Local SLM Chat",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
code, pre, .stCodeBlock {
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0E0E12;
    border-right: 1px solid #1E1E2E;
}
section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border-radius: 8px;
    font-size: 13px;
    text-align: left;
    background: #16161C;
    border: 1px solid #2A2A3A;
    color: #C8C8D8;
    transition: all .15s;
    padding: 8px 12px;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #1E1E2E;
    border-color: #7C6AF7;
    color: #fff;
}

/* ── Chat messages ── */
.chat-bubble-user {
    background: linear-gradient(135deg, #7C6AF7 0%, #5E4FD6 100%);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 4px 0 4px 15%;
    font-size: 15px;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(124,106,247,.25);
    word-wrap: break-word;
}
.chat-bubble-assistant {
    background: #16161C;
    color: #E8E8F0;
    border: 1px solid #2A2A3A;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 4px 15% 4px 0;
    font-size: 15px;
    line-height: 1.6;
    box-shadow: 0 2px 8px rgba(0,0,0,.2);
    word-wrap: break-word;
}
.chat-meta {
    font-size: 11px;
    color: #555570;
    margin-bottom: 2px;
    padding: 0 4px;
}
.chat-meta-right { text-align: right; }

/* ── Status badges ── */
.badge-online  { color: #4ADE80; font-size: 12px; }
.badge-offline { color: #F87171; font-size: 12px; }

/* ── Input area ── */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid #2A2A3A !important;
    background: #16161C !important;
    color: #E8E8F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #7C6AF7 !important;
    box-shadow: 0 0 0 2px rgba(124,106,247,.2) !important;
}

/* ── Send button ── */
div[data-testid="column"]:last-child .stButton button {
    background: linear-gradient(135deg, #7C6AF7, #5E4FD6);
    color: white;
    border: none;
    border-radius: 12px;
    font-weight: 600;
    height: 80px;
    font-size: 22px;
    transition: all .2s;
    box-shadow: 0 4px 15px rgba(124,106,247,.35);
}
div[data-testid="column"]:last-child .stButton button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,106,247,.45);
}

/* ── Scrollable chat area ── */
.chat-container {
    max-height: 62vh;
    overflow-y: auto;
    padding: 8px 4px;
    scrollbar-width: thin;
    scrollbar-color: #2A2A3A transparent;
}
.chat-container::-webkit-scrollbar { width: 4px; }
.chat-container::-webkit-scrollbar-track { background: transparent; }
.chat-container::-webkit-scrollbar-thumb { background: #2A2A3A; border-radius: 4px; }

/* ── Dividers & misc ── */
hr { border-color: #1E1E2E !important; }
.stSlider > div > div { color: #7C6AF7; }
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  Session state initialisation
# ═══════════════════════════════════════════════════════════════════════════════

def _init_state() -> None:
    defaults = {
        "messages": [],                   # current conversation
        "session_id": HistoryManager.new_session_id(),
        "model": RECOMMENDED_MODELS[0],
        "system_prompt": "You are a helpful, concise, and friendly AI assistant running entirely on the user's local machine.",
        "temperature": 0.7,
        "streaming": True,
        "client": OllamaClient(),
        "ollama_ok": False,
        "local_models": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_state()
client: OllamaClient = st.session_state.client


# ═══════════════════════════════════════════════════════════════════════════════
#  Helper functions
# ═══════════════════════════════════════════════════════════════════════════════

def refresh_models() -> None:
    st.session_state.ollama_ok = client.is_running()
    if st.session_state.ollama_ok:
        st.session_state.local_models = client.list_local_models()


def new_chat() -> None:
    """Start a fresh conversation."""
    st.session_state.messages = []
    st.session_state.session_id = HistoryManager.new_session_id()


def load_session(session_id: str) -> None:
    """Load a past session into the active view."""
    data = HistoryManager.load_session(session_id)
    if data:
        st.session_state.messages = data.get("messages", [])
        st.session_state.session_id = session_id
        st.session_state.model = data.get("model", st.session_state.model)
        st.session_state.system_prompt = data.get("system", st.session_state.system_prompt)


def delete_session(session_id: str) -> None:
    HistoryManager.delete_session(session_id)
    if st.session_state.session_id == session_id:
        new_chat()


def render_message(role: str, content: str) -> None:
    if role == "user":
        st.markdown(f'<div class="chat-meta chat-meta-right">You</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-user">{content}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-meta">🧠 Assistant</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-assistant">{content}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  Sidebar
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("## 🧠 Local SLM Chat")
    st.markdown("---")

    # ── Ollama status ──────────────────────────────────────────────────────
    col_s, col_r = st.columns([3, 1])
    with col_s:
        if st.session_state.ollama_ok:
            st.markdown('<span class="badge-online">● Ollama running</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-offline">● Ollama offline</span>', unsafe_allow_html=True)
    with col_r:
        if st.button("↻", help="Refresh connection"):
            refresh_models()
            st.rerun()

    st.markdown("---")

    # ── Model selection ────────────────────────────────────────────────────
    st.markdown("**Model**")
    all_models = list(dict.fromkeys(st.session_state.local_models + RECOMMENDED_MODELS))
    if all_models:
        current_idx = all_models.index(st.session_state.model) if st.session_state.model in all_models else 0
        selected_model = st.selectbox(
            "Model",
            options=all_models,
            index=current_idx,
            label_visibility="collapsed",
        )
        st.session_state.model = selected_model
    else:
        st.caption("No models detected. Pull one below.")

    # ── Pull a model ───────────────────────────────────────────────────────
    with st.expander("Pull a new model"):
        pull_name = st.text_input("Model tag", placeholder="e.g. llama3.2:3b")
        if st.button("Pull", disabled=not pull_name):
            with st.spinner(f"Pulling {pull_name}…"):
                try:
                    for prog in client.pull_model(pull_name):
                        status = prog.get("status", "")
                        total = prog.get("total", 0)
                        done = prog.get("completed", 0)
                        if total:
                            pct = int(done / total * 100)
                            st.progress(pct / 100, text=f"{status} {pct}%")
                    refresh_models()
                    st.success(f"✅ {pull_name} ready!")
                except RuntimeError as e:
                    st.error(str(e))

    st.markdown("---")

    # ── Generation settings ────────────────────────────────────────────────
    st.markdown("**Settings**")
    st.session_state.temperature = st.slider(
        "Temperature", 0.0, 2.0, st.session_state.temperature, 0.05,
        help="Higher = more creative. Lower = more deterministic."
    )
    st.session_state.streaming = st.toggle("Streaming", value=st.session_state.streaming)

    st.markdown("---")

    # ── System prompt ──────────────────────────────────────────────────────
    st.markdown("**System Prompt**")
    st.session_state.system_prompt = st.text_area(
        "System prompt",
        value=st.session_state.system_prompt,
        height=100,
        label_visibility="collapsed",
        placeholder="Give the model a personality…",
    )

    st.markdown("---")

    # ── New chat ───────────────────────────────────────────────────────────
    if st.button("＋  New Chat", use_container_width=True):
        new_chat()
        st.rerun()

    st.markdown("---")

    # ── Chat history ───────────────────────────────────────────────────────
    st.markdown("**History**")
    sessions = HistoryManager.list_sessions()
    if not sessions:
        st.caption("No saved chats yet.")
    for s in sessions[:20]:   # show latest 20
        is_active = s["id"] == st.session_state.session_id
        label = ("▶ " if is_active else "") + s["title"][:30]
        col_h, col_d = st.columns([5, 1])
        with col_h:
            if st.button(label, key=f"load_{s['id']}", help=s["title"]):
                load_session(s["id"])
                st.rerun()
        with col_d:
            if st.button("🗑", key=f"del_{s['id']}", help="Delete"):
                delete_session(s["id"])
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  Main chat area
# ═══════════════════════════════════════════════════════════════════════════════

# ── Header ─────────────────────────────────────────────────────────────────
header_col, action_col = st.columns([6, 1])
with header_col:
    model_display = st.session_state.model or "No model selected"
    st.markdown(f"### 💬 Chat &nbsp; <span style='color:#555570;font-size:14px;font-weight:400'>{model_display}</span>", unsafe_allow_html=True)
with action_col:
    if st.button("🗑 Clear", help="Clear current chat"):
        st.session_state.messages = []
        st.session_state.session_id = HistoryManager.new_session_id()
        st.rerun()

st.markdown("---")

# ── Check Ollama on first load ─────────────────────────────────────────────
if not st.session_state.ollama_ok:
    refresh_models()

if not st.session_state.ollama_ok:
    st.error(
        "⚠️ **Ollama is not running.** Start it with `ollama serve` in a terminal, "
        "then click ↻ in the sidebar.",
        icon="🔴",
    )
    st.stop()

if not st.session_state.local_models and not st.session_state.model:
    st.warning("No local models found. Pull one from the sidebar.", icon="⚠️")

# ── Render existing messages ───────────────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    render_message(msg["role"], msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

# ── Input row ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
input_col, btn_col = st.columns([9, 1])

with input_col:
    user_input = st.text_area(
        "Message",
        key="chat_input",
        placeholder="Type a message… (Shift+Enter for newline)",
        height=80,
        label_visibility="collapsed",
    )

with btn_col:
    send_pressed = st.button("➤", help="Send message")

# ── Handle send ────────────────────────────────────────────────────────────
if send_pressed and user_input.strip():
    prompt = user_input.strip()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ── Stream or full response ────────────────────────────────────────
    with st.spinner(""):
        render_message("user", prompt)
        st.markdown('<div class="chat-meta">🧠 Assistant</div>', unsafe_allow_html=True)
        response_placeholder = st.empty()
        full_response = ""

        try:
            if st.session_state.streaming:
                for chunk in client.chat_stream(
                    model=st.session_state.model,
                    messages=st.session_state.messages,
                    system_prompt=st.session_state.system_prompt,
                    temperature=st.session_state.temperature,
                ):
                    full_response += chunk
                    response_placeholder.markdown(
                        f'<div class="chat-bubble-assistant">{full_response}▌</div>',
                        unsafe_allow_html=True,
                    )
                response_placeholder.markdown(
                    f'<div class="chat-bubble-assistant">{full_response}</div>',
                    unsafe_allow_html=True,
                )
            else:
                full_response = client.chat(
                    model=st.session_state.model,
                    messages=st.session_state.messages,
                    system_prompt=st.session_state.system_prompt,
                    temperature=st.session_state.temperature,
                )
                response_placeholder.markdown(
                    f'<div class="chat-bubble-assistant">{full_response}</div>',
                    unsafe_allow_html=True,
                )

            # Save assistant reply
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Persist to disk
            HistoryManager.save_session(
                session_id=st.session_state.session_id,
                messages=st.session_state.messages,
                model=st.session_state.model,
                system_prompt=st.session_state.system_prompt,
            )

        except RuntimeError as exc:
            st.error(f"❌ {exc}")
            # Remove the user message we already appended if response failed
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

    st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#333355;font-size:12px'>"
    "🔒 100% local · no cloud · no tracking"
    "</p>",
    unsafe_allow_html=True,
)
