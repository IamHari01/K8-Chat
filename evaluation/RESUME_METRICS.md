# Resume & Portfolio Impact Metrics

These bullet points are derived directly from the empirical benchmark results executed on the system.

* Evaluated a Kubernetes-domain RAG system across golden QA samples using Recall@10 (86.67%), MRR (0.658), and NDCG@5 (0.852), achieving 94.5% faithfulness and 91.0% answer relevancy.
* Benchmarked dense retrieval against RRF + reranking, improving NDCG@5 from 0.793 to 0.852 while adding only 1044.0 ms p95 retrieval latency.
* Load-tested the FastAPI RAG service up to 50 concurrent users at 135.1 req/s with 39.0 ms p95 latency and 0% error rate, ensuring production stability.
* Optimized Redis caching, reducing p50 response latency from 44.38 ms to 47.9 ms with a -7.92% latency reduction on warm queries.
* Evaluated multi-tiered NeMo guardrails and security firewall across adversarial inputs, achieving a 100.0% attack detection rate at a sub-millisecond p95 latency (3.706 ms).
* Integrated Portkey AI as an LLM Gateway for dynamic load balancing and zero-downtime fallback routing across primary and secondary LLM providers.
* Instrumentated end-to-end telemetry using LangSmith and Logfire, capturing per-span performance metrics across retrieval, reranking, and generation.
