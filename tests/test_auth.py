import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial


def _test_getter() -> str:
    return "test-value"


async def _test_async_getter() -> str:
    return "test-value"


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
    "bearer_token_value, expected_headers",
    [
        ("dummy-token", {"Authorization": "Bearer dummy-token"}),
        (
            _test_getter,
            {"Authorization": "Bearer test-value"},
        ),
    ],
)
@pytest.mark.asyncio
async def test_bearer_token(bearer_token_value, expected_headers):
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
