import json

import httpx
import pytest

from aidial_client import AsyncDial, Dial
from aidial_client._exception import DialException

BASE_URL = "http://dial.core"
GRANT_PATH = "/v1/ops/resource/per-request-permissions/grant"


def _make_sync_client_capturing() -> tuple[Dial, list[httpx.Request]]:
    """Returns a Dial client whose mock captures every sent request."""
    captured: list[httpx.Request] = []
    client = Dial(api_key="dummy", base_url=BASE_URL)

    def send_mock(request: httpx.Request, **kwargs):
        captured.append(request)
        return httpx.Response(200, request=request, json={})

    client._http_client._internal_http_client.send = send_mock
    return client, captured


def _make_async_client_capturing() -> tuple[AsyncDial, list[httpx.Request]]:
    """Returns an AsyncDial client whose mock captures every sent request."""
    captured: list[httpx.Request] = []
    client = AsyncDial(api_key="dummy", base_url=BASE_URL)

    async def send_mock(request: httpx.Request, **kwargs):
        captured.append(request)
        return httpx.Response(200, request=request, json={})

    client._http_client._internal_http_client.send = send_mock
    return client, captured


# ---------------------------------------------------------------------------
# Happy path — return value
# ---------------------------------------------------------------------------


def test_grant_returns_none():
    client, _ = _make_sync_client_capturing()
    result = client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
    )
    assert result is None


@pytest.mark.asyncio
async def test_async_grant_returns_none():
    client, _ = _make_async_client_capturing()
    result = await client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
    )
    assert result is None


# ---------------------------------------------------------------------------
# Request body verification
# ---------------------------------------------------------------------------


def test_grant_request_body_single_resource():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
        permissions=["READ"],
    )
    assert len(captured) == 1
    body = json.loads(captured[0].content)
    assert body == {
        "resources": [{"url": "files/bucket/img.png", "permissions": ["READ"]}],
        "receiver": "my-app",
    }


@pytest.mark.asyncio
async def test_async_grant_request_body_single_resource():
    client, captured = _make_async_client_capturing()
    await client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
        permissions=["READ"],
    )
    assert len(captured) == 1
    body = json.loads(captured[0].content)
    assert body == {
        "resources": [{"url": "files/bucket/img.png", "permissions": ["READ"]}],
        "receiver": "my-app",
    }


def test_grant_request_body_multiple_resources():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/a.png", "files/bucket/b.png"],
        receiver="deployment-x",
        permissions=["READ"],
    )
    body = json.loads(captured[0].content)
    assert body["receiver"] == "deployment-x"
    assert len(body["resources"]) == 2
    assert body["resources"][0] == {
        "url": "files/bucket/a.png",
        "permissions": ["READ"],
    }
    assert body["resources"][1] == {
        "url": "files/bucket/b.png",
        "permissions": ["READ"],
    }


def test_grant_request_body_write_permission():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
        permissions=["WRITE"],
    )
    body = json.loads(captured[0].content)
    assert body["resources"][0]["permissions"] == ["WRITE"]


def test_grant_request_url():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
    )
    assert captured[0].url.path == GRANT_PATH


def test_grant_request_method():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
    )
    assert captured[0].method == "POST"


# ---------------------------------------------------------------------------
# Default permissions
# ---------------------------------------------------------------------------


def test_grant_default_permissions_are_read():
    client, captured = _make_sync_client_capturing()
    client.resource_permissions.grant(
        resources=["files/bucket/img.png"],
        receiver="my-app",
    )
    body = json.loads(captured[0].content)
    assert body["resources"][0]["permissions"] == ["READ"]


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_grant_http_error():
    client = Dial(api_key="dummy", base_url=BASE_URL)

    def send_mock(request: httpx.Request, **kwargs):
        return httpx.Response(
            403,
            request=request,
            json={
                "error": {
                    "message": "Forbidden: per-request key required",
                    "type": "auth_error",
                }
            },
        )

    client._http_client._internal_http_client.send = send_mock
    with pytest.raises(DialException):
        client.resource_permissions.grant(
            resources=["files/bucket/img.png"],
            receiver="my-app",
        )


@pytest.mark.asyncio
async def test_async_grant_http_error():
    client = AsyncDial(api_key="dummy", base_url=BASE_URL)

    async def send_mock(request: httpx.Request, **kwargs):
        return httpx.Response(
            403,
            request=request,
            json={
                "error": {
                    "message": "Forbidden: per-request key required",
                    "type": "auth_error",
                }
            },
        )

    client._http_client._internal_http_client.send = send_mock
    with pytest.raises(DialException):
        await client.resource_permissions.grant(
            resources=["files/bucket/img.png"],
            receiver="my-app",
        )
