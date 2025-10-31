from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from sqlalchemy import Index
from sqlalchemy.engine import Engine
from sqlmodel import (
    Session,
    select,
    text,
)

from ragtube.core.models import Chunk, Video

VECTOR_OPS = ["l1", "l2", "cosine"]


# TODO: ef_search
def create_index(
    engine: Engine,
    m: int = 16,
    ef_construction: int = 64,
    ef_search: int = 40,
    vector_ops: str = "l2",
):
    if vector_ops not in VECTOR_OPS:
        raise ValueError(f"Invalid vector_ops: {vector_ops}")
    index = Index(
        "chunk_index",
        Chunk.embedding,
        postgresql_using="hnsw",
        postgresql_with={"m": m, "ef_construction": ef_construction},
        postgresql_ops={"embedding": f"vector_{vector_ops}_ops"},
    )
    index.create(engine, checkfirst=True)


def drop_index(engine: Engine, index_name: str):
    with Session(engine) as session:
        session.connection().execute(
            text(f"DROP INDEX IF EXISTS {index_name}")
        )
        session.commit()


class Retriever(BaseRetriever):
    engine: Engine
    embedding_model: Embeddings
    vector_ops: str = "l2"
    results_to_retrieve: int = 5
    channel_id: str | None = None

    def model_post_init(self, __context):
        if self.vector_ops not in VECTOR_OPS:
            raise ValueError(f"Invalid vector_ops: {self.vector_ops}")

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        with Session(self.engine) as session:
            embedding = self.embedding_model.embed_query(query)
            statement = select(Chunk)
            if self.channel_id:
                statement = statement.join(Video).where(
                    Video.channel_id == self.channel_id
                )

            vector_ops = f"{self.vector_ops}_distance"
            distance_fn = getattr(Chunk.embedding, vector_ops)
            statement = statement.order_by(distance_fn(embedding)).limit(
                self.results_to_retrieve
            )

            docs_retrieved = session.exec(statement).all()
            docs_retrieved = [
                Document(
                    page_content=doc.content,
                    metadata={
                        "id": doc.id,
                        "video_id": doc.video.id,
                        "title": doc.video.title,
                        "publish_time": doc.video.publish_time,
                    },
                )
                for doc in docs_retrieved
            ]
        return docs_retrieved
