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
    embedding_model_name: str = "BAAI/bge-large-en-v1.5"
    embedding_model_kwargs: dict | None = None
    embedding_encode_kwargs: dict | None = None
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
    conf_file = os.path.join(PROJECT_DIR, "params.yaml")
    config = yaml.safe_load(pathlib.Path(conf_file).read_text())
    params = Params(**config)
    return params
