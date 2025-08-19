import pytest
from src.fields import split_fields
from src.parser import parse_field, parse_code


class TestParseField:
    def test_key_normalized(self) -> None:
        code = "     TItle    :    Hello    "
        fields = list(split_fields(code))

        assert "title" in parse_field(fields[0])

    def test_unchanged_values(self) -> None:
        code = "     TItle    :    Hello    \nNotes:---World!"

        for field in split_fields(code):
            normalized_key = field["key"].strip().lower()
            assert field["value"] == parse_field(field)[normalized_key]  # type: ignore[literal-required]

    def test_invalid_key(self) -> None:
        code = "Invalid Key : Value"
        fields = list(split_fields(code))

        with pytest.raises(ValueError, match="Invalid key: 'Invalid Key '"):
            parse_field(fields[0])

    def test_title_value(self) -> None:
        code = "Title:      Hello                  "
        fields = list(split_fields(code))

        assert parse_field(fields[0])["title"] == "      Hello                  "

    def test_notes_value(self) -> None:
        code = '''Notes: """
- Item 1
- Item 2
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["notes"] == "\n- Item 1\n- Item 2\n        "

    def test_tags_value(self) -> None:
        code = "Tags:     Tag1    ,    tag2,   TAG 3   "
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tags"] == {"Tag1", "tag2", "TAG 3"}

    def test_tags_value_multiline(self) -> None:
        code = '''Tags: """
            Tag1,
            tag2,
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tags"] == {"Tag1", "tag2"}

    def test_tags_value_empty(self) -> None:
        code = "Tags: "
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tags"] == set()

    def test_tags_value_empty_multiline(self) -> None:
        code = '''Tags: """
            ,
            ,
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tags"] == set()

    def test_tags_value_just_commas(self) -> None:
        code = "Tags: , ,   ,,"
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tags"] == set()

    def test_tasks_value(self) -> None:
        code = '''Tasks: """
Task 1

Task 2
        Task 3
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["tasks"] == ["Task 1", "Task 2", "        Task 3"]

    def test_schedule_value(self) -> None:
        code = '''Schedule: """
        set 2025-01-01
        end 2025-01-02
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-02"),
        ]

    def test_schedule_value_action_only(self) -> None:
        code = '''Schedule: """
        set
        end
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["schedule"] == [("set", None), ("end", None)]

    def test_schedule_value_extra_whitespace(self) -> None:
        code = '''Schedule: """
        set     2025-01-01
          end  2025-01-02
        """'''
        fields = list(split_fields(code))

        assert parse_field(fields[0])["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-02"),
        ]

    def test_schedule_value_invalid_action(self) -> None:
        code = '''Schedule: """
        start 2025-01-01
        """'''
        fields = list(split_fields(code))

        with pytest.raises(ValueError, match="Invalid action: start"):
            parse_field(fields[0])


class TestParseCode:
    def test_parse_code(self) -> None:
        code = '''

Title: Test {function_name}
Notes: Notes are totally optional,    yah
Tags: nuh, uh

Tasks: """
Write a test for {function_name}
Do more coding
Fix bugs
"""

Schedule: """
set
"""

'''
        block_data = parse_code(code, {"function_name": "parse_code"})

        assert block_data["title"] == " Test parse_code"
        assert block_data["notes"] == " Notes are totally optional,    yah"
        assert block_data["tags"] == {"nuh", "uh"}
        assert block_data["tasks"] == [
            "Write a test for parse_code",
            "Do more coding",
            "Fix bugs",
        ]
        assert block_data["schedule"] == [("set", None)]

    def test_parse_code_minimal_required_fields(self) -> None:
        """Test parse_code with only required fields (title and schedule)."""
        code = "Title: Minimal Block\n" 'Schedule: """\n' "set 2025-01-01\n" '"""'
        block_data = parse_code(code, {})

        assert block_data["title"] == " Minimal Block"
        assert block_data["notes"] is None
        assert block_data["tags"] is None
        assert block_data["tasks"] is None
        assert block_data["schedule"] == [("set", "2025-01-01")]

    def test_parse_code_all_fields_present(self) -> None:
        """Test parse_code with all fields present."""
        code = (
            "Title: Complete Block\n"
            "Notes: This is a complete block with all fields\n"
            "Tags: important, urgent, project\n"
            'Tasks: """\n'
            "Task 1\n"
            "Task 2\n"
            "Task 3\n"
            '"""\n'
            'Schedule: """\n'
            "set 2025-01-01\n"
            "end 2025-01-31\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Complete Block"
        assert block_data["notes"] == " This is a complete block with all fields"
        assert block_data["tags"] == {"important", "urgent", "project"}
        assert block_data["tasks"] == ["Task 1", "Task 2", "Task 3"]
        assert block_data["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-31"),
        ]

    def test_parse_code_with_variables(self) -> None:
        """Test parse_code with variable substitution."""
        code = (
            "Title: {project_name} Project\n"
            "Notes: Working on {project_name} since {start_date}\n"
            "Tags: {priority}, {category}\n"
            'Tasks: """\n'
            "Complete {task1}\n"
            "Review {task2}\n"
            '"""\n'
            'Schedule: """\n'
            "set {start_date}\n"
            "end {end_date}\n"
            '"""'
        )
        variables = {
            "project_name": "WatDo",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "priority": "high",
            "category": "engine",
            "task1": "parser implementation",
            "task2": "test coverage",
        }

        block_data = parse_code(code, variables)

        assert block_data["title"] == " WatDo Project"
        assert block_data["notes"] == " Working on WatDo since 2025-01-01"
        assert block_data["tags"] == {"high", "engine"}
        assert block_data["tasks"] == [
            "Complete parser implementation",
            "Review test coverage",
        ]
        assert block_data["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-31"),
        ]

    def test_parse_code_case_insensitive_keys(self) -> None:
        """Test that field keys are case-insensitive."""
        code = (
            "TITLE: Case Insensitive\n"
            "NOTES: Notes with uppercase key\n"
            "TAGS: tag1, tag2\n"
            'TASKS: """\n'
            "Task 1\n"
            '"""\n'
            'SCHEDULE: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Case Insensitive"
        assert block_data["notes"] == " Notes with uppercase key"
        assert block_data["tags"] == {"tag1", "tag2"}
        assert block_data["tasks"] == ["Task 1"]
        assert block_data["schedule"] == [("set", "2025-01-01")]

    def test_parse_code_mixed_case_keys(self) -> None:
        """Test that field keys with mixed case are handled correctly."""
        code = (
            "TiTlE: Mixed Case\n"
            "NoTeS: Mixed case notes\n"
            "TaGs: tag1, tag2\n"
            'TaSkS: """\n'
            "Task 1\n"
            '"""\n'
            'ScHeDuLe: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Mixed Case"
        assert block_data["notes"] == " Mixed case notes"
        assert block_data["tags"] == {"tag1", "tag2"}
        assert block_data["tasks"] == ["Task 1"]
        assert block_data["schedule"] == [("set", "2025-01-01")]

    def test_parse_code_empty_tags(self) -> None:
        """Test parse_code with empty tags field."""
        code = (
            "Title: Empty Tags\n" "Tags: \n" 'Schedule: """\n' "set 2025-01-01\n" '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Empty Tags"
        assert block_data["tags"] == set()
        assert block_data["schedule"] == [("set", "2025-01-01")]

    def test_parse_code_empty_tasks(self) -> None:
        """Test parse_code with empty tasks field."""
        code = (
            "Title: Empty Tasks\n"
            "Tasks: \n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Empty Tasks"
        assert block_data["tasks"] == []
        assert block_data["schedule"] == [("set", "2025-01-01")]

    def test_parse_code_empty_schedule(self) -> None:
        """Test parse_code with empty schedule field."""
        code = "Title: Empty Schedule\n" "Schedule: \n"
        block_data = parse_code(code, {})

        assert block_data["title"] == " Empty Schedule"
        assert block_data["schedule"] == []

    def test_parse_code_whitespace_handling(self) -> None:
        """Test parse_code with various whitespace patterns."""
        code = (
            "    Title:    Whitespace Test    \n"
            "  Notes:   Notes with spaces   \n"
            "Tags:   tag1   ,   tag2   ,   tag3   \n"
            'Tasks: """\n'
            "   Task 1   \n"
            "   Task 2   \n"
            '"""\n'
            'Schedule: """\n'
            "   set   2025-01-01   \n"
            "   end   2025-01-02   \n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == "    Whitespace Test    "
        assert block_data["notes"] == "   Notes with spaces   "
        assert block_data["tags"] == {"tag1", "tag2", "tag3"}
        assert block_data["tasks"] == ["   Task 1   ", "   Task 2   "]
        assert block_data["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-02"),
        ]

    def test_parse_code_multiline_fields(self) -> None:
        """Test parse_code with multiline fields."""
        code = (
            "Title: Multiline Test\n"
            'Notes: """\n'
            "This is a multiline\n"
            "note with multiple\n"
            "lines of content\n"
            '"""\n'
            'Tags: """\n'
            "tag1,\n"
            "tag2,\n"
            "tag3\n"
            '"""\n'
            'Tasks: """\n'
            "First task\n"
            "Second task\n"
            "Third task\n"
            '"""\n'
            'Schedule: """\n'
            "set 2025-01-01\n"
            "end 2025-01-15\n"
            "end 2025-01-31\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Multiline Test"
        assert (
            block_data["notes"]
            == "\nThis is a multiline\nnote with multiple\nlines of content\n"
        )
        assert block_data["tags"] == {"tag1", "tag2", "tag3"}
        assert block_data["tasks"] == ["First task", "Second task", "Third task"]
        assert block_data["schedule"] == [
            ("set", "2025-01-01"),
            ("end", "2025-01-15"),
            ("end", "2025-01-31"),
        ]

    def test_parse_code_duplicate_fields(self) -> None:
        """Test parse_code with duplicate field keys (should use last occurrence)."""
        code = (
            "Title: First Title\n"
            "Title: Second Title\n"
            "Notes: First Notes\n"
            "Notes: Second Notes\n"
            "Tags: tag1, tag2\n"
            "Tags: tag3, tag4\n"
            'Tasks: """\n'
            "Task 1\n"
            '"""\n'
            'Tasks: """\n'
            "Task 2\n"
            '"""\n'
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""\n'
            'Schedule: """\n'
            "end 2025-01-02\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Second Title"
        assert block_data["notes"] == " Second Notes"
        assert block_data["tags"] == {"tag3", "tag4"}
        assert block_data["tasks"] == ["Task 2"]
        assert block_data["schedule"] == [("end", "2025-01-02")]

    def test_parse_code_variable_error_handling(self) -> None:
        """Test parse_code with undefined variables."""
        code = (
            "Title: {undefined_var} Project\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Variable 'undefined_var' is undefined"):
            parse_code(code, {})

    def test_parse_code_invalid_field_format(self) -> None:
        """Test parse_code with invalid field format."""
        code = (
            "Title: Valid Title\n"
            "Invalid Field\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        with pytest.raises(
            ValueError,
            match="Field is missing a colon to separate the key and value in line 2",
        ):
            parse_code(code, {})

    def test_parse_code_empty_value_error(self) -> None:
        """Test parse_code with empty field value."""
        code = "Title:\n" 'Schedule: """\n' "set 2025-01-01\n" '"""'
        with pytest.raises(ValueError, match="Value cannot be empty in line 1"):
            parse_code(code, {})

    def test_parse_code_unclosed_multiline_error(self) -> None:
        """Test parse_code with unclosed multiline field."""
        code = (
            "Title: Unclosed Multiline\n"
            'Notes: """\n'
            "This note never closes\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        with pytest.raises(
            ValueError,
            match="Field is missing a colon to separate the key and value in line 5",
        ):
            parse_code(code, {})

    def test_parse_code_empty_string(self) -> None:
        """Test parse_code with empty string."""
        code = ""

        with pytest.raises(ValueError, match="Missing required field: 'title'"):
            parse_code(code, {})

    def test_parse_code_only_whitespace(self) -> None:
        """Test parse_code with only whitespace."""
        code = "   \n  \n\t\n  "

        with pytest.raises(ValueError, match="Missing required field: 'title'"):
            parse_code(code, {})

    def test_parse_code_special_characters_in_values(self) -> None:
        """Test parse_code with special characters in field values."""
        code = (
            "Title: Special Characters: !@#$%^&*()\n"
            "Notes: Notes with special chars: <>&\"'`\n"
            "Tags: tag-with-dash, tag_with_underscore, tag.with.dots\n"
            'Tasks: """\n'
            "Task with special chars: !@#$%^&*()\n"
            "Task with <>&\"'` characters\n"
            '"""\n'
            'Schedule: """\n'
            "set 2025-01-01 12:00:00\n"
            "end 2025-01-02 23:59:59\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Special Characters: !@#$%^&*()"
        assert block_data["notes"] == " Notes with special chars: <>&\"'`"
        assert block_data["tags"] == {
            "tag-with-dash",
            "tag_with_underscore",
            "tag.with.dots",
        }
        assert block_data["tasks"] == [
            "Task with special chars: !@#$%^&*()",
            "Task with <>&\"'` characters",
        ]
        assert block_data["schedule"] == [
            ("set", "2025-01-01 12:00:00"),
            ("end", "2025-01-02 23:59:59"),
        ]

    def test_parse_code_unicode_characters(self) -> None:
        """Test parse_code with unicode characters."""
        code = (
            "Title: Unicode Test: 你好世界 🌍\n"
            "Notes: Notes with unicode: café, naïve, résumé\n"
            "Tags: émojis, 🚀, 🎉, 🎯\n"
            'Tasks: """\n'
            "Complete unicode task: 你好\n"
            "Fix emoji bug: 🐛\n"
            '"""\n'
            'Schedule: """\n'
            "set 🚀 2025-01-01\n"
            "end 🎯 2025-01-31\n"
            '"""'
        )
        block_data = parse_code(code, {})

        assert block_data["title"] == " Unicode Test: 你好世界 🌍"
        assert block_data["notes"] == " Notes with unicode: café, naïve, résumé"
        assert block_data["tags"] == {"émojis", "🚀", "🎉", "🎯"}
        assert block_data["tasks"] == [
            "Complete unicode task: 你好",
            "Fix emoji bug: 🐛",
        ]
        assert block_data["schedule"] == [
            ("set", "🚀 2025-01-01"),
            ("end", "🎯 2025-01-31"),
        ]

    def test_parse_code_missing_required_fields(self) -> None:
        """Test parse_code with missing required fields."""
        # Test missing title
        code_missing_title = (
            "Notes: Some notes\n"
            "Tags: tag1, tag2\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Missing required field: 'title'"):
            parse_code(code_missing_title, {})

        # Test missing schedule
        code_missing_schedule = (
            "Title: Test Title\n"
            "Notes: Some notes\n"
            "Tags: tag1, tag2\n"
            'Tasks: """\n'
            "Task 1\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Missing required field: 'schedule'"):
            parse_code(code_missing_schedule, {})

        # Test missing both required fields
        code_missing_both = (
            "Notes: Some notes\n" "Tags: tag1, tag2\n" 'Tasks: """\n' "Task 1\n" '"""'
        )
        with pytest.raises(ValueError, match="Missing required field: 'title'"):
            parse_code(code_missing_both, {})

    def test_parse_code_invalid_schedule_actions(self) -> None:
        """Test parse_code with invalid schedule actions."""
        # Test invalid action "start"
        code_invalid_action = (
            "Title: Invalid Action Test\n" 'Schedule: """\n' "start 2025-01-01\n" '"""'
        )
        with pytest.raises(ValueError, match="Invalid action: start"):
            parse_code(code_invalid_action, {})

        # Test invalid action "finish"
        code_invalid_action2 = (
            "Title: Invalid Action Test 2\n"
            'Schedule: """\n'
            "finish 2025-01-31\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Invalid action: finish"):
            parse_code(code_invalid_action2, {})

        # Test invalid action "begin"
        code_invalid_action3 = (
            "Title: Invalid Action Test 3\n"
            'Schedule: """\n'
            "begin 2025-01-01\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Invalid action: begin"):
            parse_code(code_invalid_action3, {})

        # Test mixed valid and invalid actions
        code_mixed_actions = (
            "Title: Mixed Actions Test\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            "invalid_action 2025-01-02\n"
            '"""'
        )
        with pytest.raises(ValueError, match="Invalid action: invalid_action"):
            parse_code(code_mixed_actions, {})

    def test_parse_code_fields_in_any_order(self) -> None:
        """Test parse_code with fields in different orders."""
        # Test with Schedule first, then Title
        code_schedule_first = (
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""\n'
            "Title: Schedule First\n"
            "Notes: Notes after title\n"
            "Tags: tag1, tag2\n"
            'Tasks: """\n'
            "Task 1\n"
            '"""'
        )
        block_data = parse_code(code_schedule_first, {})
        assert block_data["title"] == " Schedule First"
        assert block_data["schedule"] == [("set", "2025-01-01")]

        # Test with Tags first, then Title, then Schedule
        code_tags_first = (
            "Tags: tag1, tag2\n"
            "Title: Tags First\n"
            'Schedule: """\n'
            "end 2025-01-31\n"
            '"""\n'
            "Notes: Notes at the end\n"
            'Tasks: """\n'
            "Task 1\n"
            '"""'
        )
        block_data = parse_code(code_tags_first, {})
        assert block_data["title"] == " Tags First"
        assert block_data["tags"] == {"tag1", "tag2"}
        assert block_data["schedule"] == [("end", "2025-01-31")]

        # Test with Tasks first, then Schedule, then Title
        code_tasks_first = (
            'Tasks: """\n'
            "Task 1\n"
            "Task 2\n"
            '"""\n'
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""\n'
            "Title: Tasks First\n"
            "Notes: Notes at the end\n"
            "Tags: tag3, tag4"
        )
        block_data = parse_code(code_tasks_first, {})
        assert block_data["title"] == " Tasks First"
        assert block_data["tasks"] == ["Task 1", "Task 2"]
        assert block_data["schedule"] == [("set", "2025-01-01")]
        assert block_data["tags"] == {"tag3", "tag4"}

        # Test with Notes first, then Schedule, then Title
        code_notes_first = (
            "Notes: Notes come first\n"
            'Schedule: """\n'
            "end 2025-01-31\n"
            '"""\n'
            "Title: Notes First\n"
            "Tags: tag5, tag6\n"
            'Tasks: """\n'
            "Task 3\n"
            '"""'
        )
        block_data = parse_code(code_notes_first, {})
        assert block_data["title"] == " Notes First"
        assert block_data["notes"] == " Notes come first"
        assert block_data["schedule"] == [("end", "2025-01-31")]
        assert block_data["tags"] == {"tag5", "tag6"}
        assert block_data["tasks"] == ["Task 3"]

        # Test with completely random order
        code_random_order = (
            "Tags: random, order\n"
            'Tasks: """\n'
            "Random task\n"
            '"""\n'
            "Title: Random Order\n"
            'Schedule: """\n'
            "set 2025-01-01\n"
            '"""\n'
            "Notes: Random notes"
        )
        block_data = parse_code(code_random_order, {})
        assert block_data["title"] == " Random Order"
        assert block_data["notes"] == " Random notes"
        assert block_data["tags"] == {"random", "order"}
        assert block_data["tasks"] == ["Random task"]
        assert block_data["schedule"] == [("set", "2025-01-01")]
