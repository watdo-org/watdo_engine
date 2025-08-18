from typing import TypedDict, Generator


class Field(TypedDict):
    line_no_range: tuple[int, int]
    content: str
    key: str
    value: str


def split_fields(code: str) -> Generator[Field, None, None]:
    current_key = ""
    current_value = ""
    multiline_mode = False

    for index, line in enumerate(code.splitlines()):
        line_no = index + 1

        if not multiline_mode:
            if line.strip() == "":
                continue

            try:
                current_key, current_value = line.split(":", 1)
            except ValueError:
                raise ValueError(
                    f"Field is missing a colon to separate the key and value in line {line_no}"
                )

            if current_value == "":
                raise ValueError(f"Value cannot be empty in line {line_no}")

            if current_value.lstrip().startswith('"""'):
                opening_quotes_trimmed = current_value.lstrip()[3:]

                # Make sure the multiline field is actually multiline
                # If it closes in the same line, then we treat it as a single line
                if not opening_quotes_trimmed.rstrip().endswith('"""'):
                    current_value = opening_quotes_trimmed
                    multiline_mode = True

        else:
            current_value += f"\n{line}"

            if line.rstrip().endswith('"""'):
                current_value = current_value.rstrip()[:-3]
                multiline_mode = False

        if not multiline_mode:
            start_line_no = index - len(current_value.splitlines()) + 2
            end_line_no = line_no
            content = "\n".join(code.splitlines()[start_line_no - 1 : end_line_no])
            field: Field = {
                "line_no_range": (start_line_no, end_line_no),
                "content": content,
                "key": current_key,
                "value": current_value,
            }

            yield field

    # If we ended with multiline_mode, then it wasn't closed which is invalid
    if multiline_mode:
        raise ValueError("Multiline field was not closed")
