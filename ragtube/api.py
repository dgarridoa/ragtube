import json
import logging
from datetime import datetime
from typing import Annotated, Generator

import requests
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBasic
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from ragtube.database import get_session
from ragtube.models import Channel
from ragtube.rag import get_rag_chain


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


class RAGError(Exception):
    error: str
    response: dict = {}


app = FastAPI()
security = HTTPBasic()


def get_allowed_origins() -> list[str]:
    from ragtube.settings import get_settings

    settings = get_settings()
    hostname = settings.hostname.get_secret_value()
    if hostname == "localhost":
        return ["http://localhost:8501"]
    return [f"https://{hostname}"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/readiness")
async def readiness():
    return {"status": "ok"}


@app.get("/channel")
async def channel(*, session: Session = Depends(get_session)) -> list[Channel]:
    return list(session.exec(select(Channel)).all())


@app.get("/rag")
async def rag(
    *,
    input: str,
    channel_id: str | None = None,
    rag_chain=Depends(get_rag_chain),
):
    response = rag_chain.stream({"input": input})

    def stream(response):
        for message in response:
            if "context" in message:
                context = [
                    Document(
                        id=doc.metadata["id"],
                        video_id=doc.metadata["video_id"],
                        title=doc.metadata["title"],
                        publish_time=doc.metadata["publish_time"],
                        content=doc.page_content,
                    ).model_dump(mode="json")
                    for doc in message["context"]
                ]
                yield json.dumps({"context": context}) + "\n"
            if "answer" in message:
                yield json.dumps({"answer": message["answer"]}) + "\n"

    return StreamingResponse(
        stream(response), media_type="application/x-ndjson"
    )


def get_rag_response(
    url: str, params: dict
) -> Generator[list[Document] | str | None, None, None]:
    try:
        with requests.get(
            url,
            params=params,
            timeout=120,
            stream=True,
        ) as r:
            try:
                r.raise_for_status()
                for chunk in r.iter_lines():
                    chunk_data = json.loads(chunk.decode("utf-8"))
                    if "context" in chunk_data:
                        context = None
                        if len(chunk_data["context"]) > 0:
                            context = [
                                Document.model_validate(doc)
                                for doc in chunk_data["context"]
                            ]
                        yield context
                    elif "answer" in chunk_data:
                        yield chunk_data["answer"]
            except requests.exceptions.HTTPError as http_err:
                raise RAGError(str(http_err), r.json())
    except Exception as err:
        raise RAGError(str(err))


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
