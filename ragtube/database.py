from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine

from ragtube.retriever import create_vector_extension
from ragtube.settings import get_settings


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
    SQLModel.metadata.create_all(engine)
    create_vector_extension(engine)
    return engine
