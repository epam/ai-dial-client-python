from collections.abc import Mapping
from typing import TypeGuard


def is_mapping(obj) -> TypeGuard[Mapping]:
    return isinstance(obj, Mapping)
