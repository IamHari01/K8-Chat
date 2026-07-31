import os
import time
import uuid

import logfire
import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables explicitly from the root directory
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)


# Initialize Logfire
LOGFIRE_STATUS = "Unknown"
try:
    token = os.getenv("LOGFIRE_TOKEN")
    base_url = os.getenv("LOGFIRE_BASE_URL")
    # EU Logfire v2 tokens must hit the EU endpoint.
    if not base_url and token and token.startswith("pylf_v2_eu_"):
        base_url = "https://logfire-eu.pydantic.dev"
    if not token:
        print("ERROR: LOGFIRE_TOKEN is empty or None!")
        LOGFIRE_STATUS = "Standby (LOGFIRE_TOKEN not set)"
    else:
        logfire.configure(
            token=token,
            advanced=logfire.AdvancedOptions(base_url=base_url) if base_url else None,
        )
        LOGFIRE_STATUS = "Connected & Tracing"
except Exception as e:
    print(f"Logfire Init Error in UI: {e}")
    LOGFIRE_STATUS = f"Standby (Error: {e})"


# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Enterprise Agentic RAG",
    page_icon="🤖",
    layout="wide",
)

# --- AVATARS ---
AI_AVATAR = "🤖"
USER_AVATAR = "👤"


# --- SESSION MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"✨ New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []


# --- SIDEBAR ---
with st.sidebar:
    st.title("🧠 Agent OS")
    st.markdown("---")
    st.success(f"Logfire: {LOGFIRE_STATUS}")
    st.info(f"Memory ID: {st.session_state.session_id[:8]}")

    if st.button("🗑️ Clear History & Memory", width="stretch", type="primary"):
        logfire.warn(f"🗑️ Memory Wipe Triggered for session: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- RUFUS-STYLE ANIMATIONS & CUSTOM STYLES ---
st.markdown("""
<style>
@keyframes pulse-heartbeat {
    0% { opacity: 0.45; transform: scale(0.99); }
    50% { opacity: 1.0; transform: scale(1.01); }
    100% { opacity: 0.45; transform: scale(0.99); }
}

@keyframes dot-pulse {
    0%, 80%, 100% { opacity: 0.25; transform: scale(0.75); }
    40% { opacity: 1.0; transform: scale(1.25); }
}

.rufus-thinking {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-style: italic;
    font-size: 1.15rem;
    font-weight: 500;
    color: #2D3748;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    background: linear-gradient(135deg, #F7FAFC 0%, #EDF2F7 100%);
    border-radius: 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
    animation: pulse-heartbeat 1.6s infinite ease-in-out;
    margin: 8px 0;
}

.dot-loader {
    display: inline-flex;
    gap: 5px;
    align-items: center;
}

.dot-loader span {
    width: 7px;
    height: 7px;
    background-color: #3182CE;
    border-radius: 50%;
    display: inline-block;
    animation: dot-pulse 1.4s infinite ease-in-out both;
}

.dot-loader span:nth-child(1) { animation-delay: -0.32s; }
.dot-loader span:nth-child(2) { animation-delay: -0.16s; }
.dot-loader span:nth-child(3) { animation-delay: 0s; }
</style>
""", unsafe_allow_html=True)


# --- MAIN CHAT ---
st.title("☸️ K8 Chat")


# Display history
for message in st.session_state.messages:
    avatar = AI_AVATAR if message["role"] == "assistant" else USER_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Ask about your documentation..."):
    # START TRACE: User Interaction
    with logfire.span("💬 User Chat Interaction", user_query=prompt, session_id=st.session_state.session_id):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        # Assistant Response with Rufus-style Heartbeat Animation
        with st.chat_message("assistant", avatar=AI_AVATAR):
            status_placeholder = st.empty()
            status_placeholder.markdown("""
            <div class="rufus-thinking">
                Checking on that...
                <div class="dot-loader">
                    <span></span><span></span><span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                # DISTRIBUTED TRACE: Calling Backend
                with logfire.span("📡 Calling RAG Backend"):
                    base_url = os.getenv("BACKEND_URL", "http://localhost:8000")
                    url = f"{base_url}/query"
                    payload = {"q": prompt, "thread_id": st.session_state.session_id}
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {os.getenv('RAG_API_KEY', '')}",
                    }
                    response = requests.post(url, json=payload, headers=headers, timeout=180)
                    data = response.json()

                full_answer = data.get("answer", "No response.")
            except Exception as e:
                logfire.error(f"❌ UI-Backend Connection Failed: {e}")
                status_placeholder.empty()
                st.error(f"Backend Offline or job failed: {e}")
                st.stop()

            # Clear Rufus thinking state once response is ready
            status_placeholder.empty()

            # Final Answer Streaming
            answer_placeholder = st.empty()
            full_answer = data.get("answer", "No response.")

            curr_text = ""
            for char in full_answer:
                curr_text += char
                answer_placeholder.markdown(curr_text + "▌")
                time.sleep(0.005)

            answer_placeholder.markdown(full_answer)
            st.session_state.messages.append({"role": "assistant", "content": full_answer})
            logfire.info("✅ Chat cycle completed successfully.")
