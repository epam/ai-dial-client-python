from typing import Any, cast
from unittest.mock import AsyncMock

import httpx
import pytest

from aidial_client._client import AsyncDial
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
    ResourceNotFoundError,
)
from tests.client_mock import MockStreamIterator


def _make_client(status_code: int, body: bytes) -> AsyncDial:
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._get_my_bucket = cast(Any, AsyncMock(return_value="test-bucket"))

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        # A streamed response: the body isn't read until someone asks for it.
        return httpx.Response(
            status_code=status_code,
            request=request,
            stream=MockStreamIterator(mock_chunks=[body]),
        )

    client._http_client._internal_http_client.send = cast(Any, send_mock)
    return client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code, body, error_type",
    [
        (404, b"File not found", ResourceNotFoundError),
        (412, b"Precondition failed", EtagMismatchError),
    ],
)
async def test_stream_download_maps_storage_errors(
    status_code: int, body: bytes, error_type: type[DialException]
):
    client = _make_client(status_code, body)

    with pytest.raises(error_type) as exc_info:
        async with client.files.stream_download("files/test-bucket/a.txt"):
            pass

    assert exc_info.value.message == body.decode()


@pytest.mark.asyncio
async def test_stream_download_maps_other_errors_with_core_message():
    client = _make_client(
        403, b'{"error": {"message": "Access denied", "code": "403"}}'
    )

    with pytest.raises(DialException) as exc_info:
        async with client.files.stream_download("files/test-bucket/a.txt"):
            pass

    assert exc_info.value.status_code == 403
    assert exc_info.value.message == "Access denied"
