import datetime
import dateparser


def parse_date(date_string: str) -> datetime.datetime:
    dt = dateparser.parse(date_string)

    if dt is None:
        raise ValueError(date_string)

    return dt
