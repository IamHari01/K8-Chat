# Docker & Scaling Process

## Overview
This document outlines how the application is containerized using Docker and how to scale the RAG pipeline horizontally using open-source, free-tier services.

## Justification
- **Docker Compose:** Containerization ensures the application runs identically across development, staging, and production. It packages the FastAPI server, Streamlit UI, and local model weights into self-contained units.
- **Max Scaling on Open Source Free Tier:** To handle massive traffic for free:
  1. **Stateless API:** The FastAPI backend is entirely stateless. State is managed by Qdrant and Neon Postgres.
  2. **Load Balancing:** You can deploy multiple replicas of the FastAPI Docker container behind an Nginx or Traefik reverse proxy.
  3. **Local Models:** By forcing the use of local `mxbai` embeddings and `MiniLM` rerankers inside the containers, you completely avoid 3rd-party API rate limits.
  4. **Groq via Portkey:** Utilize the multi-key Portkey config to load-balance LLM requests, essentially multiplying your free tier limits.

---

## 10 Common Questions & Answers

1. **Why use Docker for this project?**
   It bundles Python, libraries, local models, and system dependencies into a single image, eliminating "it works on my machine" issues.

2. **What does `docker-compose.yml` do?**
   It orchestrates the startup of both the FastAPI backend and the Streamlit frontend, ensuring they can communicate over an internal network.

3. **How do I start the services with Docker?**
   Simply run `docker-compose up --build -d` in the root directory.

4. **How do we scale this horizontally?**
   You can scale the API container using `docker-compose up --scale api=3 -d`, and put an Nginx container in front to round-robin traffic to them.

5. **Where is state stored if the API is stateless?**
   Conversational memory is in serverless Postgres (Neon), rate limits in Redis (Upstash), and vectors in Qdrant—all external.

6. **How do we maximize the free tier?**
   By entirely ditching Jina AI and using the local sentence-transformer models built into the Docker image, eliminating those API costs.

7. **Can the Docker container use my GPU?**
   Yes, by passing the `--gpus all` flag to `docker run`, or configuring `deploy.resources` in `docker-compose.yml` to utilize NVIDIA hardware for local model inference.

8. **How does this affect LLM scaling?**
   Since LLMs are routed via Portkey to Groq, the FastAPI container doesn't do the heavy LLM lifting, making it very CPU-efficient and easy to scale.

9. **What if my container crashes?**
   Docker's `restart: always` policy will instantly spin it back up. Since the app is stateless, no conversation data is lost.

10. **Can I deploy this on free cloud providers?**
    Yes, you can push the Docker image to platforms like HuggingFace Spaces, Render (free tier), or Google Cloud Run (free tier quota) for highly cost-effective hosting.
