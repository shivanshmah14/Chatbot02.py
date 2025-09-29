# chatbot03.py
import streamlit as st
import uuid
from datetime import datetime
import os
import requests
import json
import re

st.set_page_config(page_title="Shiva AI", layout="wide")
st.title("Shiva AI")

# --- Configuration ---
API_KEY = os.getenv("CHATBOT_API_KEY", "sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk")
MODEL = "sarvam-m"   # Backend model
SYSTEM_PROMPT = (
    "You are Shiva AI, a helpful assistant. "
    "You can explain and solve mathematics and physics problems. "
    "Use LaTeX notation for equations and symbols (e.g., x^2, \\frac{a}{b}, \\Delta E, \\vec{F}). "
    "Always format math and physics content clearly."
)

# --- Session state initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT, "ts": datetime.utcnow().isoformat()}
    ]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- Chat layout ---
chat_col, meta_col = st.columns((3, 1))

with chat_col:
    st.markdown("### Chat")

    # Display previous messages
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            content = msg["content"]

            # Render LaTeX if detected
            if re.search(r"(\$.*\$|\\\[.*\\\])", content):
                try:
                    st.markdown(content)
                except:
                    st.write(content)
            else:
                st.write(content)

    # Input area
    user_message = st.chat_input("Type a message...")

    if user_message:
        st.session_state.messages.append({
            "role": "user",
            "content": user_message,
            "ts": datetime.utcnow().isoformat()
        })

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.write("…thinking…")

        # --- API request ---
        try:
            if not API_KEY:
                raise ValueError("No API key found. Set CHATBOT_API_KEY in environment.")

            messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}]
            for m in st.session_state.messages:
                if m["role"] != "system":
                    messages_for_api.append({"role": m["role"], "content": m["content"]})

            payload = {"model": MODEL, "messages": messages_for_api}
            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            url = "https://api.sarvam.ai/v1/chat/completions"

            resp = requests.post(url, headers=headers, json=payload, timeout=60)

            if resp.status_code != 200:
                response_text = f"[Error {resp.status_code}] {resp.text}"
            else:
                data = resp.json()
                response_text = (
                    data.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "No reply.")
                )

        except Exception as e:
            response_text = f"[Error] {e}"

        # Display reply
        if re.search(r"(\$.*\$|\\\[.*\\\])", response_text):
            placeholder.markdown(response_text)
        else:
            placeholder.write(response_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": response_text,
            "ts": datetime.utcnow().isoformat()
        })

with meta_col:
    st.markdown("### Conversation info")
    st.write(f"Messages: {len([m for m in st.session_state.messages if m['role'] != 'system'])}")
    if st.button("Clear conversation"):
        st.session_state.messages = [
            {"role": "system", "content": SYSTEM_PROMPT, "ts": datetime.utcnow().isoformat()}
        ]
        st.experimental_rerun()

st.caption("Shiva AI — your personal assistant ⚡")

