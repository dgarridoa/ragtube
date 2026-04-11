# RAGTube — Project Overview

**RAGTube** is a **Retrieval Augmented Generation (RAG)** application that lets you ask questions about YouTube video transcripts and get AI-powered answers, with references back to the source videos.

## How it works (high level)

1. **Ingest** — A CLI pipeline downloads transcripts from configured YouTube channels (via the YouTube Data API), splits them into overlapping chunks (~500 tokens each), generates vector embeddings (via Ollama's `bge-large` model), and stores everything in **PostgreSQL + pgvector** with an HNSW index.

2. **Query** — When a user asks a question through the web UI:
   - The query is embedded and the most similar transcript chunks are retrieved via vector similarity search.
   - Results are re-ranked with **FlashRank** for better precision.
   - The top chunks are fed as context to a local LLM (e.g. `llama3.2:3b` via **Ollama**), which generates a streamed answer.
   - The frontend displays the answer token-by-token alongside clickable source video references.

## Key components

| Layer | Tech |
|---|---|
| **Frontend** | Vanilla JS + Vite + shadcn/ui + Tailwind CSS |
| **Backend API** | FastAPI (streaming NDJSON responses) |
| **Data pipeline / CLI** | Typer CLI (`update_index` command) |
| **Embeddings & LLM** | Ollama (local, no external API calls) |
| **Vector search** | PostgreSQL + pgvector (HNSW index) |
| **Reranking** | FlashRank |
| **Orchestration** | LangChain |
| **Deployment** | Docker Compose, Traefik (reverse proxy + SSL), Watchtower (auto-updates) |

## Data model

- **Channel** → has many **Videos** → each video has **Captions** (raw transcript lines) and **Chunks** (token-split pieces with 1024-dim vector embeddings).

## API endpoints

- `GET /readiness` — health check
- `GET /channel` — list available YouTube channels
- `GET /rag?input=...&channel_id=...` — stream a RAG response (context + answer tokens as NDJSON)

## Configuration

- **`params.yaml`** — runtime config (model names, chunk sizes, HNSW parameters, retrieval/rerank thresholds)
- **`.env`** — secrets (YouTube API key, DB credentials, hostname)

## Notable design decisions

- **Fully local LLMs** via Ollama — no data leaves the server
- **Idempotent ingestion** — safe to re-run; only new videos are processed
- **Streaming end-to-end** — tokens stream from Ollama → FastAPI → browser for instant feedback
- **Reranking** improves precision on top of raw vector similarity

In short: it's a self-hosted, privacy-friendly system for chatting with YouTube content using semantic search and a local LLM.
