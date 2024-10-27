import pathlib
from functools import lru_cache

import yaml
from pydantic import BaseModel


class Params(BaseModel):
    channel_id: str | list[str]
    language: str = "en"
    request_timeout: int = 60
    request_proxies: dict | None = None
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_size: int = 384
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_model_kwargs: dict | None = None
    embedding_encode_kwargs: dict | None = None
    index_hnsm_m: int = 16
    index_hnsm_ef_construction: int = 64
    index_hnsm_ef_searh: int = 40
    results_to_retrieve: int = 5
    chat_model_name: str = "llama3.1:8b"
    chat_temperature: float = 0.0
    chat_max_tokens: int = 500


@lru_cache
def get_params() -> Params:
    conf_file = "conf.yaml"
    config = yaml.safe_load(pathlib.Path(conf_file).read_text())
    params = Params(**config)
    return params
