import logfire
from langchain_openai import ChatOpenAI
from nemoguardrails import LLMRails, RailsConfig

from app.config import settings
from app.guardrails.colang_rules import COLANG_CONTENT, RAIL_INDICATORS, YAML_CONTENT

_rails: LLMRails | None = None


def initialize_rails() -> None:
    """
    Build the NeMo LLMRails singleton at app startup.
    Uses OpenAI gpt-5-mini for fast intent classification at the gate.
    """
    global _rails

    if settings.OPENAI_API_KEY:
        guard_llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-4o-mini")
    else:
        from app.gateway.client import get_langchain_llm
        guard_llm = get_langchain_llm("guardrails")

    try:
        config = RailsConfig.from_content(colang_content=COLANG_CONTENT, yaml_content=YAML_CONTENT)
        _rails = LLMRails(config, llm=guard_llm)
        logfire.info("🛡️ NeMo Guardrails initialised.")
    except Exception as e:
        logfire.warning(f"⚠️ NeMo Guardrails initialization failed ({e}); Layer 1 & 2 Firewalls active.")
        _rails = None


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through Layer 1 Security Firewall & Fast-Path Router,
    and Layer 2 Pre-Retrieval Sensitive Semantic Intent Guardrail.

    Returns:
        (True,  rail_response) — a rail or firewall fired; return response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    from app.guardrails.security_firewall import evaluate_security_and_fastpath

    # Layer 1 & 2: Deterministic Security Firewall & Fast-Path Router (0ms, 0 Tokens, 100% Stable)
    handled, fast_response, category = evaluate_security_and_fastpath(message)
    if handled:
        logfire.info(f"🛡️ Security/Fast-Path Gate Triggered [{category}] | query='{message[:80]}'")
        return True, fast_response

    logfire.info("✅ Security Firewalls & Intent Gates Passed.")
    return False, None
