import glob
import json
import os
import re
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


def _search_local_docs(query: str, limit: int = 8) -> list[dict]:
    """Fallback search over local ingested JSON documents when Qdrant Cloud is offline."""
    words = [w.lower() for w in re.findall(r"\w+", query) if len(w) > 2]
    scored_chunks = []
    base_dir = os.path.join(os.getcwd(), "processed_data", "true")
    if not os.path.exists(base_dir):
        return []

    for fname in os.listdir(base_dir):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(base_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                source_name = fname.replace(".json", "")
                text_blocks = []
                if isinstance(data, list):
                    text_blocks = [str(item) for item in data]
                elif isinstance(data, dict):
                    for k, v in data.items():
                        if isinstance(v, list):
                            text_blocks.extend([str(item) for item in v])
                        elif isinstance(v, str):
                            text_blocks.append(v)

                for block in text_blocks:
                    block_lower = block.lower()
                    score = sum(block_lower.count(w) for w in words)
                    if score > 0:
                        scored_chunks.append(
                            {"content": block, "source": source_name, "score": float(score)}
                        )
        except Exception:
            pass

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunks[:limit]


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
    Uses modern query_points with fallback to local ingested docs if Qdrant is unreachable.
    """
    try:
        res = _search_enterprise_knowledge(query, limit=limit)
        if res:
            return res
    except Exception as e:
        logfire.warning(f"⚠️ Qdrant search unavailable ({e}); using local document retriever fallback.")

    return _search_local_docs(query, limit=limit)

