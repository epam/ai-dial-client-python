from typing import Any, cast
from unittest.mock import AsyncMock

import httpx
import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
    InvalidDialURLError,
    ResourceNotFoundError,
)
from tests.client_mock import MockStreamIterator, get_client_mock

SKILL_URL = "skills/test-bucket/writing/tone-of-voice"
ZIP_BYTES = b"PK\x03\x04fake-archive"


def _capturing_client(
    captured: list[httpx.Request],
    content: bytes,
    headers: dict[str, str] | None = None,
) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200,
            request=request,
            content=content,
            headers=headers or {},
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    return client


def test_download_whole_skill_as_zip():
    captured: list[httpx.Request] = []
    client = _capturing_client(
        captured,
        ZIP_BYTES,
        {"content-type": "application/zip", "etag": "aggregate-etag"},
    )

    response = client.skills.download(SKILL_URL)

    assert (
        captured[0].url.path == "/v2/skills/test-bucket/writing/tone-of-voice"
    )
    assert response.get_content() == ZIP_BYTES
    assert response.content_type == "application/zip"
    assert response.headers["etag"] == "aggregate-etag"
    # Core sends no Content-Disposition, so the archive is named after the skill.
    assert response.filename == "tone-of-voice.zip"


def test_reads_send_no_if_match():
    # DIAL Core ignores If-Match on both v2 reads: neither
    # ComplexResourceController.get nor .getFile calls ProxyUtil.etag, and
    # neither operation declares the header or a 412 response. Sending it
    # anyway would advertise a precondition the server does not enforce.
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, ZIP_BYTES)

    client.skills.download(SKILL_URL)
    client.skills.get_file(SKILL_URL, "SKILL.md")

    assert all("if-match" not in request.headers for request in captured)


def test_download_rejects_non_skill_url():
    client = _capturing_client([], ZIP_BYTES)

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        client.skills.download("files/test-bucket/folder/file.txt")


def test_get_file_returns_bytes():
    captured: list[httpx.Request] = []
    client = _capturing_client(
        captured,
        b"---\nname: tone\ndescription: d\n---\nbody",
        {"content-type": "text/markdown", "etag": "aggregate-etag"},
    )

    response = client.skills.get_file(SKILL_URL, "SKILL.md")

    assert captured[0].url.path == (
        "/v2/skills/test-bucket/writing/tone-of-voice/files/SKILL.md"
    )
    assert response.filename == "SKILL.md"
    assert response.get_content().startswith(b"---")


def test_get_file_percent_encodes_relative_path():
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"schema")

    response = client.skills.get_file(SKILL_URL, "references/api schema.md")

    assert captured[0].url.raw_path.decode() == (
        "/v2/skills/test-bucket/writing/tone-of-voice"
        "/files/references/api%20schema.md"
    )
    # The filename stays human-readable.
    assert response.filename == "api schema.md"


def test_get_file_accepts_already_encoded_path():
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"schema")

    client.skills.get_file(SKILL_URL, "references/api%20schema.md")

    assert captured[0].url.raw_path.decode() == (
        "/v2/skills/test-bucket/writing/tone-of-voice"
        "/files/references/api%20schema.md"
    )


def test_get_file_preserves_non_utf8_content():
    payload = b"\x89PNG\r\n\x1a\n\xff\xfe"
    client = _capturing_client([], payload, {"content-type": "image/png"})

    response = client.skills.get_file(SKILL_URL, "assets/logo.png")

    assert response.get_content() == payload


@pytest.mark.parametrize(
    "status_code, expected_exception",
    [
        (404, ResourceNotFoundError),
        (412, EtagMismatchError),
        (403, DialException),
    ],
)
def test_error_mapping(status_code, expected_exception):
    client = get_client_mock(
        status_code=status_code, json_mock={"error": {"message": "nope"}}
    )

    with pytest.raises(expected_exception) as exc_info:
        client.skills.get_file(SKILL_URL, "SKILL.md")

    if status_code == 403:
        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_async_stream_download_streams_and_closes():
    captured: list[httpx.Request] = []
    captured_kwargs: list[dict[str, Any]] = []
    responses: list[httpx.Response] = []
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._get_my_bucket = cast(Any, AsyncMock(return_value="test-bucket"))

    async def send_mock(
        request: httpx.Request, *, stream: bool = False, **kwargs: Any
    ) -> httpx.Response:
        captured.append(request)
        captured_kwargs.append({"stream": stream, **kwargs})
        response = httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(mock_chunks=[b"PK\x03\x04", b"rest"]),
        )
        responses.append(response)
        return response

    client._http_client._internal_http_client.send = cast(Any, send_mock)

    async with client.skills.stream_download(SKILL_URL) as response:
        assert response.filename == "tone-of-voice.zip"
        chunks = [chunk async for chunk in response]
        assert b"".join(chunks) == b"PK\x03\x04rest"

    assert (
        captured[0].url.path == "/v2/skills/test-bucket/writing/tone-of-voice"
    )
    assert captured_kwargs == [{"stream": True}]
    assert responses[0].is_closed is True


@pytest.mark.asyncio
async def test_async_stream_file_streams_and_closes():
    captured: list[httpx.Request] = []
    responses: list[httpx.Response] = []
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(mock_chunks=[b"# skill"]),
        )
        responses.append(response)
        return response

    client._http_client._internal_http_client.send = cast(Any, send_mock)

    async with client.skills.stream_file(SKILL_URL, "SKILL.md") as response:
        assert response.filename == "SKILL.md"
        assert b"".join([c async for c in response]) == b"# skill"

    assert captured[0].url.path == (
        "/v2/skills/test-bucket/writing/tone-of-voice/files/SKILL.md"
    )
    assert responses[0].is_closed is True


@pytest.mark.parametrize(
    "bad_path",
    [
        "../../../victimbucket9f2/their-skill/files/SKILL.md",
        "../SKILL.md",
        "refs/../../../other/x.md",
        "refs/./x.md",
        ".",
        "..",
        # Percent-encoded dot segments: _percent_encode_relative_url
        # unquotes before quoting, so these decode back to ".." and would
        # otherwise slip past a literal check.
        "%2e%2e/%2e%2e/%2e%2e/victimbucket9f2/s/files/SKILL.md",
        "%2E%2E/SKILL.md",
        "refs/%2e/x.md",
        ".%2e/SKILL.md",
    ],
)
def test_get_file_rejects_traversal_segments(bad_path):
    # file_path is appended to an already-validated api path and never goes
    # back through the url parser, so "." / ".." would shift the bucket
    # segment and retarget the request at another bucket.
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    with pytest.raises(InvalidDialURLError, match=r'"\." and "\.\."'):
        client.skills.get_file(SKILL_URL, bad_path)

    assert captured == []


@pytest.mark.parametrize(
    "bad_path",
    [
        "../../../victimbucket9f2/their-skill/files",
        "refs/../../..",
        "%2e%2e/%2e%2e/%2e%2e/victimbucket9f2/s/files",
    ],
)
def test_list_files_rejects_traversal_segments(bad_path):
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    with pytest.raises(InvalidDialURLError, match=r'"\." and "\.\."'):
        client.skills.list_files(SKILL_URL, path=bad_path)

    assert captured == []


@pytest.mark.parametrize(
    "bad_path, message",
    [
        ("", "must not be empty"),
        ("   ", "must not be empty"),
        ("/abs/path.md", "must be relative to the skill root"),
        ("refs/", "points to a directory, not a file"),
        ("a//b.md", "Empty path segment"),
    ],
)
def test_get_file_rejects_malformed_path(bad_path, message):
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    with pytest.raises(InvalidDialURLError, match=message):
        client.skills.get_file(SKILL_URL, bad_path)

    assert captured == []


@pytest.mark.asyncio
async def test_async_get_file_rejects_traversal():
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    with pytest.raises(InvalidDialURLError, match=r'"\." and "\.\."'):
        await client.skills.get_file(SKILL_URL, "../../../other/s/files/x.md")


@pytest.mark.parametrize(
    "bad_path",
    ["refs/a%2Fb.md", "a%2fb.md", "a%2f%2e%2e%2fb"],
)
def test_get_file_rejects_encoded_separator(bad_path):
    # An encoded separator would decode into a real one, splitting a segment
    # after validation and landing in the derived filename.
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    with pytest.raises(InvalidDialURLError, match="encoded path separator"):
        client.skills.get_file(SKILL_URL, bad_path)

    assert captured == []


def test_list_files_rejects_empty_path_like_get_file():
    # "" is validated the same way for both entry points; None means "unset".
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    with pytest.raises(InvalidDialURLError, match="path must not be empty"):
        client.skills.list_files(SKILL_URL, path="")

    assert captured == []


@pytest.mark.parametrize(
    "good_path, expected_raw, expected_filename",
    [
        ("SKILL.md", "SKILL.md", "SKILL.md"),
        ("refs/api schema.md", "refs/api%20schema.md", "api schema.md"),
        ("refs/api%20schema.md", "refs/api%20schema.md", "api schema.md"),
        # A dot inside a segment is not a dot segment.
        ("v1.2/notes.md", "v1.2/notes.md", "notes.md"),
    ],
)
def test_get_file_accepts_legitimate_paths(
    good_path, expected_raw, expected_filename
):
    captured: list[httpx.Request] = []
    client = _capturing_client(captured, b"x")

    response = client.skills.get_file(SKILL_URL, good_path)

    assert captured[0].url.raw_path.decode() == (
        f"/v2/skills/test-bucket/writing/tone-of-voice/files/{expected_raw}"
    )
    assert response.filename == expected_filename
