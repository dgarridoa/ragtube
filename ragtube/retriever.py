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

from ragtube.models import Chunk


def create_vector_extension(engine: Engine):
    with Session(engine) as session:
        session.connection().execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )
        session.commit()


# TODO: ef_search
def create_index(
    engine: Engine, m: int = 16, ef_construction: int = 64, ef_search: int = 40
):
    index = Index(
        "chunk_index",
        Chunk.embedding,
        postgresql_using="hnsw",
        postgresql_with={"m": m, "ef_construction": ef_construction},
        postgresql_ops={"embedding": "vector_l2_ops"},
    )
    index.create(engine, checkfirst=True)


class Retriever(BaseRetriever):
    engine: Engine
    embedding_model: Embeddings
    results_to_retrieve: int = 5

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        with Session(self.engine) as session:
            embedding = self.embedding_model.embed_query(query)
            docs_retrieved = session.exec(
                select(Chunk)
                .order_by(Chunk.embedding.l2_distance(embedding))
                .limit(self.results_to_retrieve)
            ).all()
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
