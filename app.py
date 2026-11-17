# GEMINI KNOWLEDGE-BASED CHATBOT (Streamlit version)
import os
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.5-flash-lite"
KNOWLEDGE_FILE = Path(__file__).parent / "knowledge_base.txt"

SYSTEM_INSTRUCTION = """
Answer only from the given manual.
If the answer is not available in the manual, say: Answer not available
Give simple and clear answers.
"""

st.set_page_config(page_title="Digital Marketing Chatbot", page_icon="📣")


# ---------- Helpers ----------
def get_api_key() -> str | None:
    """Read the API key from Streamlit secrets, env var, or sidebar input."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY") or st.session_state.get("sidebar_key")


@st.cache_data
def load_manual() -> str:
    return KNOWLEDGE_FILE.read_text(encoding="utf-8")


@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Settings")
    if not (os.getenv("GEMINI_API_KEY") or "GEMINI_API_KEY" in st.secrets):
        st.text_input("Gemini API key", type="password", key="sidebar_key")
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()
    with st.expander("View knowledge base"):
        st.text(load_manual())

# ---------- Main UI ----------
st.title("📣 Digital Marketing Chatbot")
st.caption("Ask any question about digital marketing. Answers come only from the knowledge base.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask your question...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    api_key = get_api_key()
    with st.chat_message("assistant"):
        if not api_key:
            answer = "Please provide your Gemini API key (sidebar, secrets.toml, or GEMINI_API_KEY env var)."
            st.warning(answer)
        else:
            try:
                with st.spinner("Thinking..."):
                    client = get_client(api_key)
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=load_manual() + "\n\nQuestion: " + question,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION
                        ),
                    )
                answer = response.text or "Answer not available"
                st.markdown(answer)
            except Exception as e:
                answer = f"Error: {e}"
                st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
