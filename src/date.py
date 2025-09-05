import datetime
import dateutil
import dateparser


def parse_date_string(
    date_string_expression: str,
    relative_base: datetime.datetime | None = None,
    *,
    timezone: str | None = None,
) -> datetime.datetime | None:
    timezone = timezone or "UTC"
    last_date: datetime.datetime

    if relative_base is not None:
        tz = dateutil.tz.gettz(timezone)
        relative_base = relative_base.astimezone(tz)

    for date_string in date_string_expression.split("->"):
        date = dateparser.parse(
            date_string,
            settings={
                "TIMEZONE": timezone,
                "RETURN_AS_TIMEZONE_AWARE": True,
                **({} if relative_base is None else {"RELATIVE_BASE": relative_base}),
            },
        )

        if date is None:
            return None

        last_date = date
        relative_base = date

    return last_date
