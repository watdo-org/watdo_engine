from typing import TypedDict, Literal

ScheduleEntry = tuple[Literal["set", "end"], str | None]


class PartialBlockData(TypedDict, total=False):
    title: str
    notes: str | None
    tags: set[str] | None
    tasks: list[str] | None
    schedule: list[ScheduleEntry]


class BlockData(TypedDict, total=True):
    title: str
    notes: str | None
    tags: set[str] | None
    tasks: list[str] | None
    schedule: list[ScheduleEntry]
