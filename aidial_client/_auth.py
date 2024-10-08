from enum import Enum
from inspect import isawaitable
from typing import Awaitable, Callable, Dict, TypeVar, Union


class AuthType(Enum):
    API_KEY = "API_KEY"
    BEARER = "BEARER"


SyncAuthValue = Union[str, Callable[[], str]]
AsyncAuthValue = Union[SyncAuthValue, Callable[[], Awaitable[str]]]

AuthValueT = TypeVar(
    "AuthValueT",
    bound=Union[SyncAuthValue, AsyncAuthValue],
)


def get_auth_headers(
    *,
    auth_value: SyncAuthValue,
    auth_type: AuthType,
) -> Dict[str, str]:
    if auth_type == AuthType.API_KEY:
        if isinstance(auth_value, str):
            return {"api-key": auth_value}
        elif callable(auth_value):
            return {"api-key": auth_value()}
    elif auth_type == AuthType.BEARER:
        if isinstance(auth_value, str):
            return {"Authorization": f"Bearer {auth_value}"}
        elif callable(auth_value):
            return {"Authorization": f"Bearer {auth_value()}"}
    else:
        raise NotImplementedError("Unsupported auth")


async def get_async_auth_headers(
    auth_value: AsyncAuthValue,
    auth_type: AuthType,
) -> Dict[str, str]:
    if auth_type == AuthType.API_KEY:
        if isinstance(auth_value, str):
            return {"api-key": auth_value}
        elif callable(auth_value):
            result = auth_value()
            if isawaitable(result):
                return {"api-key": await result}
            return {"api-key": result}
    elif auth_type == AuthType.BEARER:
        if isinstance(auth_value, str):
            return {"Authorization": f"Bearer {auth_value}"}
        elif callable(auth_value):
            result = auth_value()
            if isawaitable(result):
                return {"Authorization": f"Bearer {await result}"}
            return {"Authorization": f"Bearer {result}"}
    else:
        raise NotImplementedError("Unsupported auth")
