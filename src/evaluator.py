import datetime
from typing import Generator
from .date import parse_date_string
from .block import Action, ScheduleEntry


def generate_timeline(
    schedule: list[ScheduleEntry],
    relative_base: datetime.datetime,
    *,
    timezone: str | None = None,
) -> Generator[tuple[Action, datetime.datetime | None], None, None]:
    for action, date_string in schedule:
        if date_string is None:
            yield action, None

        else:
            date = parse_date_string(date_string, relative_base, timezone=timezone)

            if date is None:
                raise ValueError(f"Failed parsing '{date_string}'")

            yield action, date


def evaluate_schedule(
    schedule: list[ScheduleEntry],
    *,
    relative_base: datetime.datetime,
    evaluation_date: datetime.datetime,
    timezone: str | None = None,
) -> tuple[bool, datetime.datetime | None]:
    timeline = generate_timeline(schedule, relative_base, timezone=timezone)
    evaluation = False
    matched_date: datetime.datetime | None = None

    for action, date in timeline:
        if date is None:
            evaluation = action == "set"
            matched_date = date

        else:
            if date <= evaluation_date:
                evaluation = action == "set"
                matched_date = date
            else:
                break

            if date == evaluation_date:
                break

    return evaluation, matched_date
