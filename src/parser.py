from typing import cast
from .block import BlockData, PartialBlockData, ScheduleEntry
from .fields import Field, split_fields
from .variables import apply_variables


def parse_field(field: Field) -> PartialBlockData:
    key = field["key"].strip().lower()

    if key == "title":
        return {"title": field["value"]}

    elif key == "notes":
        return {"notes": field["value"]}

    elif key == "tags":
        tags = []

        for item in field["value"].split(","):
            item = item.strip()

            if item == "":
                continue

            tags.append(item)

        return {"tags": set(tags)}

    elif key == "tasks":
        tasks = []

        for line in field["value"].splitlines():
            if line.strip() == "":
                continue

            tasks.append(line)

        return {"tasks": tasks}

    elif key == "timezone":
        return {"timezone": field["value"].strip()}

    elif key == "schedule":
        schedule: list[ScheduleEntry] = []

        for line in field["value"].splitlines():
            line = line.strip()

            if line == "":
                continue

            try:
                action, date = line.split(" ", 1)
                date = date.strip()
            except ValueError:
                action = line
                date = None

            if action not in ["set", "end"]:
                raise ValueError(f"Invalid action: {action}")

            schedule.append(cast(ScheduleEntry, (action, date)))

        return {"schedule": schedule}

    raise ValueError(f"Invalid key: '{field["key"]}'")


def parse_code(code: str, variables: dict[str, str]) -> BlockData:
    code = apply_variables(code, variables)
    fields = split_fields(code)
    partial_block_data: PartialBlockData = {}

    for field in fields:
        partial_block_data.update(parse_field(field))

    try:
        block_data: BlockData = {
            "title": partial_block_data["title"],
            "notes": partial_block_data.get("notes", None),
            "tags": partial_block_data.get("tags", None),
            "tasks": partial_block_data.get("tasks", None),
            "timezone": partial_block_data.get("timezone", None),
            "schedule": partial_block_data["schedule"],
        }
    except KeyError as error:
        raise ValueError(f"Missing required field: {error}")

    return block_data
