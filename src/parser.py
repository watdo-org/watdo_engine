from typing import TypedDict
from .fields import Field, split_fields
from .variables import apply_variables


class PartialBlockData(TypedDict, total=False):
    title: str
    notes: str | None
    tags: set[str] | None


class BlockData(TypedDict, total=True):
    title: str
    notes: str | None
    tags: set[str] | None


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

    raise ValueError(f"Invalid key: '{field["key"]}'")


def parse_code(code: str, variables: dict[str, str]) -> BlockData:
    code = apply_variables(code, variables)
    fields = split_fields(code)
    partial_block_data: PartialBlockData = {}

    for field in fields:
        partial_block_data.update(parse_field(field))

    block_data: BlockData = {
        "title": partial_block_data["title"],
        "notes": partial_block_data.get("notes", None),
        "tags": partial_block_data.get("tags", None),
    }

    return block_data
