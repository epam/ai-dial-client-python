from typing import Any, cast
from unittest.mock import AsyncMock

import httpx
import pytest

from aidial_client._client import AsyncDial
from aidial_client._exception import InvalidDialURLError
from tests.client_mock import MockStreamIterator


@pytest.mark.asyncio
async def test_stream_download_async_streams_and_closes_response():
    captured_requests: list[httpx.Request] = []
    captured_kwargs: list[dict[str, Any]] = []
    captured_responses: list[httpx.Response] = []
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._get_my_bucket = cast(Any, AsyncMock(return_value="test-bucket"))

    async def send_mock(
        request: httpx.Request, *, stream: bool = False, **kwargs: Any
    ) -> httpx.Response:
        captured_requests.append(request)
        captured_kwargs.append({"stream": stream, **kwargs})
        response = httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(mock_chunks=[b"hello ", b"world"]),
        )
        captured_responses.append(response)
        return response

    client._http_client._internal_http_client.send = cast(Any, send_mock)

    async with client.files.stream_download(
        url=await client.my_files_home() / "folder/file.txt"
    ) as response:
        assert response.filename == "file.txt"
        assert b"".join([chunk async for chunk in response]) == b"hello world"

    assert (
        captured_requests[0].url.path == "/v1/files/test-bucket/folder/file.txt"
    )
    assert captured_kwargs == [{"stream": True}]
    assert captured_responses[0].is_closed is True


@pytest.mark.asyncio
async def test_stream_download_async_rejects_directory_url():
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._get_my_bucket = cast(Any, AsyncMock(return_value="test-bucket"))
    send_mock = AsyncMock()
    client._http_client._internal_http_client.send = cast(Any, send_mock)

    with pytest.raises(
        InvalidDialURLError, match="URL points to a directory, not a file"
    ):
        async with client.files.stream_download(
            url="files/test-bucket/folder/"
        ):
            pass

    send_mock.assert_not_called()
