import pytest
from src.variables import apply_variables


class TestApplyVariables:
    def test_apply_variables_basic(self) -> None:
        code = "Title: {title}"
        variables = {"title": "Test title"}
        new_code = apply_variables(code, variables)

        assert new_code == "Title: Test title"

    def test_apply_variables_syntax_error(self) -> None:
        code = "Title: {title"
        variables = {"title": "Test title"}

        with pytest.raises(ValueError):
            apply_variables(code, variables)

    def test_apply_variables_undefined_variable(self) -> None:
        code = "Title: {title}"

        with pytest.raises(ValueError) as exc_info:
            apply_variables(code, {})

        assert "Variable 'title' is undefined" in str(exc_info.value)
