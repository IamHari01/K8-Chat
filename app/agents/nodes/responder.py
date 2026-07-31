import logfire
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.agents.state import AgentState
from app.config import settings
from app.gateway import extract_cache_status, portkey_client
from app.guardrails.security_firewall import SECURE_GATE_SYSTEM_PROMPT


def generate_node(state: AgentState):
    """
    Synthesizes a response using both Documentation Context AND Conversation History.
    Uses the native Portkey client (not LangChain) so we can read the
    x-portkey-cache-status response header and surface Cache: Hit in the UI.
    """
    query = state["current_query"]

    history_str = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history_str += f"{role}: {msg['content']}\n"

    user_msg = state["messages"][-1]["content"] if state["messages"] else ""

    if query == "CONVERSATIONAL":
        logfire.info("Generating conversational response using memory.")
        prompt = f"""
{SECURE_GATE_SYSTEM_PROMPT}

        You are a crisp, direct, and intelligent Enterprise AI Assistant.
        Answer the user's message concisely using CONVERSATION HISTORY.

        CONVERSATION HISTORY:
        {history_str}

        LATEST MESSAGE:
        "{user_msg}"
        """
    else:
        logfire.info("Generating technical RAG response.")
        max_context_chars = 25000
        full_context = ""

        for doc in state["documents"]:
            if len(full_context) + len(doc) < max_context_chars:
                full_context += doc + "\n\n"
            else:
                logfire.warning("Context truncated to fit Groq TPM limits.")
                break

        prompt = f"""
{SECURE_GATE_SYSTEM_PROMPT}

        You are an expert Senior Technical Architect.
        Answer the user's question directly, crisply, and accurately using the TECHNICAL CONTEXT.

        STRICT RESPONSE RULES:
        1. Keep the answer CRISP, SHARP, and HIGH-IMPACT.
        2. Give a 2-3 sentence core definition/summary first.
        3. Follow up with at most 3-4 bullet points if essential.
        4. Do NOT output generic textbook tutorials, introductory fluff, or long concluding disclaimers.

        TECHNICAL CONTEXT:
        {full_context}

        CONVERSATION HISTORY:
        {history_str}

        USER QUESTION:
        "{user_msg}"
        """

    with logfire.span("✍️ LLM Synthesis & Layer 4 Confidentiality Inspection"):
        try:
            response = _generate_response(prompt)
            content = response.choices[0].message.content
            cache_status = extract_cache_status(response)
            is_cache_hit = cache_status == "HIT"

            # Layer 4: Post-Synthesis Output Confidentiality Guardrail
            from app.guardrails.security_firewall import sanitize_post_synthesis_output
            sanitized_content = sanitize_post_synthesis_output(content)

            if is_cache_hit:
                logfire.info("⚡ Gateway Cache Hit — response served from Portkey cache.")
                plan_update = state["plan"] + ["Cache: Hit ⚡"]
                status = "Cache hit — instant response."
            else:
                logfire.info("✅ Response synthesised via LLM & Layer 4 Verified.")
                plan_update = state["plan"]
                status = "Response generated."

            return {
                "final_answer": sanitized_content,
                "status": status,
                "plan": plan_update,
                "messages": [{"role": "assistant", "content": sanitized_content}],
            }

        except Exception as e:
            logfire.error(f"LLM Generation failed after retries: {e}")
            raise e


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
    before_sleep=before_sleep_log(logfire, "warning"),
)
def _generate_response(prompt: str):
    """Call the LLM gateway with retry logic for transient failures."""
    return portkey_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
