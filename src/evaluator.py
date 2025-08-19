import datetime
from typing import Generator
import dateparser
from .block import Action, ScheduleEntry


def generate_timeline(
    schedule: list[ScheduleEntry],
    relative_base: datetime.datetime,
) -> Generator[tuple[Action, datetime.datetime | None], None, None]:
    for action, date_string in schedule:
        if date_string is None:
            yield action, None

        else:
            date = dateparser.parse(
                date_string,
                settings={"RELATIVE_BASE": relative_base},
            )

            if date is None:
                raise ValueError(f"Failed parsing '{date_string}'")

            yield action, date


def evaluate_schedule(
    schedule: list[ScheduleEntry],
    evaluation_date: datetime.datetime,
) -> bool:
    evaluation = False

    for action, date in generate_timeline(schedule, evaluation_date):
        if date is None:
            evaluation = action == "set"

        else:
            if date <= evaluation_date:
                evaluation = action == "set"
            else:
                break

            if date == evaluation_date:
                break

    return evaluation
