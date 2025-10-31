from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import (
    Session,
    SQLModel,
    create_engine,
    text,
)

from ragtube.core.settings import get_settings


def create_vector_extension(engine: Engine):
    with Session(engine) as session:
        session.connection().execute(
            text("CREATE EXTENSION IF NOT EXISTS vector;")
        )
        session.commit()


@lru_cache
def setting_engine() -> Engine:
    settings = get_settings()
    connection = "postgresql+psycopg://{}:{}@{}:{}/{}".format(
        settings.db_user.get_secret_value(),
        settings.db_password.get_secret_value(),
        settings.db_host.get_secret_value(),
        settings.db_port.get_secret_value(),
        settings.db_name.get_secret_value(),
    )
    engine = create_engine(connection)
    create_vector_extension(engine)
    SQLModel.metadata.create_all(engine)
    return engine


def get_session():
    engine = setting_engine()
    with Session(engine) as session:
        yield session
