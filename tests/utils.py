import datetime
import dateparser


def parse_date(date_string: str, *, timezone: str = "UTC") -> datetime.datetime:
    dt = dateparser.parse(
        date_string,
        settings={"TIMEZONE": timezone, "RETURN_AS_TIMEZONE_AWARE": True},
    )

    if dt is None:
        raise ValueError(date_string)

    return dt
