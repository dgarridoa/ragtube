# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAGTube is a RAG (Retrieval Augmented Generation) application for querying YouTube transcriptions. It uses pgvector for vector storage, Ollama for embeddings/chat, FastAPI for the backend, and a Vanilla JS + shadcn/ui frontend.

## Commands

### Backend (run from `backend/`)

```bash
uv sync --all-extras                          # Install dependencies
uv run uvicorn ragtube.api.app:app --host 0.0.0.0 --port 5000 --log-config log_config.yaml  # Run API
uv run python -m ragtube.cli.app update_index # Ingest transcripts
uv run pytest                                 # Run all tests
uv run pytest tests/unit/services/test_retriever.py  # Single test file
uv run pytest --cov=ragtube --cov-report=html # Tests with coverage
uv run ruff check --fix ragtube/              # Lint
uv run ruff format ragtube/                   # Format
uv run pyright ragtube/                          # Type check
```

### Frontend (run from `frontend/`)

```bash
npm install                   # Install dependencies
npm run dev                   # Dev server on port 8501
npm run build                 # Production build
npm run format                # Format with Prettier
npm run format:check          # Check formatting
```

### Docker

```bash
docker compose up             # Run full stack
```

## Architecture

### Backend (`backend/ragtube/`)

- **`api/app.py`** - FastAPI app with endpoints: `/readiness`, `/channel`, `/rag`
- **`cli/app.py`** - Typer CLI for data ingestion (`update_index`)
- **`core/`** - Database engine (`database.py`), SQLModel schemas (`models.py`), YAML config (`params.py`), env secrets (`settings.py`)
- **`data/`** - YouTube transcript fetching (`transcript.py`) and text chunking (`chunk.py`)
- **`services/`** - RAG pipeline: embedding (Ollama) -> retrieval (pgvector HNSW) -> rerank (FlashRank) -> chat (Ollama via LangChain)

**RAG request flow:** Query hits `/rag` -> embed query -> pgvector HNSW retrieval -> FlashRank reranking -> Ollama generates answer -> NDJSON streaming response (`{"context": [...]}` then `{"answer": "..."}` tokens).

**DB models:** Channel -> Video -> Caption -> Chunk (with `embedding: Vector`). Tables auto-created by SQLModel (`create_all`), no migration tool.

### Frontend (`frontend/src/`)

Vanilla JS SPA with Vite, Tailwind CSS, and shadcn/ui components. Key files: `main.js` (entry), `api/client.js` (API client with NDJSON streaming), `components/chat-interface.js`, `components/channel-selector.js`.

### Configuration

- **`.env`** (root) - Secrets: `YOUTUBE_API_KEY`, `DB_*`, `HOSTNAME`, `OLLAMA_HOST`
- **`params.yaml`** (root) - App config: channel IDs, model names, chunk sizes, HNSW params, rerank thresholds. Searched in: env var path -> package dir -> repo root -> `/app/`
- Both are cached via `@lru_cache` - restart required after edits

### Pre-commit hooks

Ruff linting/formatting and basic file hygiene (trailing whitespace, end-of-file, YAML check) run automatically on commit.

### CI/CD

- **PR pipeline** (`.github/workflows/onpr.yaml`): ruff + pytest with coverage (backend), Prettier check (frontend)
- **Release pipeline** (`.github/workflows/onrelease.yaml`): Multi-arch Docker builds on tag push, published to Docker Hub and GHCR
