# Project Analysis: Enterprise Agentic RAG

## 1. Information About the Project
This project is a production-grade, enterprise-level **Retrieval-Augmented Generation (RAG) system**. It is designed to accurately answer questions based on ingested documents while maintaining security, observability, and scalability. 

**Key Components and Features:**
*   **Orchestration:** Built with **LangChain** and **LangGraph**, allowing for cyclic reasoning, multi-step planning, and conversational memory via a graph-based agent architecture.
*   **LLM Gateway:** Uses **Portkey** to route LLM calls, providing automatic fallbacks (e.g., from OpenAI to Anthropic) and managing provider integrations efficiently.
*   **Security & Guardrails:** Integrates **NeMo Guardrails** to block off-topic queries, jailbreak attempts, and prompt injections *before* retrieval even happens.
*   **Vector Search & Reranking:** Uses **Qdrant Cloud** for high-performance vector search and **Jina AI Reranker API** to semantically rerank the retrieved documents, distinguishing true technical data from noisy data.
*   **Embeddings:** Employs Jina AI embeddings (`jina-embeddings-v3`) with a local fallback (`mxbai-embed-large-v1`).
*   **Document Processing:** Parses PDF, HTML, TXT, DOCX, and PPTX locally (without external OCR services) and chunks them for vectorization.
*   **Observability & Metrics:** Features full tracing with **Pydantic Logfire** and **LangSmith**, plus Prometheus metrics for monitoring RAG and guardrails performance.
*   **Interfaces:** Provides a synchronous `/query` FastAPI endpoint and a **Streamlit** user interface.
*   **Evaluation:** Includes a dedicated **RAGAS**-powered evaluation suite to test the pipeline's performance across multiple metrics.

---

## 2. How to Scale This with Free Models and APIs
To enhance this project and make it highly cost-effective (or entirely free to run), you can substitute the paid APIs with free or open-source alternatives:

### LLMs (Replacing OpenAI)
*   **Groq API:** Use Groq's free tier for lightning-fast inference on models like Llama 3 (8B/70B) or Mixtral. Portkey can easily route your requests to Groq instead of OpenAI.
*   **Local LLMs with Ollama:** If you have the hardware (a decent GPU or Apple Silicon), you can run models like `llama3` or `phi3` entirely locally using Ollama. Point your LangChain configuration to the local Ollama server, eliminating API costs and rate limits.
*   **HuggingFace Inference Endpoints / Together AI:** Utilize their free tiers for access to top-tier open-source models.

### Embeddings & Reranking (Replacing Jina AI API)
*   **Local Embeddings:** The project already supports `mxbai-embed-large-v1` as a local fallback. You can make this the primary embedding model using HuggingFace's `sentence-transformers` library. This runs locally and costs nothing.
*   **Local Reranking:** Replace the Jina AI Reranker API with a local cross-encoder model like `BAAI/bge-reranker-base` or `cross-encoder/ms-marco-MiniLM-L-6-v2` run via HuggingFace locally.

### Vector Database (Replacing Qdrant Cloud)
*   **Qdrant Local/Docker:** Instead of using Qdrant Cloud, you can spin up a Qdrant instance locally using Docker (`docker run -p 6333:6333 qdrant/qdrant`).
*   **ChromaDB / FAISS:** Switch the vector store backend to ChromaDB or FAISS, which can run completely locally and store indices as files on your disk.

### Observability
*   **Phoenix by Arize:** Instead of LangSmith (which has a free tier but can get expensive), you can use open-source alternatives like Arize Phoenix for local LLM tracing and evaluation.

---

## 3. How to Explain This Project in 1 Minute (Elevator Pitch)
"This project is a highly scalable, enterprise-grade AI assistant that securely answers questions based on your company's private documents. Think of it as a smart search engine for your internal data. 

When a user asks a question, the system first passes the request through strict security guardrails to block malicious or off-topic prompts. Then, it uses an intelligent planner to search through your ingested documents—like PDFs and Word files—using advanced vector search and semantic reranking to find the absolute most relevant information. Finally, it feeds that context to an LLM to generate a precise, accurate answer. 

It's built for production with a robust FastAPI backend, a user-friendly Streamlit chat interface, and full observability tracking every step to ensure accuracy and manage costs. Essentially, it's a secure, smart, and observable chat interface for any knowledge base."
