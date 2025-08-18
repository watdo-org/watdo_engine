def apply_variables(code: str, variables: dict[str, str]) -> str:
    try:
        new_code = code.format(**variables)
    except KeyError as error:
        raise ValueError(f"Variable {error} is undefined")

    return new_code
