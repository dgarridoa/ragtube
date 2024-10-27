import logging
import secrets
from datetime import datetime
from typing import Annotated

import requests
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ragtube.database import setting_engine
from ragtube.models import Channel
from ragtube.rag import get_rag_chain
from ragtube.settings import get_settings


class RAGInput(BaseModel):
    input: Annotated[
        str,
        Field(
            title="Input text",
            examples=["What is the analogy between agile and communism?"],
        ),
    ]


class Document(BaseModel):
    id: Annotated[
        int,
        Field(
            title="Chunk id",
            examples=[1],
        ),
    ]
    video_id: Annotated[
        str, Field(title="YouTube video id", examples=["UBXXw2JSloo"])
    ]
    title: Annotated[
        str,
        Field(
            title="YouTube video title", examples=["I Interviewed Uncle Bob"]
        ),
    ]
    publish_time: Annotated[
        datetime,
        Field(
            title="Youtube video published time",
            examples=["2024-04-29T18:10:20"],
        ),
    ]
    content: Annotated[
        str,
        Field(
            title="Chunk text",
            examples=[
                "are we sure we're on the same topic I'm pretty sure ..."
            ],
        ),
    ]


class RAGOutput(BaseModel):
    answer: Annotated[
        str,
        Field(
            title="Answer text",
            examples=["The analogy between agile and communism ..."],
        ),
    ]
    context: list[Document]


class RAGError(BaseModel):
    error: str
    response: dict = {}


app = FastAPI()
security = HTTPBasic()


def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    settings = get_settings()
    username = settings.api_user.get_secret_value()
    password = settings.api_password.get_secret_value()

    if username is None or password is None:
        raise ValueError(
            "API_USERNAME and API_PASSWORD environment variables must be set"
        )

    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/readiness")
async def readiness():
    return {"status": "ok"}


@app.get("/channel")
async def channel() -> list[Channel]:
    engine = setting_engine()
    with Session(engine) as session:
        return list(session.exec(select(Channel)).all())


@app.post("/rag")
async def rag(
    *,
    input: str,
    channel_id: str | None = None,
    username: Annotated[str, Depends(get_current_username)],
) -> RAGOutput:
    rag_chain = get_rag_chain(channel_id)
    response = rag_chain.invoke({"input": input})
    output = RAGOutput(
        answer=response["answer"],
        context=[
            Document(
                id=doc.metadata["id"],
                video_id=doc.metadata["video_id"],
                title=doc.metadata["title"],
                publish_time=doc.metadata["publish_time"],
                content=doc.page_content,
            )
            for doc in response["context"]
        ],
    )
    return output


def get_rag_response(
    url: str, api_username: str, api_password: str, params: dict
) -> RAGOutput | RAGError:
    try:
        response = requests.post(
            url,
            auth=(
                api_username,
                api_password,
            ),
            params=params,
            timeout=120,
        )
        try:
            response.raise_for_status()
            return RAGOutput.model_validate(response.json())
        except requests.exceptions.HTTPError as http_err:
            return RAGError(error=str(http_err), response=response.json())
    except Exception as err:
        return RAGError(error=str(err))


class ReadinessFilter(logging.Filter):
    def filter(self, record):
        endpoints = ["/readiness"]
        return not any(
            endpoint in record.getMessage() for endpoint in endpoints
        )


if __name__ == "__main__":
    import uvicorn

    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    uvicorn.run(
        "ragtube.api:app",
        host="0.0.0.0",  # noqa
        port=5000,
        log_config="log_config.yaml",
    )
