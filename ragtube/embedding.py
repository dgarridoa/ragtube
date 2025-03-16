from langchain_ollama.embeddings import OllamaEmbeddings
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select
from tqdm import tqdm

from ragtube.models import Chunk


def get_embedding_model(model_name: str = "bge-large", num_ctx: int = 512):
    model = OllamaEmbeddings(model=model_name, num_ctx=num_ctx)
    return model


class EmbeddingTask:
    def __init__(
        self,
        engine: Engine,
        model_name: str = "bge-large",
        num_ctx: int = 512,
    ):
        self.engine = engine
        self.model = get_embedding_model(
            model_name=model_name, num_ctx=num_ctx
        )

    def get_missing_chunks(self) -> list[Chunk] | None:
        with Session(self.engine) as session:
            statement = select(Chunk).where(col(Chunk.embedding).is_(None))
            chunks = session.exec(statement).all()
        if not chunks:
            return None
        return list(chunks)

    def add_embeddings(self, chunks: list[Chunk]) -> None:
        for chunk in tqdm(chunks, desc="Embeddings"):
            chunk.embedding = self.model.embed_query(chunk.content)

    def launch(self):
        chunks = self.get_missing_chunks()
        if not chunks:
            return None
        with Session(self.engine) as session:
            self.add_embeddings(chunks)
            session.add_all(chunks)
            session.commit()
