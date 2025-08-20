import datetime
from datetime import timezone
from src.date import parse_date_string
from tests.utils import parse_date


class TestParseDateString:
    def test_timezone(self) -> None:
        """Test basic timezone functionality"""
        assert parse_date_string("Aug 1 2025", timezone="UTC+8") == parse_date(
            "Aug 1 2025", timezone="UTC+8"
        )
        assert parse_date_string("Aug 1 2025 UTC+8") == parse_date(
            "Aug 1 2025", timezone="UTC+8"
        )
        assert parse_date_string(
            "Aug 1 2025",
            timezone="UTC+8",
        ) == parse_date("Aug 1 2025 UTC+8")
        assert parse_date_string("Aug 1 2025 UTC+8") == parse_date("Aug 1 2025 UTC+8")
        assert parse_date_string("Aug 1 2025 UTC+8", timezone="UTC-3") == parse_date(
            "Aug 1 2025 UTC+8"
        )
        assert parse_date_string("Aug 1 2025 UTC+8") == parse_date(
            "Aug 1 2025 UTC+8", timezone="UTC-3"
        )
        assert parse_date_string("Aug 1 2025 UTC+8", timezone="UTC-3") == parse_date(
            "Aug 1 2025 UTC+8", timezone="UTC-3"
        )

    def test_timezone_formats(self) -> None:
        """Test various timezone format specifications"""
        # Test various timezone formats
        assert parse_date_string("Aug 1 2025", timezone="UTC-5") == parse_date(
            "Aug 1 2025", timezone="UTC-5"
        )
        assert parse_date_string("Aug 1 2025", timezone="UTC+0") == parse_date(
            "Aug 1 2025", timezone="UTC+0"
        )
        assert parse_date_string("Aug 1 2025", timezone="UTC+12") == parse_date(
            "Aug 1 2025", timezone="UTC+12"
        )
        assert parse_date_string("Aug 1 2025", timezone="UTC-12") == parse_date(
            "Aug 1 2025", timezone="UTC-12"
        )

        # Test fractional timezone offsets
        assert parse_date_string("Aug 1 2025", timezone="UTC+5:30") == parse_date(
            "Aug 1 2025", timezone="UTC+5:30"
        )
        assert parse_date_string("Aug 1 2025", timezone="UTC-3:30") == parse_date(
            "Aug 1 2025", timezone="UTC-3:30"
        )

        # Test timezone abbreviations (common ones)
        assert parse_date_string("Aug 1 2025", timezone="EST") == parse_date(
            "Aug 1 2025", timezone="EST"
        )
        assert parse_date_string("Aug 1 2025", timezone="PST") == parse_date(
            "Aug 1 2025", timezone="PST"
        )
        assert parse_date_string("Aug 1 2025", timezone="GMT") == parse_date(
            "Aug 1 2025", timezone="GMT"
        )

    def test_timezone_with_time_components(self) -> None:
        """Test timezone handling with time components"""
        # Test timezone-aware dates with different timezone parameters
        assert parse_date_string(
            "Aug 1 2025 10:00 UTC+3", timezone="UTC+8"
        ) == parse_date("Aug 1 2025 10:00 UTC+3", timezone="UTC+8")
        assert parse_date_string(
            "Aug 1 2025 10:00 UTC+3", timezone="UTC-2"
        ) == parse_date("Aug 1 2025 10:00 UTC+3", timezone="UTC-2")

        # Test dates with explicit timezone in string vs parameter
        assert parse_date_string("Aug 1 2025 15:30 UTC+5") == parse_date(
            "Aug 1 2025 15:30 UTC+5"
        )
        assert parse_date_string("Aug 1 2025 15:30", timezone="UTC+5") == parse_date(
            "Aug 1 2025 15:30", timezone="UTC+5"
        )

        # Test timezone with time components
        assert parse_date_string("Aug 1 2025 14:30", timezone="UTC+9") == parse_date(
            "Aug 1 2025 14:30", timezone="UTC+9"
        )
        assert parse_date_string("Aug 1 2025 23:45", timezone="UTC-4") == parse_date(
            "Aug 1 2025 23:45", timezone="UTC-4"
        )

    def test_timezone_parameter_override(self) -> None:
        """Test that timezone parameter correctly overrides string timezone"""
        # Test edge case: timezone parameter overrides string timezone
        assert parse_date_string(
            "Aug 1 2025 10:00 UTC+2", timezone="UTC+7"
        ) == parse_date("Aug 1 2025 10:00 UTC+2", timezone="UTC+7")

        # Test midnight and noon edge cases with timezones
        assert parse_date_string("Aug 1 2025 00:00", timezone="UTC+6") == parse_date(
            "Aug 1 2025 00:00", timezone="UTC+6"
        )
        assert parse_date_string("Aug 1 2025 12:00", timezone="UTC-8") == parse_date(
            "Aug 1 2025 12:00", timezone="UTC-8"
        )

    def test_timezone_edge_cases(self) -> None:
        """Test timezone edge cases and boundary conditions"""
        # Test extreme timezone offsets
        assert parse_date_string("Aug 1 2025", timezone="UTC+14") == parse_date(
            "Aug 1 2025", timezone="UTC+14"
        )
        assert parse_date_string("Aug 1 2025", timezone="UTC-12") == parse_date(
            "Aug 1 2025", timezone="UTC-12"
        )

        # Test timezone with seconds precision
        assert parse_date_string(
            "Aug 1 2025 12:30:45", timezone="UTC+5:30:45"
        ) == parse_date("Aug 1 2025 12:30:45", timezone="UTC+5:30:45")

        # Test timezone parameter with None (should default to UTC)
        assert parse_date_string("Aug 1 2025", timezone=None) == parse_date(
            "Aug 1 2025", timezone="UTC"
        )

        # Test empty timezone string (should default to UTC)
        assert parse_date_string("Aug 1 2025", timezone="") == parse_date(
            "Aug 1 2025", timezone="UTC"
        )

    def test_timezone_with_relative_operations(self) -> None:
        """Test timezone handling with relative date operations"""
        # Test relative operations with timezone
        assert parse_date_string(
            "Aug 1 2025 -> in 2 days", timezone="UTC+8"
        ) == parse_date("Aug 3 2025", timezone="UTC+8")
        assert parse_date_string(
            "Aug 1 2025 UTC+5 -> in 1 week", timezone="UTC+8"
        ) == parse_date("Aug 8 2025 UTC+5", timezone="UTC+8")

        # Test chained relative operations with timezone
        assert parse_date_string(
            "Aug 1 2025 -> in 2 days -> in 3 hours", timezone="UTC+3"
        ) == parse_date("Aug 3 2025 03:00", timezone="UTC+3")

    def test_timezone_conversion_consistency(self) -> None:
        """Test that timezone conversions are consistent and accurate"""
        # Test that same time in different timezones produces different UTC times
        base_time = "Aug 1 2025 12:00"
        utc_plus_5 = parse_date_string(base_time, timezone="UTC+5")
        utc_plus_8 = parse_date_string(base_time, timezone="UTC+8")

        # These should be different UTC times (3 hours apart)
        assert utc_plus_5 != utc_plus_8

        # Test that timezone parameter correctly affects the base timezone
        assert parse_date_string("12:00", timezone="UTC+5") != parse_date_string(
            "12:00", timezone="UTC+8"
        )

    def test_relative_operation(self) -> None:
        assert parse_date_string("Aug 1, 2025 -> in 4 days") == parse_date("Aug 5 2025")
        assert parse_date_string("Aug 1, 2025->in 2 months") == parse_date("Oct 1 2025")
        assert parse_date_string("Aug 1, 2025 ->in 3 years") == parse_date("Aug 1 2028")
        assert parse_date_string("Aug 9 2025 -> 4 days ago") == parse_date("Aug 5 2025")
        assert parse_date_string(
            "in 3 days -> in 4 days->1 days",  # + 3 days + 4 days - 1 day
            parse_date("Aug 10, 2000"),
        ) == parse_date("Aug 16 2000")

    def test_relative_operation_invalid(self) -> None:
        assert parse_date_string("") is None
        assert parse_date_string("-> Aug 1, 2025 -> in 4 days") is None
        assert parse_date_string("Aug 1, 2025 -> in 4 days ->") is None

    def test_absolute_date(self) -> None:
        """Test parsing absolute date strings"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("2024-01-20", base)
        assert result == datetime.datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)

    def test_relative_date_tomorrow(self) -> None:
        """Test parsing relative date 'tomorrow'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("tomorrow", base)
        assert result == datetime.datetime(2024, 1, 16, 12, 0, 0, tzinfo=timezone.utc)

    def test_relative_date_yesterday(self) -> None:
        """Test parsing relative date 'yesterday'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("yesterday", base)
        assert result == datetime.datetime(2024, 1, 14, 12, 0, 0, tzinfo=timezone.utc)

    def test_relative_date_next_week(self) -> None:
        """Test parsing relative date 'next week'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("next week", base)
        assert result == datetime.datetime(2024, 1, 22, 12, 0, 0, tzinfo=timezone.utc)

    def test_relative_date_last_month(self) -> None:
        """Test parsing relative date 'last month'"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("last month", base)
        assert result == datetime.datetime(2023, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_time_with_date(self) -> None:
        """Test parsing date with time"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("2024-01-20 15:30", base)
        assert result == datetime.datetime(2024, 1, 20, 15, 30, 0, tzinfo=timezone.utc)

    def test_natural_language_date(self) -> None:
        """Test parsing natural language dates"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("January 20th", base)
        assert result == datetime.datetime(2024, 1, 20, 0, 0, 0, tzinfo=timezone.utc)

    def test_invalid_date_string(self) -> None:
        """Test parsing invalid date string returns None"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("not a date", base)
        assert result is None

    def test_empty_string(self) -> None:
        """Test parsing empty string returns None"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("", base)
        assert result is None

    def test_weekday_relative(self) -> None:
        """Test parsing relative weekday"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)  # Monday
        result = parse_date_string("friday", base)
        # dateparser interprets "friday" as the previous Friday when base is Monday
        assert result == datetime.datetime(2024, 1, 12, 0, 0, 0, tzinfo=timezone.utc)

    def test_time_only(self) -> None:
        """Test parsing time only (should use base date)"""
        base = datetime.datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = parse_date_string("15:30", base)
        assert result == datetime.datetime(2024, 1, 15, 15, 30, 0, tzinfo=timezone.utc)
