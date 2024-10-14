import pytest

from aidial_client import AsyncDialClientPool, DialClientPool


def _test_getter() -> str:
    return "test-value"


async def _test_async_getter() -> str:
    return "test-value"


@pytest.mark.parametrize(
    "pool, api_key",
    [
        (DialClientPool(), "dummy"),
        (DialClientPool(), _test_getter),
        (AsyncDialClientPool(), "dummy"),
        (AsyncDialClientPool(), _test_getter),
        (AsyncDialClientPool(), _test_async_getter),
    ],
)
def test_pools(pool, api_key):
    client_1 = pool.create_client(base_url="http://dial.core", api_key=api_key)
    client_2 = pool.create_client(
        base_url="http://another_dial.core", api_key=api_key
    )
    assert client_1.base_url != client_2.base_url

    assert client_1.api_url == "http://dial.core/v1/"
    assert client_2.api_url == "http://another_dial.core/v1/"

    client_1_url = "http://dial.core/v1/bucket"
    client_2_url = "http://another_dial.core/v1/bucket"

    assert client_1.is_dial_url(client_1_url)
    assert not client_1.is_dial_url(client_2_url)

    assert client_2.is_dial_url(client_2_url)
    assert not client_2.is_dial_url(client_1_url)

    assert id(client_1) != id(client_2)
    assert id(client_1._http_client) != id(client_2._http_client)
    # Clients are different, but internal httpx client is the same
    assert id(client_1._http_client._internal_http_client) == id(
        client_2._http_client._internal_http_client
    )
