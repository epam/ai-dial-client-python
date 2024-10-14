from typing import Mapping

from typing_extensions import TypeGuard


def is_mapping(obj) -> TypeGuard[Mapping]:
    return isinstance(obj, Mapping)
