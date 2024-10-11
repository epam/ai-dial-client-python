"""
Just copy of alias generators from pydantic V2:
https://github.com/pydantic/pydantic/blob/c772b43edb952c5fe54bb28da5124b10d5470caf/pydantic/alias_generators.py

So we can use library  with pydantic < 2.0 version
"""

import re


def to_pascal(snake: str) -> str:
    """Convert a snake_case string to PascalCase.

    Args:
        snake: The string to convert.

    Returns:
        The PascalCase string.
    """
    camel = snake.title()
    return re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)


def to_camel(snake: str) -> str:
    """Convert a snake_case string to camelCase.

    Args:
        snake: The string to convert.

    Returns:
        The converted camelCase string.
    """
    # If the string is already in camelCase
    # and does not contain a digit followed
    # by a lowercase letter, return it as it is
    if re.match("^[a-z]+[A-Za-z0-9]*$", snake) and not re.search(
        r"\d[a-z]", snake
    ):
        return snake

    camel = to_pascal(snake)
    return re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), camel)
