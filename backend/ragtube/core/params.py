import os
import pathlib
from functools import lru_cache

import yaml
from pydantic import BaseModel

from ragtube import PROJECT_DIR


class Params(BaseModel):
    channel_id: str | list[str]
    language: str = "en"
    request_timeout: int = 60
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_size: int = 384
    embedding_model_name: str = "bge-large"
    embedding_num_ctx: int = 512
    index_hnsm_m: int = 16
    index_hnsm_ef_construction: int = 64
    index_hnsm_ef_searh: int = 40
    index_vector_ops: str = "l2"
    results_to_retrieve: int = 5
    rerank_model_name: str = "rank-T5-flan"
    rerank_score_threshold: float = 0.1
    chat_model_name: str = "llama3.1:8b"
    chat_temperature: float = 0.0
    chat_max_tokens: int = 500


@lru_cache
def get_params() -> Params:
    env_path = os.environ.get("RAGTUBE_PARAMS_FILE")
    candidates = [
        env_path,
        os.path.join(PROJECT_DIR, "params.yaml"),
        os.path.abspath(os.path.join(PROJECT_DIR, "..", "params.yaml")),
        "/app/params.yaml",
    ]
    for path in candidates:
        if path and os.path.exists(path):
            config = yaml.safe_load(pathlib.Path(path).read_text())
            return Params(**config)
    raise FileNotFoundError(
        "params.yaml not found. Searched: "
        + ", ".join([p for p in candidates if p])
    )
