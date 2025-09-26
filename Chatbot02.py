# chatbot02.py
import streamlit as st
import uuid
from datetime import datetime
import os
import requests
import json

st.set_page_config(page_title="Sarvam AI Chatbot", layout="wide")
st.title("Shiva Chatbot")

# --- Sidebar settings ---
with st.sidebar:
    st.header("Settings")
    mode = st.selectbox(
        "Mode (choose one)",
        ["Mock (no API)", "Sarvam AI"]
    )
    api_key_input = st.text_input(
        "API Key (for Sarvam AI)",
        type="password",
        value="sk_h4gsam68_z6e2xo8u9aaleUaBshwjVyDk"
    )
    model_choice = st.selectbox(
        "Sarvam model",
        ["sarvam-m", "gemma-4b", "gemma-12b"],
        index=0
    )
    system_prompt = st.text_area(
        "System prompt (instructions to the assistant)",
        value="You are a helpful assistant.",
        height=120
    )
    st.markdown("---")
    st.write("Keep API keys private. For Sarvam AI, enter your key here.")

# Set API key as environment variable
if api_key_input:
    os.environ["CHATBOT_API_KEY"] = api_key_input

# --- Session state initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt, "ts": datetime.utcnow().isoformat()}]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- Chat layout ---
chat_col, meta_col = st.columns((3, 1))

with chat_col:
    st.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    st.markdown("### Chat")

    # Display previous messages
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Input area
    user_message = st.chat_input("Type a message...")

    if user_message:
        # Append user message
        st.session_state.messages.append({
            "role": "user",
            "content": user_message,
            "ts": datetime.utcnow().isoformat()
        })

        # Placeholder for assistant response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.write("…thinking…")

        # --- Sarvam AI integration ---
        response_text = ""
        if mode == "Mock (no API)":
            txt = user_message.lower()
            if any(w in txt for w in ["hi", "hello", "hey"]):
                response_text = "Hi there! How can I help you today?"
            elif "how are you" in txt:
                response_text = "I'm a bot, doing fine — thanks for asking! How about you?"
            elif "bye" in txt or "goodbye" in txt:
                response_text = "Goodbye — talk later!"
            else:
                response_text = "Sorry, I don't have a smart reply in Mock mode. Switch to Sarvam AI for full conversation."

        elif mode == "Sarvam AI":
            try:
                key = os.getenv("CHATBOT_API_KEY")
                if not key:
                    raise ValueError("No API key found. Enter it in the sidebar.")

                # Build messages for multi-turn context
                messages_for_api = [
                    {"role": "system", "content": system_prompt}
                ]
                for m in st.session_state.messages:
                    if m["role"] != "system":
                        messages_for_api.append({"role": m["role"], "content": m["content"]})

                payload = {
                    "model": model_choice,   # ✅ required by Sarvam
                    "messages": messages_for_api
                }

                headers = {
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json"
                }

                # Correct endpoint for Sarvam AI chat-completion
                url = "https://api.sarvam.ai/v1/chat/completions"
                resp = requests.post(url, headers=headers, json=payload, timeout=60)

                if resp.status_code != 200:
                    response_text = f"[Sarvam AI error {resp.status_code}] {resp.text}"
                else:
                    data = resp.json()
                    response_text = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "Sarvam AI did not return a reply.")
                    )

            except Exception as e:
                response_text = f"[Sarvam AI error] {e}"

        # Remove placeholder & append assistant response
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
        st.session_state.messages = [{"role": "system", "content": system_prompt, "ts": datetime.utcnow().isoformat()}]
        st.experimental_rerun()

st.caption("Your chatbot now uses Sarvam AI. Type messages and see live responses.")
