from typing import TypedDict


class PartialBlockData(TypedDict, total=False):
    title: str
    notes: str | None


class BlockData(TypedDict, total=True):
    title: str
    notes: str | None
