from unittest.mock import patch

import pytest

from aidial_client import AsyncDialClientPool, Dial, DialClientPool
from aidial_client._client import AsyncDial


def test_dial_close():
    client = Dial(api_key="dummy", base_url="http://dial.core")

    with patch.object(
        client._http_client.internal_http_client, "close"
    ) as close_mock:
        client.close()

    close_mock.assert_called_once()


def test_dial_context_manager():
    client = Dial(api_key="dummy", base_url="http://dial.core")

    with patch.object(
        client._http_client.internal_http_client, "close"
    ) as close_mock:
        with client as managed_client:
            assert managed_client is client

    close_mock.assert_called_once()


@pytest.mark.asyncio
async def test_async_dial_aclose():
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    with patch.object(
        client._http_client.internal_http_client, "aclose"
    ) as aclose_mock:
        await client.aclose()

    aclose_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_dial_context_manager():
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    with patch.object(
        client._http_client.internal_http_client, "aclose"
    ) as aclose_mock:
        async with client as managed_client:
            assert managed_client is client

    aclose_mock.assert_awaited_once()


def test_dial_client_pool_close():
    pool = DialClientPool()

    with patch.object(pool._internal_http_client, "close") as close_mock:
        pool.close()

    close_mock.assert_called_once()


def test_dial_client_pool_context_manager():
    pool = DialClientPool()

    with patch.object(pool._internal_http_client, "close") as close_mock:
        with pool as managed_pool:
            assert managed_pool is pool

    close_mock.assert_called_once()


@pytest.mark.asyncio
async def test_async_dial_client_pool_aclose():
    pool = AsyncDialClientPool()

    with patch.object(pool._internal_http_client, "aclose") as aclose_mock:
        await pool.aclose()

    aclose_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_dial_client_pool_context_manager():
    pool = AsyncDialClientPool()

    with patch.object(pool._internal_http_client, "aclose") as aclose_mock:
        async with pool as managed_pool:
            assert managed_pool is pool

    aclose_mock.assert_awaited_once()
