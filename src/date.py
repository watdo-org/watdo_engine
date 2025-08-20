import datetime
import dateparser


def parse_date_string(
    date_string_expression: str,
    relative_base: datetime.datetime | None = None,
) -> datetime.datetime | None:
    last_date: datetime.datetime

    for date_string in date_string_expression.split("->"):
        date = dateparser.parse(
            date_string,
            settings=(
                None if relative_base is None else {"RELATIVE_BASE": relative_base}
            ),
        )

        if date is None:
            return None

        last_date = date
        relative_base = date

    return last_date
