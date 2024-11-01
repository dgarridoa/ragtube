from datetime import datetime

from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from sqlalchemy.engine import Engine
from sqlmodel import Session

from ragtube.models import Channel, Chunk, Video
from ragtube.rerank import get_rerank_retriever
from ragtube.retriever import Retriever, create_index


def create_chunk_table(engine: Engine):
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
                -0.297897279262542724609375,
                -2.93831539154052734375,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=2,
            content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
            embedding=[
                0.604319095611572265625,
                -0.21918331086635589599609375,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=3,
            content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
            embedding=[
                -0.3561325967311859130859375,
                0.29398024082183837890625,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
        Chunk(
            id=4,
            content="measurement to project an end date and tell everybody that's kind of it",
            embedding=[
                -0.3162524402141571044921875,
                -0.392429411411285400390625,
            ],
            video_id="Guy5D3PJlZk",
            video=video,
        ),
    ]
    with Session(engine) as session:
        session.add_all(chunks)
        session.commit()


def test_rerank_retriever(engine: Engine):
    assert Chunk.embedding.type.dim == 2

    create_chunk_table(engine)
    create_index(engine)

    embedding_model = DeterministicFakeEmbedding(size=2)
    retriever = Retriever(
        engine=engine,
        embedding_model=embedding_model,
        results_to_retrieve=2,
    )
    rerank_retriever = get_rerank_retriever(
        retriever,
        results_to_retrieve=2,
        score_threshold=0.4,
        model_name="rank-T5-flan",
    )

    docs = rerank_retriever.invoke(
        input="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is"
    )
    expected_docs = [
        Document(
            metadata={
                "id": 2,
                "relevance_score": 0.41914457082748413,
                "video_id": "Guy5D3PJlZk",
                "title": "Agile Manifesto",
                "publish_time": datetime(2024, 8, 9, 16, 3, 23),
            },
            page_content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
        ),
    ]
    assert docs == expected_docs
