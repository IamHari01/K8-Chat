import time

import logfire
import requests
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.config import settings

_JINA_RERANK_URL = "https://api.jina.ai/v1/rerank"
_JINA_RERANK_MODEL = "jina-reranker-v3"
_FALLBACK_RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_ranker = None
_fallback_ranker = None


class _JinaReranker:
    """Thin wrapper around the Jina Reranker API."""

    def rerank(self, query: str, documents: list[str], top_n: int) -> list[str]:
        """Score and reorder documents against the query via the Jina API."""
        response = requests.post(
            _JINA_RERANK_URL,
            headers={
                "Authorization": f"Bearer {settings.JINA_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": _JINA_RERANK_MODEL,
                "query": query,
                "documents": documents,
                "top_n": top_n,
                "return_documents": True,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()

        results = payload.get("results", [])
        # Results are already sorted by relevance_score descending
        reranked_docs = []
        for res in results[:top_n]:
            doc_obj = res.get("document")
            doc_text = None
            if isinstance(doc_obj, dict):
                doc_text = doc_obj.get("text") or str(doc_obj)
            elif isinstance(doc_obj, str):
                doc_text = doc_obj

            if doc_text is None:
                # Fallback to original index if document text is missing
                index = res.get("index")
                if index is not None and 0 <= index < len(documents):
                    doc_text = documents[index]
            if doc_text is not None:
                reranked_docs.append(str(doc_text))

        return reranked_docs


def _get_ranker() -> _JinaReranker:
    """Returns the Jina Reranker wrapper (lazy singleton)."""
    global _ranker
    if _ranker is None:
        logfire.info("🧠 Initializing Jina Reranker v3 via API...")
        _ranker = _JinaReranker()
    return _ranker


def _get_fallback_ranker():
    """Returns the local CrossEncoder fallback model (lazy singleton)."""
    global _fallback_ranker
    if _fallback_ranker is None:
        logfire.info(f"🧠 Initializing Local Fallback Reranker ({_FALLBACK_RERANK_MODEL})...")
        from sentence_transformers import CrossEncoder
        _fallback_ranker = CrossEncoder(_FALLBACK_RERANK_MODEL)
    return _fallback_ranker


def _fallback_rerank(query: str, documents: list[str], top_n: int) -> list[str]:
    """Score and reorder documents against the query via the local CrossEncoder."""
    if not documents:
        return []
    ranker = _get_fallback_ranker()
    # Create pairs of (query, document)
    pairs = [[query, doc] for doc in documents]
    scores = ranker.predict(pairs)
    
    # Pair documents with their scores and sort descending
    doc_score_pairs = list(zip(documents, scores))
    doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
    
    return [doc for doc, _ in doc_score_pairs[:top_n]]


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
    before_sleep=before_sleep_log(logfire, "warning"),
)
def _rerank(query: str, documents: list[str], top_n: int) -> list[str]:
    """Core Jina API reranking with retry on transient failures."""
    ranker = _get_ranker()
    return ranker.rerank(query, documents, top_n)


def rerank_documents(query: str, documents: list[str], top_n: int = 5) -> list[str]:
    """
    Refines retrieval results by re-scoring documents against the query semantically.
    Retries transient failures and falls back to a local open-source cross-encoder if
    reranking ultimately fails or the API key is missing.
    """
    if not documents:
        return []

    # Clean query if it contains a URL from planner
    clean_q = re.sub(r"https?://\S+", "", query).strip()
    if not clean_q:
        clean_q = query.replace("/", " ").replace("-", " ").strip()

    if not settings.JINA_API_KEY:
        logfire.warning("⚠️ JINA_API_KEY not set — using local fallback reranker.")
        return _fallback_rerank(clean_q, documents, top_n)

    start_time = time.time()
    logfire.info(f"📡 [Reranker] Sending {len(documents)} docs to Jina Reranker API...")

    try:
        reranked_docs = _rerank(clean_q, documents, top_n)
        duration = time.time() - start_time
        logfire.info(f"✅ [Reranker] Done in {duration:.2f}s.")
        return reranked_docs
    except Exception as e:
        logfire.error(f"❌ [Reranker] Semantic Reranking Failed after retries: {e}")
        logfire.info("🔄 Falling back to local open-source reranker...")
        return _fallback_rerank(clean_q, documents, top_n)
