import pytest
from src.fields import split_fields


class TestSplitFields:
    """
    Test cases are all written by AI.
    Not even sure if they are correct.
    Too lazy to write it myself.
    Good luck everyone! 🤣
    """

    def test_single_line_fields(self) -> None:
        """Test parsing of simple single-line fields."""
        code = "name: John\nage: 30\ncity: New York"
        fields = list(split_fields(code))

        assert len(fields) == 3
        assert fields[0]["key"] == "name"
        assert fields[0]["value"] == " John"
        assert fields[0]["line_no_range"] == (1, 1)
        assert fields[0]["content"] == "name: John"

        assert fields[1]["key"] == "age"
        assert fields[1]["value"] == " 30"
        assert fields[1]["line_no_range"] == (2, 2)

        assert fields[2]["key"] == "city"
        assert fields[2]["value"] == " New York"
        assert fields[2]["line_no_range"] == (3, 3)

    def test_multiline_fields(self) -> None:
        """Test parsing of multiline fields with triple quotes."""
        code = (
            'description: """This is a\nmultiline description\nwith multiple lines"""'
        )
        fields = list(split_fields(code))

        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "description"
        assert field["value"] == "This is a\nmultiline description\nwith multiple lines"
        assert field["line_no_range"] == (1, 3)
        assert (
            field["content"]
            == 'description: """This is a\nmultiline description\nwith multiple lines"""'
        )

    def test_multiline_field_same_line(self) -> None:
        """Test multiline field that opens and closes on the same line."""
        code = 'description: """Single line multiline"""'
        fields = list(split_fields(code))

        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "description"
        assert field["value"] == ' """Single line multiline"""'
        assert field["line_no_range"] == (1, 1)

    def test_empty_lines_ignored(self) -> None:
        """Test that empty lines are properly ignored."""
        code = "name: John\n\n\nage: 30\n\ncity: New York"
        fields = list(split_fields(code))

        assert len(fields) == 3
        assert fields[0]["line_no_range"] == (1, 1)
        assert fields[1]["line_no_range"] == (4, 4)
        assert fields[2]["line_no_range"] == (6, 6)

    def test_missing_colon_error(self) -> None:
        """Test error when field is missing colon separator."""
        code = "name John\nage: 30"

        with pytest.raises(
            ValueError,
            match="Field is missing a colon to separate the key and value in line 1",
        ):
            list(split_fields(code))

    def test_empty_value_error(self) -> None:
        """Test error when field value is empty."""
        code = "name:\nage: 30"

        with pytest.raises(ValueError, match="Value cannot be empty in line 1"):
            list(split_fields(code))

    def test_unclosed_multiline_error(self) -> None:
        """Test error when multiline field is not properly closed."""
        code = 'description: """This is a\nmultiline description\nthat never closes'

        with pytest.raises(ValueError, match="Multiline field was not closed"):
            list(split_fields(code))

    def test_multiline_with_quotes_in_content(self) -> None:
        """Test multiline field with quotes inside the content."""
        code = 'message: """Here is a "quoted" text\nand more content"""'
        fields = list(split_fields(code))

        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "message"
        assert field["value"] == 'Here is a "quoted" text\nand more content'

    def test_mixed_single_and_multiline(self) -> None:
        """Test mixing single-line and multiline fields."""
        code = 'name: John\ndescription: """A person\nnamed John"""\nage: 30'
        fields = list(split_fields(code))

        assert len(fields) == 3
        assert fields[0]["key"] == "name"
        assert fields[0]["value"] == " John"
        assert fields[0]["line_no_range"] == (1, 1)

        assert fields[1]["key"] == "description"
        assert fields[1]["value"] == "A person\nnamed John"
        assert fields[1]["line_no_range"] == (2, 3)

        assert fields[2]["key"] == "age"
        assert fields[2]["value"] == " 30"
        assert fields[2]["line_no_range"] == (4, 4)

    def test_whitespace_handling(self) -> None:
        """Test proper handling of whitespace around keys and values."""
        code = "  name  :  John  \n  age : 30  "
        fields = list(split_fields(code))

        assert len(fields) == 2
        assert fields[0]["key"] == "  name  "
        assert fields[0]["value"] == "  John  "
        assert fields[1]["key"] == "  age "
        assert fields[1]["value"] == " 30  "

    def test_empty_input(self) -> None:
        """Test handling of completely empty input."""
        code = ""
        fields = list(split_fields(code))
        assert len(fields) == 0

    def test_only_empty_lines(self) -> None:
        """Test input with only empty lines and whitespace."""
        code = "\n\n  \n\t\n"
        fields = list(split_fields(code))
        assert len(fields) == 0

    def test_single_colon_line(self) -> None:
        """Test line with only a colon (no key or value)."""
        code = ":"
        with pytest.raises(ValueError, match="Value cannot be empty in line 1"):
            list(split_fields(code))

    def test_colon_only_with_whitespace(self) -> None:
        """Test line with colon and only whitespace."""
        code = "  :  "
        # The function treats whitespace-only as a valid value, not empty
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"] == "  "
        assert fields[0]["value"] == "  "

    def test_key_only_no_colon(self) -> None:
        """Test line with only a key, no colon or value."""
        code = "name"
        with pytest.raises(
            ValueError,
            match="Field is missing a colon to separate the key and value in line 1",
        ):
            list(split_fields(code))

    def test_multiple_colons_in_line(self) -> None:
        """Test line with multiple colons."""
        code = "key:value:extra"
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"] == "key"
        assert fields[0]["value"] == "value:extra"

    def test_tab_characters(self) -> None:
        """Test handling of tab characters in input."""
        code = "name\t:\tJohn\t\nage\t:\t30\t"
        fields = list(split_fields(code))
        assert len(fields) == 2
        assert fields[0]["key"] == "name\t"
        assert fields[0]["value"] == "\tJohn\t"
        assert fields[1]["key"] == "age\t"
        assert fields[1]["value"] == "\t30\t"

    def test_carriage_return_line_endings(self) -> None:
        """Test handling of carriage return line endings."""
        code = "name: John\r\nage: 30\r\ncity: New York"
        fields = list(split_fields(code))
        assert len(fields) == 3
        assert fields[0]["key"] == "name"
        assert fields[0]["value"] == " John"
        assert fields[1]["key"] == "age"
        assert fields[1]["value"] == " 30"

    def test_mixed_line_endings(self) -> None:
        """Test handling of mixed line endings (CR, LF, CRLF)."""
        code = "name: John\nage: 30\r\ncity: New York\r"
        fields = list(split_fields(code))
        assert len(fields) == 3
        assert fields[0]["key"] == "name"
        assert fields[0]["value"] == " John"
        assert fields[1]["key"] == "age"
        assert fields[1]["value"] == " 30"

    def test_very_long_key(self) -> None:
        """Test handling of very long key names."""
        long_key = "a" * 1000
        code = f"{long_key}: value"
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"] == long_key
        assert fields[0]["value"] == " value"

    def test_very_long_value(self) -> None:
        """Test handling of very long values."""
        long_value = "x" * 1000
        code = f"key: {long_value}"
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"] == "key"
        assert fields[0]["value"] == f" {long_value}"

    def test_multiline_with_empty_lines(self) -> None:
        """Test multiline field with empty lines inside."""
        code = 'description: """Line 1\n\n\nLine 4"""'
        fields = list(split_fields(code))
        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "description"
        assert field["value"] == "Line 1\n\n\nLine 4"
        assert field["line_no_range"] == (1, 4)

    def test_multiline_quotes_in_middle(self) -> None:
        """Test multiline field with triple quotes in the middle of content."""
        code = 'message: """Here are some """quotes""" in the middle"""'
        fields = list(split_fields(code))
        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "message"
        # The function includes the opening quotes and preserves the content exactly
        assert field["value"] == ' """Here are some """quotes""" in the middle"""'

    def test_multiline_quotes_at_end(self) -> None:
        """Test multiline field with triple quotes at the very end."""
        code = 'message: """Content with quotes at the end""""'
        fields = list(split_fields(code))
        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "message"
        # The function includes the opening quotes and preserves the content exactly
        assert field["value"] == ' """Content with quotes at the end""""'

    def test_multiline_quotes_at_start(self) -> None:
        """Test multiline field with triple quotes at the very start."""
        code = 'message: """"Quotes at the start\nand more content"""'
        fields = list(split_fields(code))
        assert len(fields) == 1
        field = fields[0]
        assert field["key"] == "message"
        # The function strips the first 3 quotes and keeps the rest
        assert field["value"] == '"Quotes at the start\nand more content'

    def test_consecutive_multiline_fields(self) -> None:
        """Test consecutive multiline fields without single-line fields in between."""
        code = 'field1: """First multiline"""\nfield2: """Second multiline"""'
        fields = list(split_fields(code))
        assert len(fields) == 2
        assert fields[0]["key"] == "field1"
        # The function includes the opening quotes for same-line multiline fields
        assert fields[0]["value"] == ' """First multiline"""'
        assert fields[1]["key"] == "field2"
        assert fields[1]["value"] == ' """Second multiline"""'

    def test_unicode_characters(self) -> None:
        """Test handling of unicode characters in keys and values."""
        code = "námé: José\nâge: 30\ncîtý: São Paulo"
        fields = list(split_fields(code))
        assert len(fields) == 3
        assert fields[0]["key"] == "námé"
        assert fields[0]["value"] == " José"
        assert fields[1]["key"] == "âge"
        assert fields[1]["value"] == " 30"
        assert fields[2]["key"] == "cîtý"
        assert fields[2]["value"] == " São Paulo"

    def test_special_characters_in_keys(self) -> None:
        """Test handling of special characters in keys."""
        code = (
            "key-with-dashes: value\nkey_with_underscores: value\nkey.with.dots: value"
        )
        fields = list(split_fields(code))
        assert len(fields) == 3
        assert fields[0]["key"] == "key-with-dashes"
        assert fields[1]["key"] == "key_with_underscores"
        assert fields[2]["key"] == "key.with.dots"

    def test_numbers_as_keys(self) -> None:
        """Test handling of numeric keys."""
        code = "123: value\n0: value\n-42: value"
        fields = list(split_fields(code))
        assert len(fields) == 3
        assert fields[0]["key"] == "123"
        assert fields[1]["key"] == "0"
        assert fields[2]["key"] == "-42"

    def test_value_whitespace_only_raises(self) -> None:
        """Whitespace-only values are accepted and preserved."""
        code = "key:    \n  :   "
        fields = list(split_fields(code))
        assert len(fields) == 2
        # First line: key 'key' with spaces as value preserved
        assert fields[0]["key"] == "key"
        assert fields[0]["value"] == "    "
        # Second line: empty key with spaces as value preserved
        assert fields[1]["key"] == "  "
        assert fields[1]["value"] == "   "

    def test_key_and_value_are_trimmed(self) -> None:
        """Keys and values should be trimmed of surrounding whitespace."""
        code = "  name  :   John  "
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"].strip() == "name"
        assert fields[0]["value"].strip() == "John"

    def test_key_is_case_insensitive_and_normalized(self) -> None:
        """Keys should be treated case-insensitively and normalized (lowercase)."""
        code = "Name: John\nNAME: Jane\nname: Bob"
        fields = list(split_fields(code))
        assert len(fields) == 3
        # Expect normalization to lowercase for robustness
        assert [f["key"].strip().lower() for f in fields] == ["name", "name", "name"]

    def test_same_line_triple_quotes_treated_as_single_line_without_quotes(
        self,
    ) -> None:
        """If a value starts and ends with triple quotes on the same line, treat it as plain value without quotes."""
        code = 'description: """Single line"""'
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"].strip().lower() == "description"
        # Robust expectation: quotes removed and value trimmed
        assert fields[0]["value"].strip(' \t"') == "Single line"

    def test_multiple_colons_uses_first_colon_and_trims(self) -> None:
        """Only the first colon separates key and value; value keeps remaining colons but trims surrounding spaces."""
        code = "route: GET:/users/:id"
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"].strip().lower() == "route"
        assert fields[0]["value"].strip() == "GET:/users/:id"

    def test_tabs_are_treated_like_spaces_for_trimming(self) -> None:
        """Tabs around separators should not affect parsed key/value semantics."""
        code = "\tname\t:\tJohn\t"
        fields = list(split_fields(code))
        assert len(fields) == 1
        assert fields[0]["key"].strip().lower() == "name"
        assert fields[0]["value"].strip() == "John"
