# Embedding Process: Jina AI & Sentence-Transformers Fallback

## Overview
This document outlines the usage of Jina AI for generating dense vector embeddings, with a local open-source fallback utilizing the `sentence-transformers` library and the `mxbai-embed-large-v1` model.

## Justification
- **Primary (Jina AI `jina-embeddings-v3`):** Jina provides state-of-the-art 1024-dimensional embeddings that capture deep semantic meaning, particularly optimized for long contexts and enterprise documents. 
- **Fallback (`mxbai-embed-large-v1`):** In the event of a network failure, rate limit, or exhausted API credits, the system must not crash. We utilize a highly capable open-weight model (`mixedbread-ai/mxbai-embed-large-v1`) running entirely locally via `sentence-transformers`. This ensures zero API costs on fallback and guarantees uninterrupted service for the RAG pipeline.

---

## 10 Common Questions & Answers

1. **What is an embedding?**
   An embedding is a mathematical representation (a vector of numbers) of text that captures its semantic meaning.

2. **Why use Jina AI as the primary?**
   Jina's v3 embeddings offer top-tier performance on the MTEB benchmark, natively supporting long documents and generating highly precise 1024-dim vectors.

3. **What happens if Jina AI goes down?**
   The application intercepts the API error and automatically loads the local `mxbai-embed-large-v1` model using `sentence-transformers` to continue processing.

4. **Is the local fallback model free?**
   Yes, it is open-weight and runs locally on your machine's CPU/GPU, incurring no external API costs.

5. **Will the local model be as good as Jina?**
   `mxbai-embed-large` is a highly competitive model. While slightly less capable than Jina v3 on edge cases, it provides excellent baseline retrieval accuracy.

6. **Are the dimensions the same?**
   Yes, both Jina AI v3 and `mxbai-embed-large-v1` output 1024-dimensional vectors, ensuring compatibility with the vector database.

7. **How does the code know when to fallback?**
   A retry mechanism (using the `tenacity` library) attempts the Jina API call. If all retries fail, it catches the exception and routes texts to the local model.

8. **Does the local model require a GPU?**
   It benefits greatly from a GPU (CUDA/MPS) but can run on a CPU. `sentence-transformers` automatically detects and utilizes the available hardware.

9. **Can we use *only* the local model to save money?**
   Absolutely. By simply removing the `JINA_API_KEY` from the `.env` file, the system defaults entirely to the free local fallback.

10. **How do we store these embeddings?**
    The generated 1024-dim vectors are pushed to Qdrant Cloud alongside their metadata for fast nearest-neighbor semantic search.
