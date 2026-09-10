from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial
from aidial_client._exception import InvalidDialURLError

SKILLS_LISTING_MOCK = {
    "name": "writing",
    "parentPath": None,
    "bucket": "test-bucket",
    "url": "skills/test-bucket/writing/",
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
    "items": [
        {
            "name": "tone-of-voice",
            "parentPath": "writing",
            "bucket": "test-bucket",
            "url": "skills/test-bucket/writing/tone-of-voice",
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            "createdAt": 1700000000000,
            "updatedAt": 1700000001000,
            "author": "someone",
        },
        {
            "name": "drafts",
            "parentPath": "writing",
            "bucket": "test-bucket",
            "url": "skills/test-bucket/writing/drafts/",
            "nodeType": "FOLDER",
            "resourceType": "SKILL",
        },
    ],
    "nextToken": "next-page-token",
}

SKILL_FILES_MOCK = {
    "name": "files",
    "parentPath": "tone-of-voice",
    "bucket": "test-bucket",
    "url": "skills/test-bucket/tone-of-voice/files/",
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
    "items": [
        {
            "name": "SKILL.md",
            "parentPath": "tone-of-voice/files",
            "bucket": "test-bucket",
            "url": "skills/test-bucket/tone-of-voice/files/SKILL.md",
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            # Observed responses carry no etag on these entries at all;
            # this pins that one is parsed when a deployment does send it.
            "etag": "abc123",
            "updatedAt": 1700000001000,
        },
        {
            "name": "references",
            "parentPath": "tone-of-voice/files",
            "bucket": "test-bucket",
            # A subfolder, as a non-recursive listing reports one.
            "url": "skills/test-bucket/tone-of-voice/files/references/",
            "nodeType": "FOLDER",
            "resourceType": "SKILL",
        },
    ],
    "nextToken": None,
}


def _sync_client(captured: list[httpx.Request], payload: dict) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=payload
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = Mock(return_value="test-bucket")
    return client


def _async_client(captured: list[httpx.Request], payload: dict) -> AsyncDial:
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=payload
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = cast(Any, send_mock)
    client._get_my_bucket = cast(Any, AsyncMock(return_value="test-bucket"))
    return client


def test_get_metadata_lists_bucket_root():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILLS_LISTING_MOCK)

    result = client.skills.list()

    assert captured[0].url.path == "/v2/metadata/skills/test-bucket/"
    assert result.resource_type == "SKILL"
    assert result.next_token == "next-page-token"  # noqa: S105

    items = result.items or []
    assert [item.node_type for item in items] == ["ITEM", "FOLDER"]
    # A skill node is an ITEM; Core omits the aggregate etag from the listing.
    assert items[0].name == "tone-of-voice"
    assert items[0].etag is None
    assert items[0].author == "someone"


def test_get_metadata_passes_listing_params():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILLS_LISTING_MOCK)

    (client.skills / "writing").list(
        limit=1000,
        token="page-2",  # noqa: S106
        recursive=True,
    )

    request = captured[0]
    assert request.url.path == "/v2/metadata/skills/test-bucket/writing/"
    assert dict(request.url.params) == {
        "limit": "1000",
        "token": "page-2",  # noqa: S105
        "recursive": "true",
    }


def test_get_metadata_omits_unset_params():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILLS_LISTING_MOCK)

    (client.skills / "writing").list()

    assert dict(captured[0].url.params) == {}


def test_list_files_defaults_to_skill_root():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILL_FILES_MOCK)

    result = client.skills(url="skills/test-bucket/tone-of-voice").files.list(
        recursive=True, limit=1000
    )

    request = captured[0]
    assert (
        request.url.path
        == "/v2/metadata/skills/test-bucket/tone-of-voice/files"
    )
    assert dict(request.url.params) == {"limit": "1000", "recursive": "true"}

    items = result.items or []
    assert items[0].etag == "abc123"
    assert result.next_token is None

    # A subfolder is a FOLDER and carries a trailing "/" on its url.
    assert [item.node_type for item in items] == ["ITEM", "FOLDER"]
    assert [item.url.endswith("/") for item in items] == [False, True]


def test_list_files_scopes_to_subfolder():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILL_FILES_MOCK)

    client.skills(url="skills/test-bucket/tone-of-voice").files(
        path="references/api schema"
    ).list()

    assert captured[0].url.raw_path.decode() == (
        "/v2/metadata/skills/test-bucket/tone-of-voice"
        "/files/references/api%20schema"
    )


def test_list_files_pagination_loop_terminates():
    pages = [
        {**SKILL_FILES_MOCK, "nextToken": "page-2"},
        {**SKILL_FILES_MOCK, "nextToken": None},
    ]
    captured: list[httpx.Request] = []
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        response = httpx.Response(
            status_code=200,
            request=request,
            json=pages[len(captured)],
        )
        captured.append(request)
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock

    files = client.skills(url="skills/test-bucket/tone-of-voice").files

    token = None
    seen = 0
    while True:
        page = files.list(token=token)
        seen += len(page.items or [])
        token = page.next_token
        if token is None:
            break

    assert len(captured) == 2
    assert seen == 4
    assert dict(captured[1].url.params) == {"token": "page-2"}


def test_get_metadata_rejects_non_skill_url():
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILLS_LISTING_MOCK)

    # Rejected while the reference is built, so nothing reaches the wire.
    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        client.skills(url="files/test-bucket/folder")

    assert captured == []


def test_list_files_rejects_bucket_root():
    # A bucket has no files of its own - only skills do. The reference is
    # legal; the terminal call is what has too little path for its route.
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILL_FILES_MOCK)

    with pytest.raises(InvalidDialURLError, match="points at the bucket root"):
        client.skills(url="skills/test-bucket").files.list()

    assert captured == []


@pytest.mark.asyncio
async def test_async_get_metadata_and_list_files():
    captured: list[httpx.Request] = []
    client = _async_client(captured, SKILLS_LISTING_MOCK)

    result = await client.skills.list()
    assert captured[0].url.path == "/v2/metadata/skills/test-bucket/"
    assert (result.items or [])[0].name == "tone-of-voice"

    await client.skills(url="skills/test-bucket/tone-of-voice").files.list(
        recursive=True
    )
    assert (
        captured[1].url.path
        == "/v2/metadata/skills/test-bucket/tone-of-voice/files"
    )


def test_rejects_folder_path_with_trailing_slash():
    # A reference carries no trailing slash: list() vs read() is what decides
    # whether it names a folder or a file. The old list_files(path="refs/")
    # accepted this and dropped the slash silently.
    captured: list[httpx.Request] = []
    client = _sync_client(captured, SKILL_FILES_MOCK)

    skill = client.skills(url="skills/test-bucket/tone-of-voice")
    with pytest.raises(InvalidDialURLError, match="must not end with"):
        skill.files(path="references/")

    assert captured == []
