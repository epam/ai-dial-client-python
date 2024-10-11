from enum import Enum
from inspect import isawaitable
from typing import (
    Awaitable,
    Callable,
    Dict,
    Optional,
    Tuple,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import assert_never


class AuthType(Enum):
    API_KEY = "API_KEY"
    BEARER = "BEARER"


SyncAuthValue = Union[str, Callable[[], str]]
AsyncAuthValue = Union[SyncAuthValue, Callable[[], Awaitable[str]]]

AuthValueT = TypeVar(
    "AuthValueT",
    bound=Union[SyncAuthValue, AsyncAuthValue],
)


@overload
def get_auth_value(auth_value: SyncAuthValue) -> str: ...


@overload
def get_auth_value(
    auth_value: AsyncAuthValue,
) -> Union[str, Awaitable[str]]: ...


def get_auth_value(
    auth_value: Union[SyncAuthValue, AsyncAuthValue]
) -> Union[str, Awaitable[str]]:
    if isinstance(auth_value, str):
        return auth_value
    elif callable(auth_value):
        return auth_value()
    else:
        assert_never(auth_value)


async def aget_auth_value(auth_value: AsyncAuthValue) -> str:
    processed_auth_value = get_auth_value(auth_value)
    if isawaitable(processed_auth_value):
        return await processed_auth_value
    return processed_auth_value


def _get_auth_headers(auth_type: AuthType, auth_value: str) -> Dict[str, str]:
    if auth_type == AuthType.API_KEY:
        return {"api-key": auth_value}
    elif auth_type == AuthType.BEARER:
        return {"Authorization": f"Bearer {auth_value}"}
    else:
        assert_never(auth_type)


def get_auth_headers(
    *,
    auth_value: SyncAuthValue,
    auth_type: AuthType,
) -> Dict[str, str]:
    processed_auth_value = get_auth_value(auth_value)
    return _get_auth_headers(auth_type, processed_auth_value)


async def aget_auth_headers(
    auth_value: AsyncAuthValue,
    auth_type: AuthType,
) -> Dict[str, str]:
    processed_auth_value = await aget_auth_value(auth_value)
    return _get_auth_headers(auth_type, processed_auth_value)


def process_auth(
    *,
    api_key: Optional[AuthValueT] = None,
    bearer_token: Optional[AuthValueT] = None,
) -> Tuple[AuthType, AuthValueT]:
    if api_key and bearer_token:
        raise ValueError(
            "Either api_key or bearer_token must be provided, but not both"
        )
    elif api_key:
        return AuthType.API_KEY, api_key
    elif bearer_token:
        return AuthType.BEARER, bearer_token
    else:
        raise ValueError("Either api_key or bearer_token must be provided")
