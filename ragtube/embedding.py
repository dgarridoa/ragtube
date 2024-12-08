from langchain_huggingface import HuggingFaceEmbeddings
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select

from ragtube.models import Chunk


def get_embedding_model(
    model_name: str = "BAAI/bge-large-en-v1.5",
    model_kwargs: dict | None = None,
    encode_kwargs: dict | None = None,
):
    model = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs if model_kwargs else {},
        encode_kwargs=encode_kwargs if encode_kwargs else {},
    )
    return model


class EmbeddingTask:
    def __init__(
        self,
        engine: Engine,
        model_name: str = "BAAI/bge-small-en-v1.5",
        model_kwargs: dict | None = None,
        encode_kwargs: dict | None = None,
    ):
        self.engine = engine
        self.model_name = model_name
        self.model_kwargs = model_kwargs
        self.encode_kwargs = encode_kwargs
        self.model = get_embedding_model(
            model_name=self.model_name,
            model_kwargs=self.model_kwargs,
            encode_kwargs=self.encode_kwargs,
        )

    def get_missing_chunks(self) -> list[Chunk] | None:
        with Session(self.engine) as session:
            statement = select(Chunk).where(col(Chunk.embedding).is_(None))
            chunks = session.exec(statement).all()
        if not chunks:
            return None
        return list(chunks)

    def add_embeddings(self, chunks: list[Chunk]) -> None:
        for chunk in chunks:
            chunk.embedding = self.model.embed_query(chunk.content)

    def launch(self):
        chunks = self.get_missing_chunks()
        if not chunks:
            return None
        with Session(self.engine) as session:
            self.add_embeddings(chunks)
            session.add_all(chunks)
            session.commit()
