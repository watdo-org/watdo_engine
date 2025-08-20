import datetime
from src.date import parse_date_string


class TestParseDateString:
    def test_absolute_date(self) -> None:
        """Test parsing absolute date strings"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("2024-01-20", base)
        assert result == datetime.datetime(2024, 1, 20, 0, 0, 0)

    def test_relative_date_tomorrow(self) -> None:
        """Test parsing relative date 'tomorrow'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("tomorrow", base)
        assert result == datetime.datetime(2024, 1, 16, 12, 0, 0)

    def test_relative_date_yesterday(self) -> None:
        """Test parsing relative date 'yesterday'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("yesterday", base)
        assert result == datetime.datetime(2024, 1, 14, 12, 0, 0)

    def test_relative_date_next_week(self) -> None:
        """Test parsing relative date 'next week'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("next week", base)
        assert result == datetime.datetime(2024, 1, 22, 12, 0, 0)

    def test_relative_date_last_month(self) -> None:
        """Test parsing relative date 'last month'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("last month", base)
        assert result == datetime.datetime(2023, 12, 15, 12, 0, 0)

    def test_time_with_date(self) -> None:
        """Test parsing date with time"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("2024-01-20 15:30", base)
        assert result == datetime.datetime(2024, 1, 20, 15, 30, 0)

    def test_natural_language_date(self) -> None:
        """Test parsing natural language dates"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("January 20th", base)
        assert result == datetime.datetime(2024, 1, 20, 0, 0, 0)

    def test_invalid_date_string(self) -> None:
        """Test parsing invalid date string returns None"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("not a date", base)
        assert result is None

    def test_empty_string(self) -> None:
        """Test parsing empty string returns None"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("", base)
        assert result is None

    def test_weekday_relative(self) -> None:
        """Test parsing relative weekday"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)  # Monday
        result = parse_date_string("friday", base)
        # dateparser interprets "friday" as the previous Friday when base is Monday
        assert result == datetime.datetime(2024, 1, 12, 0, 0, 0)

    def test_time_only(self) -> None:
        """Test parsing time only (should use base date)"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0)
        result = parse_date_string("15:30", base)
        assert result == datetime.datetime(2024, 1, 15, 15, 30, 0)
