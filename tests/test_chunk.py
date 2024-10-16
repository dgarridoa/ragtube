from datetime import datetime

from llama_index.core.node_parser import (
    TokenTextSplitter,
)
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ragtube.chunk import (
    ChunkTask,
    get_video_content_chunks,
)
from ragtube.models import Channel, Chunk, Video


def video():
    return Video(
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
        channel=Channel(id="UC34rhn8Um7R18-BHjPklYlw", title="diego garrido"),
    )


def videos():
    return [video()]


def chunks():
    return [
        Chunk(
            content="I often make this joke which is agile's a lot like communism you know people just keep not trying it correctly um what is",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            content="it correctly um what is what is the correct way to Agile oh gee um it's a real simple idea right uh do things",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            content="idea right uh do things in really short sequences measure how much you get done in every sequence use that measurement to project an end",
            video_id="Guy5D3PJlZk",
        ),
        Chunk(
            content="measurement to project an end date and tell everybody that's kind of it",
            video_id="Guy5D3PJlZk",
        ),
    ]


def chunks_with_id() -> list[Chunk]:
    rows = []
    for i, chunk in enumerate(chunks()):
        chunk_with_id = Chunk(**chunk.model_dump())
        chunk_with_id.id = i + 1
        rows.append(chunk_with_id)
    return rows


def create_video_table(engine: Engine):
    with Session(engine) as session:
        session.add_all(videos())
        session.commit()


def test_get_video_content_chunks():
    splitter = TokenTextSplitter(chunk_size=25, chunk_overlap=5)
    actual_chunks = get_video_content_chunks(splitter, video())
    assert actual_chunks == chunks()


def test_chunk_task(engine: Engine):
    create_video_table(engine)

    task = ChunkTask(engine, chunk_size=25, chunk_overlap=5)

    actual_videos = task.get_missing_videos_content()
    assert actual_videos == videos()

    actual_chunks = task.get_videos_content_chunks(videos())
    assert actual_chunks == chunks()

    task.launch()
    with Session(engine) as session:
        chunks_from_db = session.exec(select(Chunk)).all()
        assert chunks_from_db == chunks_with_id()

    assert task.get_missing_videos_content() is None
