from typing import Any


def remove_none(input: dict[str, Any | None]) -> dict[str, Any]:
    return {key: value for key, value in input.items() if value is not None}
