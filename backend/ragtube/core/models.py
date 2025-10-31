from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlmodel import Column, Field, Relationship, SQLModel

from ragtube.core.params import get_params


class Channel(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str

    videos: list["Video"] = Relationship(
        back_populates="channel", cascade_delete=True
    )


class Video(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    publish_time: datetime
    content: str | None = Field(default=None)

    channel_id: str = Field(foreign_key="channel.id", ondelete="CASCADE")
    channel: Channel = Relationship(back_populates="videos")
    captions: list["Caption"] = Relationship(
        back_populates="video", cascade_delete=True
    )
    chunks: list["Chunk"] = Relationship(
        back_populates="video", cascade_delete=True
    )


class Caption(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    start: float
    duration: float

    video_id: str = Field(foreign_key="video.id", ondelete="CASCADE")
    video: Video = Relationship(back_populates="captions")


class Chunk(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str
    embedding: Any = Field(
        default=None, sa_column=Column(Vector(get_params().embedding_size))
    )

    video_id: str = Field(foreign_key="video.id", ondelete="CASCADE")
    video: Video = Relationship(back_populates="chunks")
