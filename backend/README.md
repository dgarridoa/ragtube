# RAGTube Backend

A high-performance backend for RAGTube built with **FastAPI**, **SQLModel**, **pgvector**, and **Ollama**.

## ✨ Features

- 🚦 **Health Checks** - `/readiness` endpoint for container orchestration
- 📚 **Channel Management** - List available YouTube channels via `/channel`
- 🔎 **Vector Retrieval** - HNSW index on pgvector with configurable parameters
- 🎯 **Scoped Search** - Optional `channel_id` filter for per-channel retrieval
- 🧠 **Ollama Integration** - Local embeddings and chat completion
- 📊 **FlashRank Reranking** - Improves retrieval precision
- 📡 **Streaming Responses** - NDJSON streaming from `/rag` endpoint
- ⚙️ **Flexible Config** - Runtime `params.yaml` + `.env` for secrets
- 🔧 **CLI Tools** - Typer-based ingestion pipeline

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- [Ollama](https://ollama.com/download) running locally or via Docker
- YouTube API key

### Installation

1. **Install uv (Python package manager):**

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Set up Python 3.11:**

   ```bash
   uv python install 3.11
   uv pin 3.11
   ```

3. **Install dependencies:**

   ```bash
   uv sync --all-extras
   ```

4. **Configure environment:**

   Create a `.env` file in the **project root** (see Configuration below).

### Running Locally

1. **Start PostgreSQL with pgvector:**

   ```bash
   docker run \
     --name ragtube-postgres \
     -p 5432:5432 \
     -d \
     -e POSTGRES_HOST_AUTH_METHOD=trust \
     pgvector/pgvector:pg16
   ```

2. **Start Ollama and pull models:**

   ```bash
   ollama serve
   ollama pull llama3.2:3b    # or your chat_model_name from params.yaml
   ollama pull bge-large      # or your embedding_model_name
   ```

3. **Populate the database (CLI):**

   ```bash
   uv run python -m ragtube.cli update_index
   ```

4. **Start the API:**

   ```bash
   uv run uvicorn ragtube.api:app --host 0.0.0.0 --port 5000 --log-config log_config.yaml
   ```

5. **Open your browser:**
   - API: http://localhost:5000
   - OpenAPI Docs: http://localhost:5000/docs

### Running with Docker Compose

From the **project root**:

```bash
docker compose up
```

For macOS with native Ollama (GPU via Metal):

```bash
docker compose -f docker-compose-mac.yaml up
```

## 🛠️ Technology Stack

### Core Technologies

- **FastAPI** - Modern, fast web framework
- **SQLModel** - SQL databases with Python type hints
- **pgvector** - Vector similarity search in PostgreSQL
- **Ollama** - Local LLM serving (embeddings + chat)
- **LangChain** - LLM orchestration framework
- **FlashRank** - Ultra-fast reranking

### Dependencies

- **Typer** - CLI application framework
- **Pydantic** - Data validation using Python type annotations
- **uvicorn** - ASGI server for FastAPI
- **youtube-transcript-api** - Fetch YouTube transcripts

## 📁 Project Structure

```
backend/
├── pyproject.toml              # Python dependencies and project metadata
├── log_config.yaml             # Logging configuration
├── Dockerfile                  # Container build definition
└── ragtube/
    ├── api/
    │   └── app.py             # FastAPI application and endpoints
    ├── cli/
    │   └── app.py             # Typer CLI for data ingestion
    ├── core/
    │   ├── database.py        # SQLModel engine and session management
    │   ├── models.py          # Database table schemas
    │   ├── params.py          # params.yaml loader with multi-path resolution
    │   ├── settings.py        # .env loader using Pydantic Settings
    │   └── utils.py           # Shared utilities
    ├── data/
    │   ├── transcript.py      # YouTube transcript fetching
    │   └── chunk.py           # Text chunking logic
    ├── services/
    │   ├── embedding.py       # Ollama embedding generation
    │   ├── retriever.py       # pgvector HNSW retrieval
    │   ├── rerank.py          # FlashRank reranking
    │   ├── prompt.py          # LangChain prompt templates
    │   ├── chat.py            # Ollama chat model integration
    │   └── rag.py             # RAG chain orchestration
    ├── ui/
    │   └── app.py             # Legacy Streamlit UI
    └── tests/
        └── unit/              # Unit tests with pytest
```

## 🔧 Configuration

### Environment Variables (.env)

Create a `.env` file in the **repository root** with the following:

```bash
YOUTUBE_API_KEY=<your-youtube-api-key>
# HTTPS_PROXY=http://<user>:<password>@<host>:<port> # Optional for CI/CD
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost # Use 'postgres' for Docker Compose
DB_PORT=5432
DB_NAME=postgres
HOSTNAME=localhost
# OLLAMA_HOST=http://localhost:11434 # Optional override
```

Get a YouTube API Key: https://developers.google.com/youtube/v3/getting-started

### Parameters (params.yaml)

Application behavior is controlled via **root-level** `params.yaml`. The backend resolves it in this order:

1. `RAGTUBE_PARAMS_FILE` environment variable (if set)
2. `PROJECT_DIR/params.yaml` (backend package directory)
3. `../params.yaml` (repository root)
4. `/app/params.yaml` (Docker mount point)

Key Parameters:

- `channel_id`: List of string, the channel IDs to download transcriptions from.
- `language`: String, the language of the transcriptions.
- `request_timeout`: Integer, timeout in seconds for HTTP requests to retrieve list of videos of a channel and get transcriptions from a video.
- `chunk_size`: Integer, the maximum number of words in a chunk, used to split transcriptions in chunks.
- `chunk_overlap`: Integer, the number of words to overlap between chunks.
- `embedding_size`: Integer, it represents the dimensionality of the embeddings provided by the chosen model and determines the size of the embedding array column in the `chunk` table.
- `embedding_model_name`: String, the name of the model used to compute the embeddings, it must be a model supported by [`ollama`](https://ollama.com/search?c=embedding).
- `embedding_num_ctx`: String, size of the context window used to generate the next token, must not be greater than the maximum context window size of the model.
- `index_hnsm_m`: Integer, `m` parameter of the HNSW index.
- `index_hnsw_ef_construction`: Integer, `ef_construction` parameter of the HNSW index.
- `index_hnsw_ef_search`: Integer, `ef_search` parameter of the HNSW index.
- `index_vector_ops`: String, the name of the vector operations to use, it must be a vector operation supported by `pgvector`.
- `results_to_retrieve`: Integer, the number of approximate nearest neighbors to retrieve from the HNSW index.
- `rerank_model_name`: String, the name of the model used to rerank the results retrieve by the HNSW index, it must be a model supported by [`flashrank`](https://github.com/PrithivirajDamodaran/FlashRank).
- `rerank_score_threshold`: Integer, the minimum rerank score required for a result from the HNSW index to be presented to the user.
- `chat_model_name`: String, the name of the model used to generate responses based on a provided question and its corresponding retrieved context. The model must be one of those supported by [`ollama`](https://ollama.com/search?c=chat).
- `chat_temperature`: Float, the temperature used to sample tokens from the chat model.
- `chat_max_tokens`: Integer, the maximum number of tokens to generate from the chat model.

⚠️ The backend caches `params.yaml` in memory. Restart the API/CLI after changes.

## 📖 API Reference

### Base URL

- Local: `http://localhost:5000`
- Docker Compose: `http://localhost:5000` (via Traefik)

### Endpoints

#### `GET /readiness`

Health check for container orchestration.

Response:
```json
{ "status": "ok" }
```

#### `GET /channel`

List all available YouTube channels in the database.

Response:
```json
[
  { "id": "UCUyeluBRhGPCW4rPe_UvBZQ", "title": "ThePrimeTime" },
  { "id": "UCSHZKyawb77ixDdsGog4iWA", "title": "Lex Fridman" }
]
```

#### `GET /rag`

Stream RAG responses as NDJSON.

Query Parameters:
- `input` (required): User question
- `channel_id` (optional): Filter retrieval to specific channel

Response: `application/x-ndjson` stream

Each line is a JSON object:
- `{"context": [...]}` - Retrieved document chunks (sent once)
- `{"answer": "..."}` - Incremental answer tokens (streamed)

Example Request:
```bash
curl -N "http://localhost:5000/rag?input=What%20is%20agile%3F"
```

Example Response Stream:
```ndjson
{"context":[{"id":1,"video_id":"Guy5D3PJlZk","title":"I Interviewed Uncle Bob","publish_time":"2024-08-09T16:03:23","content":"..."}]}
{"answer":"Agile is"}
{"answer":" a methodology"}
{"answer":" for iterative development..."}
```

### CORS

Allowed origins are derived from `HOSTNAME` in `.env`:
- `localhost` → allows `http://localhost:8501`
- Custom domain → allows `https://<HOSTNAME>`

## 🖥️ CLI Reference

Typer-based CLI handles data ingestion, chunking, embedding, and indexing.

### Commands

#### `update_index [CHANNEL_ID...]`

Download transcripts, chunk, embed, and build/update the HNSW index.

Arguments:
- `CHANNEL_ID` (optional): Override `channel_id` from `params.yaml`

Examples:
```bash
# Use channel_id from params.yaml
uv run python -m ragtube.cli update_index

# Ingest specific channels
uv run python -m ragtube.cli update_index UC_x5XG1OV2P6uZZ5FSM9Ttw UCsBjURrPoezykLs9EqgamOA

# Re-run to update (idempotent - only processes missing data)
docker compose run --rm db-init
```

What it does:
1. Creates tables: `channel`, `video`, `caption`, `chunk`
2. Lists videos from specified channels (YouTube Data API v3)
3. Downloads missing transcripts (youtube-transcript-api)
4. Chunks transcripts (overlapping windows)
5. Computes embeddings for chunks (Ollama)
6. Creates HNSW index if it doesn't exist

## 🧪 Testing

### Run Unit Tests

1. Create `.env-test` file (same format as `.env`)
2. Ensure PostgreSQL is running
3. Run pytest:

```bash
uv run pytest
```

### Test Coverage

```bash
uv run pytest --cov=ragtube --cov-report=html
```

## 🐛 Troubleshooting

### Common Issues

1. **"params.yaml not found"**
   - Ensure `params.yaml` exists in the repository root
   - Verify `RAGTUBE_PARAMS_FILE` env var if using a custom path

2. **"Cannot connect to database"**
   - Verify PostgreSQL is running: `docker ps | grep postgres`
   - Check `DB_HOST` in `.env` (`localhost` for local, `postgres` for Docker Compose)
   - Test connection: `psql -h localhost -U postgres -d postgres`

3. **"Ollama API error"**
   - Ensure Ollama is running: `curl http://localhost:11434`
   - Verify models are pulled: `ollama list`
   - Check `OLLAMA_HOST` env var (default: `http://localhost:11434`)

4. **Params not updating**
   - Backend caches `params.yaml` via `@lru_cache`
   - Restart the API/CLI process after changes

5. **Streaming not working**
   - Ensure client supports NDJSON (`application/x-ndjson`)
   - Use `-N` flag with curl to disable buffering: `curl -N ...`

### Development Tips

- Use `/docs` endpoint to explore OpenAPI schema interactively
- Check logs with `docker compose logs -f api`
- Monitor Ollama with `ollama ps`
- Inspect database: `docker exec -it ragtube-db psql -U postgres`

## 📚 References

- pgvector: https://github.com/pgvector/pgvector
- pgvector Python SDK: https://github.com/pgvector/pgvector-python
- Ollama models: https://ollama.com/library
- FastAPI: https://fastapi.tiangolo.com/
- LangChain: https://python.langchain.com/

---

For deployment, orchestration, and architecture details, see the **root README**.
