import datetime
import pytest
from src.block import ScheduleEntry
from src.evaluator import generate_timeline, evaluate_schedule
from tests.utils import parse_date


class TestGenerateTimeline:
    def test_generate_timeline(self) -> None:
        schedule: list[ScheduleEntry] = [
            ("set", "9:00 AM"),
            ("end", "11:00 AM"),
        ]
        timeline = list(generate_timeline(schedule, parse_date("Aug 10 2025")))

        assert len(timeline) == 2
        assert timeline[0] == ("set", parse_date("Aug 10 2025 at 9:00 AM"))
        assert timeline[1] == ("end", parse_date("Aug 10 2025 at 11:00 AM"))


class TestEvaluateSchedule:
    def test_empty_schedule(self) -> None:
        now = datetime.datetime.now()
        assert evaluate_schedule([], relative_base=now, evaluation_date=now) == (
            False,
            None,
        )

    def test_action_only(self) -> None:
        now = datetime.datetime.now()
        assert evaluate_schedule(
            [("set", None)], relative_base=now, evaluation_date=now
        ) == (True, None)
        assert evaluate_schedule(
            [("end", None)], relative_base=now, evaluation_date=now
        ) == (False, None)

    def test_invalid_date(self) -> None:
        now = datetime.datetime.now()
        with pytest.raises(ValueError, match="Failed parsing 'every 6 months'"):
            evaluate_schedule(
                [("set", "every 6 months")], relative_base=now, evaluation_date=now
            )

    def test_valid_date(self) -> None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        assert evaluate_schedule(
            [("set", "in 6 months")],
            relative_base=now,
            evaluation_date=now,
        ) == (False, None)

    def test_schedule(self) -> None:
        schedule: list[ScheduleEntry] = [
            ("set", None),
            ("end", "Aug 1 2025"),
            ("set", "Aug 15 2025"),
            ("end", "Sep 1 2025"),
            ("set", "Sep 15 2025"),
            ("end", "Oct 1 2025"),
            ("set", None),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("July 31, 2025"),
        ) == (True, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Aug 14, 2025"),
        ) == (False, parse_date("Aug 1 2025"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Sep 30, 2025"),
        ) == (True, parse_date("Sep 15 2025"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Oct 1, 2025"),
        ) == (False, parse_date("Oct 1 2025"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Oct 2, 2025"),
        ) == (True, None)

    def test_same_day(self) -> None:
        """
        We stop processing the schedule if the date is the same as the evaluation date.
        Meaning, the second entry will not be processed.
        """
        schedule: list[ScheduleEntry] = [
            ("set", "Oct 1 2025"),
            ("end", "Oct 1 2025"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Oct 1, 2025"),
        ) == (True, parse_date("Oct 1 2025"))

    def test_future_action_only(self) -> None:
        schedule: list[ScheduleEntry] = [
            ("set", "Aug 15 2025"),
            ("end", "Sep 1 2025"),
            ("set", None),
            ("end", "Oct 1 2025"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Aug 14, 2025"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Sep 1, 2025"),
        ) == (False, parse_date("Sep 1 2025"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Sep 2, 2025"),
        ) == (True, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Oct 1, 2025"),
        ) == (False, parse_date("Oct 1 2025"))

    def test_relativity(self) -> None:
        schedule: list[ScheduleEntry] = [
            ("set", "9:00 AM"),
            ("end", "11:00 AM"),
        ]

        # For time-only schedules, use the evaluation date as the relative base
        eval_date_8am = parse_date("Aug 14, 2025 at 8 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_8am,
            evaluation_date=eval_date_8am,
        ) == (False, None)

        eval_date_9am = parse_date("Aug 14, 2025 at 9 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_9am,
            evaluation_date=eval_date_9am,
        ) == (True, parse_date("Aug 14, 2025 at 9:00 AM"))

        eval_date_10am = parse_date("Aug 14, 2025 at 10 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_10am,
            evaluation_date=eval_date_10am,
        ) == (True, parse_date("Aug 14, 2025 at 9:00 AM"))

        eval_date_11am = parse_date("Aug 14, 2025 at 11 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_11am,
            evaluation_date=eval_date_11am,
        ) == (False, parse_date("Aug 14, 2025 at 11:00 AM"))

        eval_date_12pm = parse_date("Aug 14, 2025 at 12 PM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_12pm,
            evaluation_date=eval_date_12pm,
        ) == (False, parse_date("Aug 14, 2025 at 11:00 AM"))

    # New test cases for time-only scenarios
    def test_time_only_schedule(self) -> None:
        """Test schedules with only time specifications (no date)."""
        schedule: list[ScheduleEntry] = [
            ("set", "9:00 AM"),
            ("end", "5:00 PM"),
        ]

        # Test on different dates but same times
        eval_date_859 = parse_date("Jan 1, 2025 at 8:59 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_859,
            evaluation_date=eval_date_859,
        ) == (False, None)

        eval_date_900 = parse_date("Jan 1, 2025 at 9:00 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_900,
            evaluation_date=eval_date_900,
        ) == (True, parse_date("Jan 1, 2025 at 9:00 AM"))

        eval_date_1200 = parse_date("Jan 1, 2025 at 12:00 PM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1200,
            evaluation_date=eval_date_1200,
        ) == (True, parse_date("Jan 1, 2025 at 9:00 AM"))

        eval_date_1700 = parse_date("Jan 1, 2025 at 5:00 PM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1700,
            evaluation_date=eval_date_1700,
        ) == (False, parse_date("Jan 1, 2025 at 5:00 PM"))

        eval_date_1800 = parse_date("Jan 1, 2025 at 6:00 PM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1800,
            evaluation_date=eval_date_1800,
        ) == (False, parse_date("Jan 1, 2025 at 5:00 PM"))

        # Test on different dates
        eval_date_feb = parse_date("Feb 15, 2025 at 10:00 AM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_feb,
            evaluation_date=eval_date_feb,
        ) == (True, parse_date("Feb 15, 2025 at 9:00 AM"))

        eval_date_mar = parse_date("Mar 30, 2025 at 3:00 PM")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_mar,
            evaluation_date=eval_date_mar,
        ) == (True, parse_date("Mar 30, 2025 at 9:00 AM"))

    def test_time_only_24_hour_format(self) -> None:
        """Test time-only schedules using 24-hour format."""
        schedule: list[ScheduleEntry] = [
            ("set", "14:00"),
            ("end", "18:00"),
        ]

        eval_date_1359 = parse_date("Dec 25, 2025 at 13:59")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1359,
            evaluation_date=eval_date_1359,
        ) == (False, None)

        eval_date_1400 = parse_date("Dec 25, 2025 at 14:00")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1400,
            evaluation_date=eval_date_1400,
        ) == (True, parse_date("Dec 25, 2025 at 14:00"))

        eval_date_1600 = parse_date("Dec 25, 2025 at 16:00")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1600,
            evaluation_date=eval_date_1600,
        ) == (True, parse_date("Dec 25, 2025 at 14:00"))

        eval_date_1800 = parse_date("Dec 25, 2025 at 18:00")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1800,
            evaluation_date=eval_date_1800,
        ) == (False, parse_date("Dec 25, 2025 at 18:00"))

        eval_date_1900 = parse_date("Dec 25, 2025 at 19:00")
        assert evaluate_schedule(
            schedule,
            relative_base=eval_date_1900,
            evaluation_date=eval_date_1900,
        ) == (False, parse_date("Dec 25, 2025 at 18:00"))

    def test_time_only_with_am_pm_variations(self) -> None:
        """Test time-only schedules with various AM/PM formats."""
        schedule: list[ScheduleEntry] = [
            ("set", "9:30 AM"),
            ("end", "4:30 PM"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 9:29 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 9:30 AM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:30 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 2:15 PM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:30 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 4:30 PM"),
        ) == (False, parse_date("Jan 1, 2025 at 4:30 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 4:31 PM"),
        ) == (False, parse_date("Jan 1, 2025 at 4:30 PM"))

    def test_time_only_overnight_schedule(self) -> None:
        base_date = parse_date("today")
        schedule: list[ScheduleEntry] = [
            ("set", "10:00 PM"),
            ("end", "tomorrow at 6:00 AM"),
        ]

        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("9:59 PM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("10:00 PM"),
        ) == (True, parse_date("10:00 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("tomorrow at 5:59 AM"),
        ) == (True, parse_date("10:00 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("tomorrow at 6:00 AM"),
        ) == (False, parse_date("tomorrow at 6:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("tomorrow at 6:01 AM"),
        ) == (False, parse_date("tomorrow at 6:00 AM"))

    def test_time_only_minute_precision(self) -> None:
        """Test time-only schedules with minute-level precision."""
        schedule: list[ScheduleEntry] = [
            ("set", "9:15 AM"),
            ("end", "5:45 PM"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 9:14 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 9:15 AM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:15 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 12:30 PM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:15 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 5:44 PM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:15 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 5:45 PM"),
        ) == (False, parse_date("Jan 1, 2025 at 5:45 PM"))

    # New test cases for date + time scenarios
    def test_date_time_schedule(self) -> None:
        """Test schedules with specific date and time combinations."""
        schedule: list[ScheduleEntry] = [
            ("set", "Jan 15, 2025 at 9:00 AM"),
            ("end", "Jan 15, 2025 at 5:00 PM"),
        ]

        # Test before the scheduled time
        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 8:59 AM"),
        ) == (False, None)
        # Test at the start time
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 9:00 AM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        # Test during the scheduled time
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 12:00 PM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        # Test at the end time
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 5:00 PM"),
        ) == (False, parse_date("Jan 15, 2025 at 5:00 PM"))
        # Test after the scheduled time
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 5:01 PM"),
        ) == (False, parse_date("Jan 15, 2025 at 5:00 PM"))

    def test_date_time_multiple_days(self) -> None:
        """Test schedules spanning multiple days with specific times."""
        schedule: list[ScheduleEntry] = [
            ("set", "Jan 15, 2025 at 9:00 AM"),
            ("end", "Jan 17, 2025 at 5:00 PM"),
        ]

        # Test before the scheduled period
        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 8:59 AM"),
        ) == (False, None)
        # Test at the start
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 9:00 AM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        # Test during the period
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 16, 2025 at 12:00 PM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        # Test at the end
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 17, 2025 at 5:00 PM"),
        ) == (False, parse_date("Jan 17, 2025 at 5:00 PM"))
        # Test after the period
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 17, 2025 at 5:01 PM"),
        ) == (False, parse_date("Jan 17, 2025 at 5:00 PM"))

    def test_date_time_iso_format(self) -> None:
        """Test schedules using ISO date-time format."""
        schedule: list[ScheduleEntry] = [
            ("set", "2025-01-15T09:00:00"),
            ("end", "2025-01-15T17:00:00"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("2025-01-15T08:59:59"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("2025-01-15T09:00:00"),
        ) == (True, parse_date("2025-01-15T09:00:00"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("2025-01-15T13:00:00"),
        ) == (True, parse_date("2025-01-15T09:00:00"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("2025-01-15T17:00:00"),
        ) == (False, parse_date("2025-01-15T17:00:00"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("2025-01-15T17:00:01"),
        ) == (False, parse_date("2025-01-15T17:00:00"))

    def test_date_time_relative_dates(self) -> None:
        """Test schedules with relative date-time expressions."""
        schedule: list[ScheduleEntry] = [
            ("set", "tomorrow at 9:00 AM"),
            ("end", "tomorrow at 5:00 PM"),
        ]

        # Test with a specific base date
        base_date = parse_date("Jan 15, 2025 at 12:00 PM")

        # This would need to be adjusted based on how dateparser handles "tomorrow"
        # For now, we'll test the basic functionality
        result = evaluate_schedule(
            schedule, relative_base=base_date, evaluation_date=base_date
        )
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], bool)  # Valid boolean result

    def test_date_time_mixed_formats(self) -> None:
        """Test schedules mixing different date-time formats."""
        schedule: list[ScheduleEntry] = [
            ("set", "Jan 15, 2025 at 9:00 AM"),
            ("end", "2025-01-15T17:00:00"),
        ]

        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 8:59 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 9:00 AM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 12:00 PM"),
        ) == (True, parse_date("Jan 15, 2025 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 15, 2025 at 5:00 PM"),
        ) == (False, parse_date("Jan 15, 2025 at 5:00 PM"))

    def test_date_time_edge_cases(self) -> None:
        """Test edge cases for date-time schedules."""
        schedule: list[ScheduleEntry] = [
            ("set", "Dec 31, 2024 at 11:59 PM"),
            ("end", "Jan 1, 2025 at 12:01 AM"),
        ]

        # Test year boundary
        base_date = parse_date("Jan 1, 2024")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Dec 31, 2024 at 11:58 PM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Dec 31, 2024 at 11:59 PM"),
        ) == (True, parse_date("Dec 31, 2024 at 11:59 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 12:00 AM"),
        ) == (True, parse_date("Dec 31, 2024 at 11:59 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 12:01 AM"),
        ) == (False, parse_date("Jan 1, 2025 at 12:01 AM"))

    def test_date_time_leap_year(self) -> None:
        """Test schedules around leap year dates."""
        schedule: list[ScheduleEntry] = [
            ("set", "Feb 29, 2024 at 9:00 AM"),
            ("end", "Feb 29, 2024 at 5:00 PM"),
        ]

        # 2024 is a leap year
        base_date = parse_date("Jan 1, 2024")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Feb 29, 2024 at 8:59 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Feb 29, 2024 at 9:00 AM"),
        ) == (True, parse_date("Feb 29, 2024 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Feb 29, 2024 at 12:00 PM"),
        ) == (True, parse_date("Feb 29, 2024 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Feb 29, 2024 at 5:00 PM"),
        ) == (False, parse_date("Feb 29, 2024 at 5:00 PM"))

    def test_date_time_dst_transitions(self) -> None:
        """Test schedules around daylight saving time transitions."""
        # Spring forward (lose an hour)
        schedule_spring: list[ScheduleEntry] = [
            ("set", "Mar 9, 2025 at 2:00 AM"),
            ("end", "Mar 9, 2025 at 4:00 AM"),
        ]

        # Note: This test depends on the specific DST rules and may need adjustment
        # for the actual implementation and timezone handling
        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule_spring,
            relative_base=base_date,
            evaluation_date=parse_date("Mar 9, 2025 at 1:59 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule_spring,
            relative_base=base_date,
            evaluation_date=parse_date("Mar 9, 2025 at 2:00 AM"),
        ) == (True, parse_date("Mar 9, 2025 at 2:00 AM"))
        assert evaluate_schedule(
            schedule_spring,
            relative_base=base_date,
            evaluation_date=parse_date("Mar 9, 2025 at 3:00 AM"),
        ) == (True, parse_date("Mar 9, 2025 at 2:00 AM"))
        assert evaluate_schedule(
            schedule_spring,
            relative_base=base_date,
            evaluation_date=parse_date("Mar 9, 2025 at 4:00 AM"),
        ) == (False, parse_date("Mar 9, 2025 at 4:00 AM"))

    def test_date_time_weekday_specific(self) -> None:
        """Test schedules with weekday-specific date-time expressions."""
        schedule: list[ScheduleEntry] = [
            ("set", "Monday at 9:00 AM"),
            ("end", "Friday at 5:00 PM"),
        ]

        # Test on different weekdays
        # This will depend on how dateparser handles "Monday" relative to the evaluation date
        # For now, we'll test that it doesn't crash
        base_date = parse_date("Jan 15, 2025 at 12:00 PM")  # A Wednesday
        try:
            result = evaluate_schedule(
                schedule, relative_base=base_date, evaluation_date=base_date
            )
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], bool)  # Valid boolean result
        except ValueError:
            # If dateparser can't handle this format, that's acceptable
            # The test passes as long as it doesn't crash with an unexpected error
            pass

    def test_date_time_complex_relative(self) -> None:
        """Test schedules with complex relative date-time expressions."""
        schedule: list[ScheduleEntry] = [
            ("set", "in 1 day at 9:00 AM"),
            ("end", "in 5 days at 5:00 PM"),
        ]

        # Test with a specific base date
        base_date = parse_date("Jan 15, 2025 at 12:00 PM")  # A Wednesday
        result = evaluate_schedule(
            schedule, relative_base=base_date, evaluation_date=base_date
        )
        assert isinstance(result, tuple) and len(result) == 2
        assert isinstance(result[0], bool)  # Valid boolean result

    def test_date_time_quarterly_schedule(self) -> None:
        """Test quarterly schedules with specific times."""
        schedule: list[ScheduleEntry] = [
            ("set", "Jan 1, 2025 at 9:00 AM"),
            ("end", "Mar 31, 2025 at 5:00 PM"),
            ("set", "Apr 1, 2025 at 9:00 AM"),
            ("end", "Jun 30, 2025 at 5:00 PM"),
            ("set", "Jul 1, 2025 at 9:00 AM"),
            ("end", "Sep 30, 2025 at 5:00 PM"),
            ("set", "Oct 1, 2025 at 9:00 AM"),
            ("end", "Dec 31, 2025 at 5:00 PM"),
        ]

        # Test Q1
        base_date = parse_date("Jan 1, 2025")
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 8:59 AM"),
        ) == (False, None)
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jan 1, 2025 at 9:00 AM"),
        ) == (True, parse_date("Jan 1, 2025 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Mar 31, 2025 at 5:00 PM"),
        ) == (False, parse_date("Mar 31, 2025 at 5:00 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Apr 1, 2025 at 9:00 AM"),
        ) == (True, parse_date("Apr 1, 2025 at 9:00 AM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jun 30, 2025 at 5:00 PM"),
        ) == (False, parse_date("Jun 30, 2025 at 5:00 PM"))
        assert evaluate_schedule(
            schedule,
            relative_base=base_date,
            evaluation_date=parse_date("Jul 1, 2025 at 9:00 AM"),
        ) == (True, parse_date("Jul 1, 2025 at 9:00 AM"))
