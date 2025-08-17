import json
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from langchain.prompts import PromptTemplate
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.language_models import (
    GenericFakeChatModel,
)
from sqlalchemy.engine import Engine
from sqlmodel import Session

from ragtube.database import get_session
from ragtube.models import Channel, Chunk, Video
from ragtube.rag import create_rag_chain, get_rag_chain
from ragtube.retriever import Retriever


def create_chunk_table(session: Session):
    channel = Channel(id="UC34rhn8Um7R18-BHjPklYlw", title="diego garrido")
    video = Video(
        id="Guy5D3PJlZk",
        title="Agile Manifesto",
        publish_time=datetime(2024, 8, 9, 16, 3, 23),
        content=" ".join(
            [
                "I often make this joke which is agile's",
                "a lot like communism you know people",
                "just keep not trying it correctly um",
                "what is what is the correct way to",
                "Agile oh gee um it's a real simple idea",
                "right uh do things in really short",
                "sequences measure how much you get done",
                "in every sequence use that measurement",
                "to project an end date and tell",
                "everybody that's kind of it",
            ]
        ),
        channel_id="UC34rhn8Um7R18-BHjPklYlw",
        channel=channel,
    )
    chunks = [
        Chunk(
            id=1,
            content="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
            embedding=[
                0.20749013125896453857421875,
                0.91412651538848876953125,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=2,
            content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
            embedding=[
                -0.885921180248260498046875,
                0.85550343990325927734375,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=3,
            content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
            embedding=[
                -0.227100789546966552734375,
                -1.99812042713165283203125,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=4,
            content="measurement to project an end date and tell everybody that's kind of it",
            embedding=[
                0.26584398746490478515625,
                0.608121931552886962890625,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
    ]
    session.add_all(chunks)
    session.commit()


@pytest.fixture(name="get_rag_chain_override")
def get_rag_chain_fixture(engine: Engine):
    def get_rag_chain_override(channel_id: str | None = None):
        chat_model = GenericFakeChatModel(
            messages=iter(
                [
                    "Agile is like Communism - everyone agrees it's a great idea, but when someone tries to implement it, it devolves into chaos and everyone starts pointing fingers at each other saying 'That's not true Agile!'"
                ]
            )
        )
        embedding_model = DeterministicFakeEmbedding(size=2)
        retriever = Retriever(
            engine=engine,
            embedding_model=embedding_model,
            results_to_retrieve=2,
            channel_id=channel_id,
        )
        TEMPLATE = """You will be asked questions about a YouTuber content creators.
        I will provide you with transcriptions from their videos to use as context to answer the question at the end.

        <context>
        {context}
        </context>

        Question: {input}

        Answer:
        """
        prompt = PromptTemplate(
            template=TEMPLATE, input_variables=["context", "input"]
        )
        rag_chain = create_rag_chain(chat_model, retriever, prompt)
        return rag_chain

    return get_rag_chain_override


@pytest.fixture(name="client")
def client_fixture(session: Session, get_rag_chain_override):
    from ragtube.api import app

    create_chunk_table(session)
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_rag_chain] = get_rag_chain_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_list_channels(client: TestClient):
    response = client.get("/channel")
    data = response.json()
    assert response.status_code == 200
    assert data == [
        {"id": "UC34rhn8Um7R18-BHjPklYlw", "title": "diego garrido"}
    ]


def test_rag(client: TestClient):
    response = client.get(
        "/rag",
        params={
            "input": "Tell me a joke between agile and communism",
            "channel_id": "UC34rhn8Um7R18-BHjPklYlw",
        },
    )
    lines = response.text.split("\n")[:-1]
    data = {"answer": "", "context": []}
    for line in lines:
        chunk_data = json.loads(line)
        if "context" in chunk_data:
            data["context"] = chunk_data["context"]
        if "answer" in chunk_data:
            data["answer"] += chunk_data["answer"]

    assert response.status_code == 200
    assert data == {
        "answer": "Agile is like Communism - everyone agrees it's a great idea, but when someone tries to implement it, it devolves into chaos and everyone starts pointing fingers at each other saying 'That's not true Agile!'",
        "context": [
            {
                "id": 1,
                "video_id": "Guy5D3PJlZk",
                "title": "Agile Manifesto",
                "publish_time": "2024-08-09T16:03:23",
                "content": "I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
            },
            {
                "id": 4,
                "video_id": "Guy5D3PJlZk",
                "title": "Agile Manifesto",
                "publish_time": "2024-08-09T16:03:23",
                "content": "measurement to project an end date and tell everybody that's kind of it",
            },
        ],
    }
