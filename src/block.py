from typing import TypedDict, Literal

Action = Literal["set", "end"]
ScheduleEntry = tuple[Action, str | None]


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
