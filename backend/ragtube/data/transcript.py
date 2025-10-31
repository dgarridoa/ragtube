import logging
from datetime import datetime

import requests
from requests.models import HTTPError
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select
from tqdm import tqdm
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import CouldNotRetrieveTranscript
from youtube_transcript_api.proxies import GenericProxyConfig

from ragtube.core.models import Caption, Channel, Video
from ragtube.core.utils import timeout_handler

YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"
WATCH_URL = "https://www.youtube.com/watch?v={video_id}"


def get_channel_metadata(
    channel_id: str,
    api_key: str,
    timeout: int = 5,
) -> Channel:
    params = {"part": "snippet", "id": channel_id, "key": api_key}
    url = f"{YOUTUBE_API_URL}/channels"
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    if "items" not in data:
        raise HTTPError("No channel found.")
    title = data["items"][0]["snippet"]["title"]
    return Channel(id=channel_id, title=title)


def get_channel_videos(
    channel_id: str,
    api_key: str,
    timeout: int = 5,
) -> list[Video]:
    # if it has a "Videos" playlist on the main page
    playlist_id = "UULF" + channel_id[2:]
    params = {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": 50,
        "key": api_key,
    }
    url = f"{YOUTUBE_API_URL}/playlistItems"
    response = requests.get(url, params=params, timeout=timeout).json()
    if "error" in response and response["error"]["status_code"] == 404:
        # if it has not a "Videos" playlist on the main page
        params["playlistId"] = "UU" + channel_id[2:]

    videos = []
    while True:
        response = requests.get(url, params=params, timeout=timeout).json()
        if "error" in response:
            raise HTTPError("Unable to get video.", response["error"])

        if "items" in response:
            for item in response["items"]:
                video_id = item["snippet"]["resourceId"]["videoId"]
                title = item["snippet"]["title"]
                publish_time = datetime.fromisoformat(
                    item["snippet"]["publishedAt"]
                ).replace(tzinfo=None)
                videos.append(
                    Video(
                        id=video_id,
                        title=title,
                        publish_time=publish_time,
                        channel_id=channel_id,
                    )
                )

        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break
        params["pageToken"] = nextPageToken

    if not videos:
        raise HTTPError("No videos found")

    return videos


def get_video_captions(
    video_id: str,
    language: str = "en",
    timeout: int = 5,
    proxies: dict | None = None,
) -> list[Caption] | None:
    @timeout_handler(timeout)
    def _get_video_captions():
        video_url = WATCH_URL.format(video_id=video_id)
        error_message = (
            f"\nCould not retrieve a transcript for the video {video_url}!"
        )
        proxy_config = None
        if proxies is not None:
            proxy_config = GenericProxyConfig(**proxies)
        client = YouTubeTranscriptApi(proxy_config=proxy_config)
        try:
            fetched_transcript = client.fetch(video_id, languages=[language])
            captions = [
                Caption(
                    text=caption.text,
                    start=caption.start,
                    duration=caption.duration,
                    video_id=video_id,
                )
                for caption in fetched_transcript.snippets
            ]
            return captions
        except CouldNotRetrieveTranscript as e:
            logging.error(f"{type(e).__name__}: {e.cause}.\n{error_message}")
            return None
        except Exception as e:
            logging.error(f"{type(e).__name__}: {e.args[0]}.\n{error_message}")
            return None

    return _get_video_captions()


def update_video_content(video: Video) -> None:
    sorted_captions = sorted(video.captions, key=lambda x: x.start)
    content = " ".join([caption.text for caption in sorted_captions])
    video.content = content


class VideoTranscriptTask:
    def __init__(
        self,
        engine: Engine,
        channel_id: str | list[str],
        api_key: str,
        language: str = "en",
        timeout: int = 60,
        proxies: dict | None = None,
    ):
        self.engine = engine
        self.channel_id = channel_id
        self.language = language
        self.timeout = timeout
        self.proxies = proxies
        self.api_key = api_key

    def get_videos(self, channel_id: str) -> list[Video]:
        videos = get_channel_videos(
            channel_id,
            self.api_key,
            self.timeout,
        )
        return videos

    def get_missing_videos(
        self, channel_id: str, videos: list[Video]
    ) -> list[Video] | None:
        video_ids = [video.id for video in videos]
        with Session(self.engine) as session:
            statement = select(Video.id).where(
                col(Video.channel_id) == channel_id,
                col(Video.id).in_(video_ids),
            )
            video_ids_found = session.exec(statement).all()
        if not video_ids_found:
            return videos
        if len(video_ids) == len(video_ids_found):
            return None
        missing_videos: list[Video] = []
        for video in videos:
            if video.id not in video_ids_found:
                missing_videos.append(video)
        return missing_videos

    def add_channel(self, channel_id: str):
        channel = get_channel_metadata(channel_id, self.api_key, self.timeout)
        with Session(self.engine) as session:
            channel_from_db = session.get(Channel, channel.id)
            if not channel_from_db:
                session.add(channel)
                session.commit()

    def add_videos_and_captions(self, videos: list[Video]):
        with Session(self.engine) as session:
            for video in tqdm(videos, desc="Captions"):
                captions = get_video_captions(
                    video.id,
                    self.language,
                    self.timeout,
                    self.proxies,
                )
                if captions:
                    video.captions = captions
                    session.add_all(captions)
                    update_video_content(video)
                    session.add(video)
            session.commit()

    def add_channel_videos_and_captions(self, channel_id: str):
        self.add_channel(channel_id)
        videos = self.get_videos(channel_id)
        missing_videos = self.get_missing_videos(channel_id, videos)
        if not missing_videos:
            return None
        self.add_videos_and_captions(missing_videos)

    def launch(self):
        if isinstance(self.channel_id, str):
            self.add_channel_videos_and_captions(self.channel_id)
        elif isinstance(self.channel_id, list):
            for channel_id in self.channel_id:
                self.add_channel_videos_and_captions(channel_id)
