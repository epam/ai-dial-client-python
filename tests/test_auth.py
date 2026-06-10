import asyncio

import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial


def _test_getter() -> str:
    return "test-value"


def _test_getter2() -> str:
    return "test-value2"


async def _test_async_getter() -> str:
    await asyncio.sleep(0)
    return "test-value"


async def _test_async_getter2() -> str:
    await asyncio.sleep(0)
    return "test-value2"


@pytest.mark.parametrize(
    "api_key_value, expected_headers",
    [
        ("dummy", {"api-key": "dummy"}),
        (
            _test_getter,
            {"api-key": "test-value"},
        ),
    ],
)
def test_api_key(api_key_value, expected_headers):
    client = Dial(api_key=api_key_value, base_url="http://dial.core")
    assert client.auth_headers() == expected_headers


@pytest.mark.parametrize(
    "api_key_value, bearer_token_value, expected_headers",
    [
        (
            "dummy",
            "dummy2",
            {"api-key": "dummy", "Authorization": "Bearer dummy2"},
        ),
        (
            _test_getter,
            _test_getter2,
            {"api-key": "test-value", "Authorization": "Bearer test-value2"},
        ),
    ],
)
def test_api_key_and_bearer_token(
    api_key_value, bearer_token_value, expected_headers
):
    client = Dial(
        api_key=api_key_value,
        bearer_token=bearer_token_value,
        base_url="http://dial.core",
    )
    assert client.auth_headers() == expected_headers


@pytest.mark.parametrize(
    "api_key_value, expected_headers",
    [
        ("dummy", {"api-key": "dummy"}),
        (
            _test_getter,
            {"api-key": "test-value"},
        ),
        (
            _test_async_getter,
            {"api-key": "test-value"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_api_key_async(api_key_value, expected_headers):
    client = AsyncDial(api_key=api_key_value, base_url="http://dial.core")
    assert await client.auth_headers() == expected_headers


@pytest.mark.parametrize(
    "api_key_value, bearer_token_value, expected_headers",
    [
        (
            "dummy",
            "dummy2",
            {"api-key": "dummy", "Authorization": "Bearer dummy2"},
        ),
        (
            _test_getter,
            _test_getter2,
            {"api-key": "test-value", "Authorization": "Bearer test-value2"},
        ),
        (
            _test_async_getter,
            _test_async_getter2,
            {"api-key": "test-value", "Authorization": "Bearer test-value2"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_api_key_and_bearer_token_async(
    api_key_value, bearer_token_value, expected_headers
):
    client = AsyncDial(
        api_key=api_key_value,
        bearer_token=bearer_token_value,
        base_url="http://dial.core",
    )
    assert await client.auth_headers() == expected_headers


@pytest.mark.parametrize(
    "bearer_token_value, expected_headers",
    [
        ("dummy-token", {"Authorization": "Bearer dummy-token"}),
        (
            _test_getter,
            {"Authorization": "Bearer test-value"},
        ),
    ],
)
def test_bearer_token(bearer_token_value, expected_headers):
    client = Dial(bearer_token=bearer_token_value, base_url="http://dial.core")
    assert client.auth_headers() == expected_headers


@pytest.mark.parametrize(
    "bearer_token_value, expected_headers",
    [
        ("dummy-token", {"Authorization": "Bearer dummy-token"}),
        (
            _test_getter,
            {"Authorization": "Bearer test-value"},
        ),
        (
            _test_async_getter,
            {"Authorization": "Bearer test-value"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_bearer_token_async(bearer_token_value, expected_headers):
    client = AsyncDial(
        bearer_token=bearer_token_value, base_url="http://dial.core"
    )
    assert await client.auth_headers() == expected_headers


def test_combined_auth():
    """Test that both api_key and bearer_token can be provided simultaneously."""
    client = Dial(
        api_key="my-api-key",
        bearer_token="my-bearer-token",  # noqa: S106
        base_url="http://dial.core",
    )
    headers = client.auth_headers()
    assert headers == {
        "api-key": "my-api-key",
        "Authorization": "Bearer my-bearer-token",
    }


@pytest.mark.asyncio
async def test_combined_auth_async():
    """Test that both api_key and bearer_token can be provided simultaneously in an async client."""
    client = AsyncDial(
        api_key="my-api-key",
        bearer_token="my-bearer-token",  # noqa: S106
        base_url="http://dial.core",
    )
    headers = await client.auth_headers()
    assert headers == {
        "api-key": "my-api-key",
        "Authorization": "Bearer my-bearer-token",
    }


def test_no_auth_raises_error():
    """Test that providing neither api_key nor bearer_token raises an error."""
    with pytest.raises(
        ValueError,
        match="At least one of api_key or bearer_token must be provided",
    ):
        Dial(base_url="http://dial.core")
