from typing import Annotated

import typer

from ragtube.core.database import setting_engine
from ragtube.core.params import get_params
from ragtube.core.settings import get_settings
from ragtube.data.chunk import ChunkTask
from ragtube.data.transcript import VideoTranscriptTask
from ragtube.services.embedding import EmbeddingTask
from ragtube.services.retriever import create_index

app = typer.Typer()


@app.command()
def update_index(
    channel_id: Annotated[
        list[str] | None,
        typer.Argument(
            help="Channel id, if not set channel_id from params.yaml will be used"
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
        {"https_url": settings.https_proxy.get_secret_value()}
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
        engine, params.embedding_model_name, params.embedding_num_ctx
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
