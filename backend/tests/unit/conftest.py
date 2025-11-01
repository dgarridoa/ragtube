from typing import Generator
from unittest.mock import patch

import pytest
from langchain_core.embeddings import DeterministicFakeEmbedding
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, text
from sqlmodel.pool import StaticPool

from ragtube.core.settings import Settings


@pytest.fixture(scope="session", autouse=True)
def mock_embedding_size():
    from ragtube.core.models import Chunk

    Chunk.__table__.columns["embedding"].type.dim = 2  # type: ignore

    with patch("ragtube.models.Chunk", Chunk):
        yield


@pytest.fixture(scope="session", autouse=True)
def mock_get_embedding_model():
    with patch(
        "ragtube.embedding.get_embedding_model",
        return_value=DeterministicFakeEmbedding(size=2),
    ):
        yield


@pytest.fixture(scope="session", autouse=True)
def settings() -> Generator[Settings, None, None]:
    test_settings = Settings(_env_file=".env-test")  # type: ignore
    with patch("ragtube.settings.get_settings", return_value=test_settings):
        yield test_settings


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    engine = create_engine(
        "postgresql+psycopg://postgres@localhost/postgres",
        poolclass=StaticPool,
    )
    with Session(engine) as session:
        session.connection().execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )
        session.commit()
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine: Engine):
    with Session(engine) as session:
        yield session
