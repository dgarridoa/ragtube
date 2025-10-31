from datetime import datetime

from langchain_core.embeddings import DeterministicFakeEmbedding
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ragtube.core.models import Channel, Chunk, Video
from ragtube.services.embedding import EmbeddingTask


def create_chunk_table(engine: Engine):
    with Session(engine) as session:
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
                content="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
                video_id="Guy5D3PJlZk",
                video=video,
            ),
            Chunk(
                content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
                video_id="Guy5D3PJlZk",
                video=video,
            ),
            Chunk(
                content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
                video_id="Guy5D3PJlZk",
                video=video,
            ),
            Chunk(
                content="measurement to project an end date and tell everybody that's kind of it",
                video_id="Guy5D3PJlZk",
                video=video,
            ),
        ]
        session.add_all(chunks)
        session.commit()


def test_embedding_task(engine: Engine):
    assert Chunk.embedding.type.dim == 2

    create_chunk_table(engine)

    task = EmbeddingTask(engine)

    assert isinstance(task.model, DeterministicFakeEmbedding)

    actual_chunks = task.get_missing_chunks()
    assert actual_chunks == [
        Chunk(
            id=1,
            content="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            id=2,
            content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            id=3,
            content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            id=4,
            content="measurement to project an end date and tell everybody that's kind of it",
            video_id="Guy5D3PJlZk",
        ),
    ]

    task.launch()
    with Session(engine) as session:
        actual_chunks_from_db = session.exec(select(Chunk)).all()
        for chunk in actual_chunks_from_db:
            chunk.embedding = list(chunk.embedding)
        assert actual_chunks_from_db == [
            Chunk(
                id=1,
                content="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
                embedding=[
                    0.20749013125896453857421875,
                    0.91412651538848876953125,
                ],
                video_id="Guy5D3PJlZk",
            ),
            Chunk(
                id=2,
                content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
                embedding=[
                    -0.885921180248260498046875,
                    0.85550343990325927734375,
                ],
                video_id="Guy5D3PJlZk",
            ),
            Chunk(
                id=3,
                content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
                embedding=[
                    -0.227100789546966552734375,
                    -1.99812042713165283203125,
                ],
                video_id="Guy5D3PJlZk",
            ),
            Chunk(
                id=4,
                content="measurement to project an end date and tell everybody that's kind of it",
                embedding=[
                    0.26584398746490478515625,
                    0.608121931552886962890625,
                ],
                video_id="Guy5D3PJlZk",
            ),
        ]

    assert task.get_missing_chunks() is None
