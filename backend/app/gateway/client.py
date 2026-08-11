from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders

from app.config import settings

# Portkey routing strategy:
#   - Primary/fallback logic lives in a Portkey saved config (required when
#     block_inline_config is enabled on the workspace).
#   - We reference that config via the x-portkey-config-id header.
#   - The inline config dict approach is disabled for this account, so all
#     retry/fallback/cache behavior must be configured inside the Portkey UI.


def _make_headers(feature: str = "rag") -> dict:
    """Build Portkey headers supporting Saved Configs or Inline Multi-Key Load Balancing & 4 Fallbacks."""
    # Mode 1: Saved Config ID (e.g. pc-groq-4-223853)
    if settings.PORTKEY_PRIMARY_CONFIG_ID:
        headers = createHeaders(
            api_key=settings.PORTKEY_API_KEY,
            config=settings.PORTKEY_PRIMARY_CONFIG_ID,
            metadata={
                "feature": feature,
                "_user": "rag-system",
                "environment": "production",
            },
        )
        headers["x-portkey-cache"] = "simple"
        return headers

    # Mode 2: Multi-Key Groq API Keys or Virtual Keys (Load Balance + Sequential Fallbacks)
    groq_keys = [
        k for k in [
            settings.GROQ_API_KEY_1,
            settings.GROQ_API_KEY_2,
            settings.GROQ_API_KEY_3,
            settings.GROQ_API_KEY_4,
        ] if k
    ]
    virtual_keys = [
        vk for vk in [
            settings.PORTKEY_VIRTUAL_KEY_1,
            settings.PORTKEY_VIRTUAL_KEY_2,
            settings.PORTKEY_VIRTUAL_KEY_3,
            settings.PORTKEY_VIRTUAL_KEY_4,
        ] if vk
    ]

    models = [
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
    ]

    targets = []
    if groq_keys:
        weight = round(1.0 / len(groq_keys), 2)
        for idx, key in enumerate(groq_keys):
            model = models[idx % len(models)]
            targets.append({
                "provider": "groq",
                "api_key": key,
                "override_params": {"model": model},
                "weight": weight,
            })
    elif virtual_keys:
        weight = round(1.0 / len(virtual_keys), 2)
        for idx, vk in enumerate(virtual_keys):
            model = models[idx % len(models)]
            targets.append({
                "virtual_key": vk,
                "override_params": {"model": model},
                "weight": weight,
            })
    else:
        targets = [
            {
                "provider": "groq",
                "override_params": {"model": "llama-3.3-70b-versatile"},
            }
        ]

    # Optional OpenAI Fallback Target
    if settings.OPENAI_API_KEY:
        targets.append({
            "provider": "openai",
            "api_key": settings.OPENAI_API_KEY,
            "override_params": {"model": "gpt-4o-mini"},
        })

    config_dict = {
        "strategy": {"mode": "loadbalance" if len(targets) > 1 else "single"},
        "targets": targets,
        "retry": {
            "attempts": 3,
            "on_status_codes": [429, 500, 502, 503, 504],
        },
        "cache": {"mode": "simple"},
    }

    headers = createHeaders(
        api_key=settings.PORTKEY_API_KEY,
        config=config_dict,
        metadata={
            "feature": feature,
            "_user": "rag-system",
            "environment": "production",
        },
    )
    headers["x-portkey-cache"] = "simple"
    return headers


# OpenAI-compatible client routed through Portkey.
# We use the OpenAI SDK directly because the native Portkey SDK does not
# surface a first-class config_id constructor parameter; the header-based
# approach works reliably with block_inline_config enabled.
portkey_client = OpenAI(
    api_key=settings.PORTKEY_API_KEY,
    base_url=PORTKEY_GATEWAY_URL,
    default_headers=_make_headers(),
)


def get_langchain_llm(feature: str = "rag") -> ChatOpenAI:
    """
    Returns a Portkey-backed ChatOpenAI - a drop-in for LangChain nodes.

    Why ChatOpenAI:
      Portkey is a proxy. It exposes an OpenAI-compatible endpoint at PORTKEY_GATEWAY_URL.
      ChatOpenAI supports base_url (points at Portkey) and default_headers (passes Portkey
      auth + saved-config reference). The @slug/model-name format is Portkey-specific - the
      upstream provider's own client does not understand it. Portkey is just in the middle.
    """
    return ChatOpenAI(
        api_key=settings.PORTKEY_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        model="llama-3.3-70b-versatile",
        default_headers=_make_headers(feature),
    )


def get_async_openai_client(feature: str = "rag") -> AsyncOpenAI:
    """
    Returns an async OpenAI client that routes through the Portkey gateway.
    Use this for non-LangChain async LLM calls (e.g. async FastAPI endpoints).
    """
    return AsyncOpenAI(
        api_key=settings.PORTKEY_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=_make_headers(feature),
    )


def extract_cache_status(response) -> str:
    """
    Pull x-portkey-cache-status from the response.

    The OpenAI SDK does not expose raw headers on parsed responses, so cache
    hit/miss tracking is best-effort. We inspect common attribute paths and
    fall back to 'MISS'.
    """
    for attr in ("_raw_response", "_response", "_http_response", "headers"):
        raw = getattr(response, attr, None)
        if raw is not None:
            headers = getattr(raw, "headers", None)
            if headers is not None:
                status = headers.get("x-portkey-cache-status", "")
                if status:
                    return status.upper()
    return "MISS"
