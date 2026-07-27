import json
from typing import Any
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial
from aidial_client._exception import InvalidDialURLError


def _make_capturing_client(captured: list[httpx.Request]) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(status_code=200, request=request, json={})
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
        response = httpx.Response(status_code=200, request=request, json={})
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = AsyncMock(return_value="test-bucket")
    return client


def _body(request: httpx.Request) -> dict[str, Any]:
    return json.loads(request.content.decode())


parametrize_method_and_endpoint = pytest.mark.parametrize(
    "method, endpoint", [("move_to", "move"), ("copy_to", "copy")]
)
parametrize_method = pytest.mark.parametrize("method", ["move_to", "copy_to"])


@parametrize_method_and_endpoint
def test_move_copy_returns_none_and_sends_expected_body(
    method: str, endpoint: str
):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    result = getattr(client.files, method)(
        source="files/test-bucket/draft/file.txt",
        destination="files/test-bucket/final/file.txt",
    )

    assert result is None
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "POST"
    assert request.url.path == f"/v1/ops/resource/{endpoint}"
    assert _body(request) == {
        "sourceUrl": "files/test-bucket/draft/file.txt",
        "destinationUrl": "files/test-bucket/final/file.txt",
        "overwrite": False,
    }


@parametrize_method
def test_overwrite_round_trips(method: str):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    getattr(client.files, method)(
        source="files/test-bucket/a.txt",
        destination="files/test-bucket/b.txt",
        overwrite=True,
    )

    assert _body(captured[0])["overwrite"] is True


@parametrize_method
def test_accepts_pureposixpath_and_absolute_urls(method: str):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    getattr(client.files, method)(
        source=client.my_files_home() / "draft/file.txt",
        destination="http://dial.core/v1/files/test-bucket/final/file.txt",
    )

    body = _body(captured[0])
    assert body["sourceUrl"] == "files/test-bucket/draft/file.txt"
    assert body["destinationUrl"] == "files/test-bucket/final/file.txt"


# Every reserved character must reach DIAL Core percent-encoded, otherwise
# `new URI(...)` on the server throws and it answers 500. `#` and `?` also must
# survive (a naive urlparse would drop them as fragment/query).
RESERVED_CASES = [
    ("my file.txt", "my%20file.txt"),
    ("50% off.txt", "50%25%20off.txt"),
    ("a#b.txt", "a%23b.txt"),
    ("a?b.txt", "a%3Fb.txt"),
    ("a&b.txt", "a%26b.txt"),
    ("tag[1].txt", "tag%5B1%5D.txt"),
    ("naïve.txt", "na%C3%AFve.txt"),
]
parametrize_reserved = pytest.mark.parametrize("raw, encoded", RESERVED_CASES)


@parametrize_method
@parametrize_reserved
def test_encodes_reserved_characters_in_body(
    method: str, raw: str, encoded: str
):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    getattr(client.files, method)(
        source=f"files/test-bucket/{raw}",
        destination="files/test-bucket/dst.txt",
    )

    assert _body(captured[0])["sourceUrl"] == f"files/test-bucket/{encoded}"


@parametrize_method
@parametrize_reserved
@pytest.mark.asyncio
async def test_async_encodes_reserved_characters_in_body(
    method: str, raw: str, encoded: str
):
    captured: list[httpx.Request] = []
    client = _make_async_capturing_client(captured)

    await getattr(client.files, method)(
        source=f"files/test-bucket/{raw}",
        destination="files/test-bucket/dst.txt",
    )

    assert _body(captured[0])["sourceUrl"] == f"files/test-bucket/{encoded}"


@parametrize_method
def test_already_encoded_input_is_not_double_encoded(method: str):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    # A url as returned by the API (percent-encoded) must round-trip unchanged.
    getattr(client.files, method)(
        source="files/test-bucket/my%20file.txt",
        destination="files/test-bucket/50%25%20off.txt",
    )

    body = _body(captured[0])
    assert body["sourceUrl"] == "files/test-bucket/my%20file.txt"
    assert body["destinationUrl"] == "files/test-bucket/50%25%20off.txt"


@parametrize_method
@pytest.mark.parametrize(
    "bad_arg",
    ["source", "destination"],
)
def test_rejects_non_files_urls(method: str, bad_arg: str):
    captured: list[httpx.Request] = []
    client = _make_capturing_client(captured)

    kwargs = {
        "source": "files/test-bucket/a.txt",
        "destination": "files/test-bucket/b.txt",
    }
    kwargs[bad_arg] = "prompts/test-bucket/a.txt"

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        getattr(client.files, method)(**kwargs)

    assert captured == []


@parametrize_method_and_endpoint
@pytest.mark.asyncio
async def test_move_copy_async_returns_none_and_sends_expected_body(
    method: str, endpoint: str
):
    captured: list[httpx.Request] = []
    client = _make_async_capturing_client(captured)

    result = await getattr(client.files, method)(
        source="files/test-bucket/draft/file.txt",
        destination=await client.my_files_home() / "final/file.txt",
        overwrite=True,
    )

    assert result is None
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "POST"
    assert request.url.path == f"/v1/ops/resource/{endpoint}"
    assert _body(request) == {
        "sourceUrl": "files/test-bucket/draft/file.txt",
        "destinationUrl": "files/test-bucket/final/file.txt",
        "overwrite": True,
    }


@parametrize_method
@pytest.mark.asyncio
async def test_async_rejects_non_files_urls(method: str):
    captured: list[httpx.Request] = []
    client = _make_async_capturing_client(captured)

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        await getattr(client.files, method)(
            source="conversations/test-bucket/c1",
            destination="files/test-bucket/b.txt",
        )

    assert captured == []
