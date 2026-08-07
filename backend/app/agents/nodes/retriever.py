import logfire

from app.agents.state import AgentState
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.ranking_service import rerank_documents


def retrieve_node(state: AgentState):
    """
    Performs vector search and semantic reranking for technical queries.
    """
    query = state["current_query"]

    # Standard Retrieval Logic
    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")
        raw_results = search_enterprise_knowledge(query, limit=15)
        logfire.info(f"Retrieved {len(raw_results)} candidates from Vector DB")

        doc_contents = [doc["content"] for doc in raw_results]

        with logfire.span("⚖️ Semantic Reranking & Layer 3 Security Inspection"):
            reranked_contents = rerank_documents(query, doc_contents, top_n=5)
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")

            # Layer 3: Context Sanity Guardrail (Scans chunks for indirect prompt injections)
            from app.guardrails.security_firewall import sanitize_retrieved_context
            sanitized_contents = sanitize_retrieved_context(reranked_contents)

        formatted_docs = [f"CONTENT: {doc}" for doc in sanitized_contents]

    return {
        "documents": formatted_docs,
        "status": "Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"],
    }
