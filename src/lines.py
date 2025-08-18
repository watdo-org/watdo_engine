from typing import TypedDict, Generator


class LogicalLine(TypedDict):
    line_no: tuple[int, int]
    content: str
    comment: str | None


def split_logical_lines(code: str) -> Generator[LogicalLine, None, None]:
    for index, line in enumerate(code.splitlines()):
        if line.strip() == "":
            continue

        logical_line: LogicalLine = {
            "line_no": (index + 1, index + 1),
            "content": line,
            "comment": None,
        }

        yield logical_line
