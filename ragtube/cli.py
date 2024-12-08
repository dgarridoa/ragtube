from typing import Annotated

import typer

from ragtube.chunk import ChunkTask
from ragtube.database import setting_engine
from ragtube.embedding import EmbeddingTask
from ragtube.params import get_params
from ragtube.retriever import create_index
from ragtube.settings import get_settings
from ragtube.transcript import VideoTranscriptTask

app = typer.Typer()


@app.command()
def update_index(
    channel_id: Annotated[
        list[str] | None,
        typer.Argument(
            help="Channel id, if not set channel_id from conf.yaml will be used"
        ),
    ] = None,
):
    """
    Add videos from a YouTube channel to the vector store
    """
    settings = get_settings()
    params = get_params()
    engine = setting_engine()
    proxies = (
        {"https": settings.https_proxy.get_secret_value()}
        if settings.https_proxy
        else None
    )
    transcript_task = VideoTranscriptTask(
        engine,
        channel_id or params.channel_id,
        settings.youtube_api_key.get_secret_value(),
        params.language,
        params.request_timeout,
        proxies,
    )
    chunk_task = ChunkTask(engine, params.chunk_size, params.chunk_overlap)
    embedding_task = EmbeddingTask(
        engine,
        params.embedding_model_name,
        params.embedding_model_kwargs,
        params.embedding_encode_kwargs,
    )

    transcript_task.launch()
    chunk_task.launch()
    embedding_task.launch()

    create_index(
        engine,
        params.index_hnsm_m,
        params.index_hnsm_ef_construction,
        params.index_hnsm_ef_searh,
    )


if __name__ == "__main__":
    app()
