import logfire
from qdrant_client import QdrantClient
from qdrant_client.http import models
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_exponential

from app.config import settings
from app.services.retrieval.embedding import embed_query, get_embedding_dim

# Initialize Qdrant Client
client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)


_collection_checked = False


def ensure_collection_exists():
    """Ensure the target Qdrant collection exists before search/upsert."""
    global _collection_checked
    if _collection_checked:
        return True
    try:
        if not client.collection_exists(settings.QDRANT_COLLECTION):
            dim = get_embedding_dim()
            client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )
            logfire.info(f"Created Qdrant collection '{settings.QDRANT_COLLECTION}' ({dim}-dim).")
        _collection_checked = True
        return True
    except Exception as e:
        logfire.warning(f"Collection check warning: {e}")
        return False


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    reraise=True,
    before_sleep=before_sleep_log(logfire, "warning"),
)
def _search_enterprise_knowledge(query: str, limit: int = 8):
    """Internal search with retry logic."""
    ensure_collection_exists()
    query_vector = embed_query(query)

    response = client.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True,
    )

    results = []
    for res in response.points:
        results.append(
            {"content": res.payload.get("text", ""), "source": res.payload.get("source", "Unknown"), "score": res.score}
        )

    return results


def search_enterprise_knowledge(query: str, limit: int = 8):
    """
    Performs a high-precision search in the enterprise knowledge base.
    Uses modern query_points. Degrades gracefully if collection is empty.
    """
    try:
        return _search_enterprise_knowledge(query, limit=limit)
    except Exception as e:
        logfire.warning(f"⚠️ Qdrant search returned empty: {e}")
        return []
