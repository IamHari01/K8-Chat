import logfire

from app.agents.state import AgentState
from app.gateway import get_langchain_llm

# Portkey-backed LLM: fallback + cache + retry — same .invoke() interface as ChatOpenAI
llm = get_langchain_llm(feature="planner")


def planner_node(state: AgentState):
    """
    The Planner determines if a search is needed based on the ENTIRE conversation.
    """
    # Get the conversation history (excluding the latest message)
    history = ""
    for msg in state["messages"][:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        history += f"{role}: {msg['content']}\n"

    user_message = state["messages"][-1]["content"] if state["messages"] else ""

    prompt = f"""
    You are an intelligent Assistant Planner.
    Analyze the conversation history and the latest user message.

    CONVERSATION HISTORY:
    {history}

    LATEST MESSAGE:
    "{user_message}"

    Task:
    1. If the latest message is a greeting (hi, hello) or a question that can be answered using ONLY the conversation history above (e.g., "what is my name"), respond with 'CONVERSATIONAL'.
    2. If it is a technical question about Kubernetes, Intel, or Networking that requires fresh documentation, output a refined search query.

    Output ONLY 'CONVERSATIONAL' or the search query.
    """

    with logfire.span("🧠 Planner Decision"):
        decision = llm.invoke(prompt).content.strip()
        logfire.info(f"Intent identified: {decision[:100]}")

    # Robust Intent Detection
    if "CONVERSATIONAL" in decision.upper() or len(decision.splitlines()) > 2:
        return {
            "current_query": "CONVERSATIONAL",
            "status": "Handling conversationally (using memory)...",
            "plan": ["Intent: Conversational/Memory", "Retrieval: Skipped"],
        }

    # Extract first line clean search term
    clean_query = decision.splitlines()[0].strip()

    return {
        "current_query": clean_query,
        "status": f"Technical research needed. Searching for: {clean_query}",
        "plan": ["Intent: Technical", f"Search Term: {clean_query}"],
    }
