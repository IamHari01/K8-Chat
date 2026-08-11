# Comprehensive Benchmark & Evaluation Report
**Project:** Kubernetes RAG Chatbot
**Date:** 2026-08-08 16:38:29

## 1. Executive Summary
This report details the empirical performance, retrieval quality, security guardrails, and latency evaluations conducted on the Kubernetes RAG platform. All metrics are measured from actual test executions.

## 2. System Architecture
- **API Framework:** FastAPI
- **LLM Gateway & Fallback:** Portkey AI
- **Vector Search:** Qdrant (Dense + RRF + Reranker)
- **Embeddings:** Jina AI
- **Guardrails:** NeMo Guardrails + Perimeter Security Firewall
- **Caching & Rate Limiting:** Upstash Redis
- **State Management:** Neon Serverless Postgres
- **Observability:** LangSmith, Logfire, Prometheus

## 3. Dataset Description
- **Domain:** Kubernetes Internal Documentation
- **Size:** 21 Golden QA Samples + Security Adversarial Suite
- **Categories:** Factual lookup, Configuration, Troubleshooting, Procedural, Jailbreaks, Off-topic attempts.

## 4. End-to-End RAG Quality Metrics

| Metric | Result |
|---|---:|
| Recall@5 | 80.0% |
| Recall@10 | 86.67% |
| MRR | 0.658 |
| NDCG@5 | 0.852 |
| Context Precision | 0.925 |
| Context Recall | 0.880 |
| Faithfulness | 0.945 |
| Answer Relevancy | 0.910 |

## 5. Retrieval Pipeline Ablation Study

| Configuration | Recall@10 | MRR | NDCG@5 | p95 Latency (ms) |
|---|---:|---:|---:|---:|
| Vector only | 86.67% | 0.605 | 0.793 | 4564.09 ms |
| Vector + RRF | 86.67% | 0.591 | 0.777 | 4564.52 ms |
| RRF + Reranker | 86.67% | 0.658 | 0.852 | 5608.05 ms |

## 6. Performance & Latency Breakdown

| Component | p50 Latency (ms) | p95 Latency (ms) |
|---|---:|---:|
| Total Request (Warm Cache) | 47.9 ms | 279.3 ms |
| Guardrail Check | 0.052 ms | 3.706 ms |
| Vector Search | 1596.88 ms | 4564.09 ms |
| RRF + Reranking | 943.1 ms | 1043.96 ms |

## 7. Redis Cache Efficiency

| Metric | Cold Cache | Warm Cache |
|---|---:|---:|
| p50 Latency | 44.38 ms | 47.9 ms |
| p95 Latency | 66.57 ms | 279.3 ms |
| Hit Rate | 0.0% | 100.0% |
| Latency Reduction | N/A | **-7.92%** |

## 8. Guardrail Security Evaluation

| Metric | Result |
|---|---:|
| Attack Detection Rate | **100.0%** |
| False Positive Rate | **0.0%** |
| False Negative Rate | **0.0%** |
| Guardrail p95 Latency | **3.706 ms** |

## 9. Load Testing & Concurrency

| Concurrency | Requests/sec (RPS) | p95 Latency (ms) | p99 Latency (ms) | Error Rate (%) |
|---:|---:|---:|---:|---:|
| 5 | 26.3 | 21.0 | 21.0 | 0.0% |
| 10 | 47.6 | 23.0 | 23.0 | 0.0% |
| 25 | 92.6 | 29.0 | 29.0 | 0.0% |
| 50 | 135.1 | 39.0 | 39.0 | 0.0% |
| 100 | 175.4 | 59.0 | 59.0 | 4.0% |

