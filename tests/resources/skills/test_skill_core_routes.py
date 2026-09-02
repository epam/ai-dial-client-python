"""
Pin the URLs the skills resource builds against DIAL Core's own route
regexes.

The rest of the skills tests assert URL strings, which cannot catch a URL
that is well-formed but unroutable - a bucket-root listing without its
trailing slash matched every string assertion while Core would have answered
404. These patterns are copied verbatim from ai-dial-core's
``server/.../data/RouteTemplate.java``; keep them in sync when Core changes
them.

The bucket here is alphanumeric on purpose: Core's ``[a-zA-Z0-9]+`` bucket
group rejects the hyphenated names used elsewhere in these tests, so a
hyphenated fixture would fail to match for the wrong reason.
"""

import re
from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

import httpx
import pytest

from aidial_client import Dial

COMPLEX_RESOURCE = re.compile(
    r"^/v2/skills/(?P<bucket>[a-zA-Z0-9]+)"
    r"/(?P<path>[^/](?:[^/]|/(?=[^/])(?!files/))*)$"
)
COMPLEX_RESOURCE_FILE = re.compile(
    r"^/v2/skills/(?P<bucket>[a-zA-Z0-9]+)"
    r"/(?P<path>.+?)/files/(?P<filePath>.+)$"
)
COMPLEX_RESOURCE_FILE_METADATA = re.compile(
    r"^/v2/metadata/skills/(?P<bucket>[a-zA-Z0-9]+)"
    r"/(?P<path>.+?)/files(?:/(?P<filePath>.*))?$"
)
COMPLEX_RESOURCE_METADATA = re.compile(
    r"^/v2/metadata/skills/(?P<bucket>[a-zA-Z0-9]+)/(?P<path>.*)$"
)

BUCKET = "mybucket7a1"
SKILL = f"skills/{BUCKET}/writing/toneofvoice"


# Parses as both SkillMetadata and SkillFileMetadata; the binary reads cast
# to httpx.Response and ignore it. Only the request URL matters here.
EMPTY_LISTING = {
    "bucket": BUCKET,
    "url": f"skills/{BUCKET}/",
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
}


def _client(captured: list[httpx.Request]) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=EMPTY_LISTING
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = Mock(return_value=BUCKET)
    return client


def _route(
    call: Callable[[Dial], object],
) -> tuple[str, dict[str, str | None]]:
    captured: list[httpx.Request] = []
    call(_client(captured))
    path = captured[0].url.raw_path.decode()

    # Core checks the file routes before the whole-resource ones, so a path
    # carrying a "/files/" segment must be reported as the file route.
    for name, pattern in (
        ("COMPLEX_RESOURCE_FILE_METADATA", COMPLEX_RESOURCE_FILE_METADATA),
        ("COMPLEX_RESOURCE_METADATA", COMPLEX_RESOURCE_METADATA),
        ("COMPLEX_RESOURCE_FILE", COMPLEX_RESOURCE_FILE),
        ("COMPLEX_RESOURCE", COMPLEX_RESOURCE),
    ):
        match = pattern.match(path)
        if match:
            return name, match.groupdict()
    pytest.fail(f"{path} matches no /v2/skills route in DIAL Core")


def test_bucket_root_listing_is_routable():
    route, groups = _route(
        lambda client: client.skills.get_metadata(client.my_skills_home())
    )

    assert route == "COMPLEX_RESOURCE_METADATA"
    assert groups["bucket"] == BUCKET
    # An empty {path} is how Core lists the bucket root - and the separator
    # before it is literal, so this only matches with the trailing slash.
    assert groups["path"] == ""


def test_grouping_folder_listing_is_routable():
    route, groups = _route(
        lambda client: client.skills.get_metadata(f"skills/{BUCKET}/writing")
    )

    assert route == "COMPLEX_RESOURCE_METADATA"
    assert groups["path"] == "writing/"


def test_list_files_is_routable():
    route, groups = _route(lambda client: client.skills.list_files(SKILL))

    assert route == "COMPLEX_RESOURCE_FILE_METADATA"
    assert groups["path"] == "writing/toneofvoice"
    assert groups["filePath"] is None


def test_list_files_subfolder_is_routable():
    route, groups = _route(
        lambda client: client.skills.list_files(SKILL, path="references")
    )

    assert route == "COMPLEX_RESOURCE_FILE_METADATA"
    assert groups["filePath"] == "references"


def test_get_file_is_routable():
    route, groups = _route(
        lambda client: client.skills.get_file(SKILL, "SKILL.md")
    )

    assert route == "COMPLEX_RESOURCE_FILE"
    assert groups["path"] == "writing/toneofvoice"
    assert groups["filePath"] == "SKILL.md"


def test_download_is_routable():
    route, groups = _route(lambda client: client.skills.download(SKILL))

    assert route == "COMPLEX_RESOURCE"
    assert groups["path"] == "writing/toneofvoice"
