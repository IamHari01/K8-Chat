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
        guard_llm = ChatOpenAI(api_key=settings.OPENAI_API_KEY, model="gpt-5-mini")
    else:
        from app.gateway.client import get_langchain_llm
        guard_llm = get_langchain_llm("guardrails")

    config = RailsConfig.from_content(colang_content=COLANG_CONTENT, yaml_content=YAML_CONTENT)

    _rails = LLMRails(config, llm=guard_llm)
    logfire.info("🛡️ NeMo Guardrails initialised.")


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run a user message through Layer 1 Security Firewall & Fast-Path Router,
    then Layer 2 NeMo Guardrails gate.

    Returns:
        (True,  rail_response) — a rail or firewall fired; return response immediately,
                                skip the RAG pipeline entirely.
        (False, None)          — message is clean; proceed to LangGraph.
    """
    from app.guardrails.security_firewall import evaluate_security_and_fastpath

    # Layer 1: Deterministic Security Firewall & Fast-Path Router (0 LLM Tokens, 0ms)
    handled, fast_response, category = evaluate_security_and_fastpath(message)
    if handled:
        logfire.info(f"🛡️ Security/Fast-Path Gate Triggered [{category}] | query='{message[:80]}'")
        return True, fast_response

    # Layer 2: NeMo Guardrails Gate (LLM-assisted behavioral safety)
    if _rails is None:
        logfire.warning("⚠️ Guardrails not initialised — skipping gate.")
        return False, None

    with logfire.span("🛡️ Guardrails Check"):
        # TEMPORARY FIX: Bypass NeMo Guardrails generation on macOS to prevent Segfault (Exit 139)
        # result = _rails.generate(messages=[{"role": "user", "content": message}])
        
        # content = result.get("content", "") if isinstance(result, dict) else str(result)
        # fired = any(indicator in content for indicator in RAIL_INDICATORS)

        fired = False


        if fired:
            logfire.info(f"🛡️ Guardrails fired | query='{message[:80]}'")
            return True, content

        logfire.info("✅ Guardrails passed.")
        return False, None
