# Reranker Process: Jina AI & Cross-Encoder Fallback

## Overview
This document explains the two-stage retrieval process: initial vector search followed by semantic reranking using the Jina AI Reranker API, with a robust local fallback utilizing an open-source cross-encoder model.

## Justification
- **Primary (Jina AI `jina-reranker-v3`):** Vector search (bi-encoders) is fast but can sometimes miss nuanced semantic overlap. Reranking (cross-encoders) compares the query and document *together*, providing vastly superior accuracy. Jina's API is highly optimized for this.
- **Fallback (`cross-encoder/ms-marco-MiniLM-L-6-v2`):** To maintain enterprise reliability and reduce costs on failures, we implement a local fallback. This model, run via `sentence-transformers`, is lightweight, open-source, and free. It guarantees that even if the external API fails, the results are still semantically sorted before being sent to the LLM.

---

## 10 Common Questions & Answers

1. **What is the purpose of a reranker?**
   It takes the top `N` results from the vector database and re-scores them for relevance, filtering out noisy data that vector similarity missed.

2. **Why is cross-encoding better than vector search?**
   Vector search compares two isolated vectors. A cross-encoder analyzes the query and the document simultaneously, allowing attention mechanisms to see how specific words interact.

3. **Why use Jina AI primarily?**
   Jina's API provides top-of-the-line accuracy and handles the heavy compute required for cross-encoding, keeping our application server lightweight.

4. **What is the local fallback model?**
   We use `cross-encoder/ms-marco-MiniLM-L-6-v2`, a fast, open-source Microsoft model trained on a massive dataset of search queries.

5. **Is the fallback model free?**
   Yes, it runs locally via the HuggingFace `sentence-transformers` library and costs absolutely nothing in API fees.

6. **How does the system handle the transition?**
   If the Jina API throws an error (e.g., rate limit, timeout), a Python exception triggers the local cross-encoder to load and rerank the documents instead.

7. **Does the fallback add latency?**
   Yes, running a cross-encoder locally on CPU can add latency (e.g., 0.5s - 2s depending on document length), which is why Jina API is preferred for the primary route.

8. **Can I use the local reranker permanently?**
   Yes. If no Jina API key is provided, the system can be configured to default to the local MiniLM cross-encoder to keep costs at zero.

9. **Does reranking modify the documents?**
   No. It only changes the *order* in which the documents are presented, ensuring the most relevant ones are passed to the LLM as context.

10. **Why not rerank *all* documents?**
    Cross-encoders are computationally expensive. We only rerank the top `K` (e.g., top 10) results returned by the extremely fast Qdrant vector database.
