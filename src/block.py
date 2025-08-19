from typing import TypedDict


class PartialBlockData(TypedDict, total=False):
    title: str
    notes: str | None
    tags: set[str] | None
    tasks: list[str] | None
    schedule: list[tuple[str, str | None]]


class BlockData(TypedDict, total=True):
    title: str
    notes: str | None
    tags: set[str] | None
    tasks: list[str] | None
    schedule: list[tuple[str, str | None]]
