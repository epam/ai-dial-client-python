from collections.abc import Awaitable, Callable
from inspect import isawaitable
from typing import TypeVar, Union

SyncAuthValue = Union[str, Callable[[], str]]
AsyncAuthValue = Union[SyncAuthValue, Callable[[], Awaitable[str]]]

AuthValueT = TypeVar(
    "AuthValueT",
    bound=SyncAuthValue | AsyncAuthValue,
)


def get_auth_value(auth_value: SyncAuthValue) -> str:
    if isinstance(auth_value, str):
        return auth_value
    if callable(auth_value):
        return auth_value()
    from typing import TYPE_CHECKING, assert_never

    if TYPE_CHECKING:
        assert_never(auth_value)
    raise TypeError(
        f"auth_value must be a string or a callable returning a string, "
        f"got {type(auth_value).__name__}"
    )


async def aget_auth_value(auth_value: AsyncAuthValue) -> str:
    if isinstance(auth_value, str):
        return auth_value
    if callable(auth_value):
        result = auth_value()
        return await result if isawaitable(result) else result
    from typing import TYPE_CHECKING, assert_never

    if TYPE_CHECKING:
        assert_never(auth_value)
    raise TypeError(
        "auth_value must be a string or a callable, "
        f"got {type(auth_value).__name__}"
    )


def get_combined_auth_headers(
    *,
    api_key: SyncAuthValue | None = None,
    bearer_token: SyncAuthValue | None = None,
) -> dict[str, str]:
    headers: dict[str, str] = {}

    if api_key is not None:
        headers["api-key"] = get_auth_value(api_key)

    if bearer_token is not None:
        bearer_str = get_auth_value(bearer_token)
        headers["Authorization"] = f"Bearer {bearer_str}"

    return headers


async def aget_combined_auth_headers(
    *,
    api_key: AsyncAuthValue | None = None,
    bearer_token: AsyncAuthValue | None = None,
) -> dict[str, str]:
    """
    Get combined authentication headers from both api_key and
    bearer_token (async).
    """
    headers: dict[str, str] = {}

    if api_key is not None:
        processed_api_key = await aget_auth_value(api_key)
        headers["api-key"] = processed_api_key

    if bearer_token is not None:
        processed_bearer_token = await aget_auth_value(bearer_token)
        headers["Authorization"] = f"Bearer {processed_bearer_token}"

    return headers


def validate_auth(
    *,
    api_key: AsyncAuthValue | None = None,
    bearer_token: AsyncAuthValue | None = None,
) -> None:
    """Validate that at least one authentication method is provided."""
    if not api_key and not bearer_token:
        raise ValueError(
            "At least one of api_key or bearer_token must be provided"
        )
