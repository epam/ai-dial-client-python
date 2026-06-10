import httpx
import pytest

from aidial_client import AsyncDial, Dial
from aidial_client._exception import DialException
from tests.client_mock import get_async_client_mock, get_client_mock

BASE_URL = "http://dial.core"

USER_INFO_MOCK = {
    "sub": "user-123",
    "email": "user@example.com",
    "name": "Test User",
}


def test_get_user_info():
    client = get_client_mock(status_code=200, json_mock=USER_INFO_MOCK)
    result = client.user.info()
    assert result == USER_INFO_MOCK


@pytest.mark.asyncio
async def test_async_get_user_info():
    client = get_async_client_mock(status_code=200, json_mock=USER_INFO_MOCK)
    result = await client.user.info()
    assert result == USER_INFO_MOCK


def test_get_user_info_request_method_and_url():
    captured: list[httpx.Request] = []
    client = Dial(api_key="dummy", base_url=BASE_URL)

    def send_mock(request: httpx.Request, **kwargs):
        captured.append(request)
        return httpx.Response(200, request=request, json=USER_INFO_MOCK)

    client._http_client._internal_http_client.send = send_mock
    client.user.info()

    assert len(captured) == 1
    assert captured[0].method == "GET"
    assert captured[0].url.path == "/v1/user/info"


@pytest.mark.asyncio
async def test_async_get_user_info_request_method_and_url():
    captured: list[httpx.Request] = []
    client = AsyncDial(api_key="dummy", base_url=BASE_URL)

    async def send_mock(request: httpx.Request, **kwargs):
        captured.append(request)
        return httpx.Response(200, request=request, json=USER_INFO_MOCK)

    client._http_client._internal_http_client.send = send_mock
    await client.user.info()

    assert len(captured) == 1
    assert captured[0].method == "GET"
    assert captured[0].url.path == "/v1/user/info"


def test_get_user_info_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        client.user.info()


@pytest.mark.asyncio
async def test_async_get_user_info_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        await client.user.info()
