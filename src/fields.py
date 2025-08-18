from typing import TypedDict, Generator


class Field(TypedDict):
    line_no_range: tuple[int, int]
    content: str
    key: str
    value: str


def split_fields(code: str) -> Generator[Field, None, None]:
    for index, line in enumerate(code.splitlines()):
        if line.strip() == "":
            continue

        key, value = line.split(":", 1)
        field: Field = {
            "line_no_range": (index + 1, index + 1),
            "content": line,
            "key": key,
            "value": value,
        }

        yield field
