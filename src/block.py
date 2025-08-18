from typing import TypedDict


class PartialBlockData(TypedDict, total=False):
    title: str
    notes: str


class BlockData(PartialBlockData):
    pass
