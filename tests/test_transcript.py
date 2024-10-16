from datetime import datetime
from unittest.mock import patch

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ragtube.models import Caption, Channel, Video
from ragtube.transcript import (
    VideoTranscriptTask,
    get_channel_videos,
    get_video_captions,
)


def channel():
    return Channel(id="UC34rhn8Um7R18-BHjPklYlw", title="diego garrido")


def channels():
    return [channel()]


def video():
    return Video(
        id="Guy5D3PJlZk",
        title="Agile Manifesto",
        publish_time=datetime(2024, 8, 9, 16, 3, 23),
        channel_id=channel().id,
        channel=channel(),
    )


def videos():
    return [video()]


def video_captions():
    return [
        Caption(
            text="I often make this joke which is agile's",
            start=0.199,
            duration=3.961,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="a lot like communism you know people",
            start=2.32,
            duration=4.8,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="just keep not trying it correctly um",
            start=4.16,
            duration=6.12,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="what is what is the correct way to",
            start=7.12,
            duration=8.08,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="Agile oh gee um it's a real simple idea",
            start=10.28,
            duration=7.52,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="right uh do things in really short",
            start=15.2,
            duration=4.72,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="sequences measure how much you get done",
            start=17.8,
            duration=4.16,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="in every sequence use that measurement",
            start=19.92,
            duration=4.0,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="to project an end date and tell",
            start=21.96,
            duration=6.04,
            video_id="Guy5D3PJlZk",
        ),
        Caption(
            text="everybody that's kind of it",
            start=23.92,
            duration=4.08,
            video_id="Guy5D3PJlZk",
        ),
    ]


def video_content():
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
    )


def videos_content():
    return [video_content()]


def videos_captions():
    return video_captions()


def videos_captions_with_id() -> list[Caption]:
    videos_caption_with_id = []
    for i, video_caption in enumerate(videos_captions()):
        video_caption_with_id = Caption(**video_caption.model_dump())
        video_caption_with_id.id = i + 1
        videos_caption_with_id.append(video_caption_with_id)
    return videos_caption_with_id


def test_get_channel_videos():
    actual_videos = get_channel_videos("UC34rhn8Um7R18-BHjPklYlw", timeout=60)
    assert actual_videos == videos()


def test_get_video_captions():
    actual_video_captions = get_video_captions(
        "Guy5D3PJlZk", language="en", timeout=5
    )
    assert actual_video_captions == video_captions()


@pytest.fixture
def mock_get_channel_videos():
    with patch("ragtube.transcript.get_channel_videos") as mock:
        mock.return_value = videos()
        yield mock


def test_video_transcript_task(
    engine: Engine,
    mock_get_channel_videos,
):
    task = VideoTranscriptTask(
        engine,
        channel_id="UC34rhn8Um7R18-BHjPklYlw",
        language="en",
        timeout=60,
    )

    actual_videos = task.get_videos()
    assert actual_videos == videos()

    assert task.get_missing_videos(videos()) == videos()

    task.launch()
    with Session(engine) as session:
        channels_from_db = session.exec(select(Channel)).all()
        assert channels_from_db == channels()

        videos_content_from_db = session.exec(select(Video)).all()
        assert videos_content_from_db == videos_content()

        videos_captions_from_db = session.exec(select(Caption)).all()

        assert videos_captions_from_db == videos_captions_with_id()

        videos_from_db = list(session.exec(select(Video)).all())
        assert task.get_missing_videos(videos_from_db) is None

    assert mock_get_channel_videos.call_count == 2
