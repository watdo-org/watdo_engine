from .lines import LogicalLine, split_logical_lines
from .block import BlockData, PartialBlockData
from .variables import apply_variables


def parse_line(line: LogicalLine) -> PartialBlockData:
    raw_key, raw_value = line["content"].split(":", 1)
    key = raw_key.strip().lower()
    value = raw_value.strip()

    if key == "title":
        return {"title": value}
    elif key == "notes":
        return {"notes": value}

    raise ValueError(f"Invalid key: '{raw_key}'")


def parse_code(code: str, variables: dict[str, str]) -> BlockData:
    code = apply_variables(code, variables)
    lines = split_logical_lines(code)
    partial_block_data: PartialBlockData = {}

    for line in lines:
        partial_block_data.update(parse_line(line))

    block_data: BlockData = {
        "title": partial_block_data["title"],
        "notes": partial_block_data.get("notes", None),
    }

    return block_data
