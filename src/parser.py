from .lines import LogicalLine
from .block import BlockData, PartialBlockData


def parse_line(line: LogicalLine) -> PartialBlockData:
    raw_key, raw_value = line["content"].split(":", 1)
    key = raw_key.strip().lower()
    value = raw_value.strip()

    if key == "title":
        return {"title": value}
    elif key == "notes":
        return {"notes": value}

    raise ValueError(f"Invalid key: '{raw_key}'")


def parse_code(code: str) -> BlockData:
    raise NotImplementedError
