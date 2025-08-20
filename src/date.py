import datetime
import dateparser


def parse_date_string(
    date_string: str,
    relative_base: datetime.datetime,
) -> datetime.datetime | None:
    return dateparser.parse(
        date_string,
        settings={"RELATIVE_BASE": relative_base},
    )
