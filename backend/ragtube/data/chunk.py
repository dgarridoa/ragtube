from llama_index.core.node_parser import (
    TokenTextSplitter,
)
from sqlalchemy.engine import Engine
from sqlmodel import Session, col, select
from tqdm import tqdm

from ragtube.core.models import Chunk, Video


def get_video_content_chunks(
    splitter: TokenTextSplitter, video: Video
) -> list[Chunk]:
    if video.content is None:
        raise ValueError("Video content is empty.")

    video_content_chunks = []
    content_chunks = splitter.split_text(video.content)
    for chunk in content_chunks:
        video_content_chunks.append(Chunk(content=chunk, video_id=video.id))
    return video_content_chunks


class ChunkTask:
    def __init__(
        self, engine: Engine, chunk_size: int = 500, chunk_overlap: int = 50
    ):
        self.engine = engine
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = TokenTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def get_missing_videos_content(self) -> list[Video] | None:
        with Session(self.engine) as session:
            statement = (
                select(Video)
                .where(col(Video.content).is_not(None))
                .join(Chunk, isouter=True)
                .where(col(Chunk.id).is_(None))
            )
            videos_content = session.exec(statement).all()
        if not videos_content:
            return None
        return list(videos_content)

    def get_videos_content_chunks(self, videos: list[Video]) -> list[Chunk]:
        videos_content_chunks = []
        for video_content in tqdm(videos, desc="Chunking"):
            videos_content_chunks.extend(
                get_video_content_chunks(self.splitter, video_content)
            )
        return videos_content_chunks

    def launch(self):
        missing_videos_content = self.get_missing_videos_content()
        if not missing_videos_content:
            return None
        videos_content_chunks = self.get_videos_content_chunks(
            missing_videos_content
        )
        with Session(self.engine) as session:
            session.add_all(videos_content_chunks)
            session.commit()
