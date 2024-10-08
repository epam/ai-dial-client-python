from typing import Any, Dict, Union


def remove_none(input: Dict[str, Union[Any, None]]) -> Dict[str, Any]:
    return {key: value for key, value in input.items() if value is not None}
