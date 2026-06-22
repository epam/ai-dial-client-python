from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial
from aidial_client.types.metadata import FileMetadata
from tests.client_mock import get_async_client_mock, get_client_mock

METADATA_RESPONSE_MOCK = {
    "name": "folder2",
    "parentPath": "folder1",
    "bucket": "test-bucket",
    "url": "files/test/folder1/folder2/",
    "nodeType": "FOLDER",
    "resourceType": "FILE",
    "items": [
        {
            "name": "file.png",
            "parentPath": "folder1/folder2",
            "bucket": "test",
            "url": "files/test/folder1/folder2/file.png",
            "nodeType": "ITEM",
            "resourceType": "FILE",
            "contentLength": 128630,
            "contentType": "image/png",
        }
    ],
    "nextToken": "next-page-token",
}


def _make_capturing_client(captured: list[httpx.Request]) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=METADATA_RESPONSE_MOCK
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = Mock(return_value="test-bucket")
    return client


def _make_async_capturing_client(
    captured: list[httpx.Request],
) -> AsyncDial:
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=METADATA_RESPONSE_MOCK
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = AsyncMock(return_value="test-bucket")
    return client


def test_get_metadata():
    client = get_client_mock(status_code=200, json_mock=METADATA_RESPONSE_MOCK)
    client._get_my_bucket = Mock(return_value="test-bucket")

    valid_response = client.files.get_metadata(
        url="files/test-bucket/folder1/folder2/"
    )
    valid_response_with_default_bucket = client.files.get_metadata(
        url=client.my_files_home() / "folder1/folder2/"
    )

    for r in [valid_response, valid_response_with_default_bucket]:
        assert isinstance(r, FileMetadata)
        assert r.node_type == "FOLDER"
        assert r.bucket == "test-bucket"
        assert r.items and len(r.items) == 1
        assert r.items[0].node_type == "ITEM"
        assert r.next_token == "next-page-token"


def test_get_metadata_sends_pagination_params():
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    result = client.files.get_metadata(
        url=client.my_files_home() / "folder1/folder2/",
        limit=100,
        token="page-token",
    )

    assert isinstance(result, FileMetadata)
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "GET"
    assert request.url.path == "/v1/metadata/files/test-bucket/folder1/folder2"
    assert request.url.params["limit"] == "100"
    assert request.url.params["token"] == "page-token"


@pytest.mark.asyncio
async def test_get_metadata_async():
    client = get_async_client_mock(
        status_code=200, json_mock=METADATA_RESPONSE_MOCK
    )
    client._get_my_bucket = AsyncMock(return_value="test-bucket")

    valid_response = await client.files.get_metadata(
        url="files/test-bucket/folder1/folder2/"
    )
    valid_response_with_default_bucket = await client.files.get_metadata(
        url=await client.my_files_home() / "folder1/folder2/"
    )

    for r in [valid_response, valid_response_with_default_bucket]:
        assert isinstance(r, FileMetadata)
        assert r.node_type == "FOLDER"
        assert r.bucket == "test-bucket"
        assert r.items and len(r.items) == 1
        assert r.items[0].node_type == "ITEM"
        assert r.next_token == "next-page-token"


@pytest.mark.asyncio
async def test_get_metadata_async_sends_pagination_params():
    captured: list[httpx.Request] = []
    client = _make_async_capturing_client(captured)

    result = await client.files.get_metadata(
        url=await client.my_files_home() / "folder1/folder2/",
        limit=100,
        token="page-token",
    )

    assert isinstance(result, FileMetadata)
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "GET"
    assert request.url.path == "/v1/metadata/files/test-bucket/folder1/folder2"
    assert request.url.params["limit"] == "100"
    assert request.url.params["token"] == "page-token"
