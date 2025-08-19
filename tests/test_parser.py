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


class TestParseCode:
    @pytest.mark.skip(reason="Not implemented yet")
    def test_parse_code(self) -> None:
        pass
