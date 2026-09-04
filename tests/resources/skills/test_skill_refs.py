"""
What the chained-reference design itself adds, on top of the URLs the other
skills tests pin: equivalence of the ways to aim a reference, immutability,
laziness of the bucket lookup, and segment validation at construction time.
"""

from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from aidial_client import AsyncDial, Dial
from aidial_client._exception import InvalidDialURLError
from aidial_client.types.metadata import SkillFileItem, SkillFileMetadata

BUCKET = "test-bucket"
SKILL_URL = f"skills/{BUCKET}/writing/tone-of-voice"
LISTING: dict[str, Any] = {
    "bucket": BUCKET,
    "url": f"skills/{BUCKET}/",
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
}


def _client(captured: list[httpx.Request]) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(200, request=request, json=LISTING)
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = Mock(return_value=BUCKET)
    return client


def _async_client(captured: list[httpx.Request]) -> AsyncDial:
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(200, request=request, json=LISTING)
        response.request = request
        return response

    client._http_client._internal_http_client.send = cast(Any, send_mock)
    client._get_my_bucket = cast(Any, AsyncMock(return_value=BUCKET))
    return client


def _path_of(build) -> str:
    captured: list[httpx.Request] = []
    build(_client(captured))
    return captured[0].url.raw_path.decode()


# --- aiming a reference --------------------------------------------------


def test_truediv_and_path_are_equivalent():
    by_operator = _path_of(lambda c: (c.skills / "a" / "b").list())
    by_keyword = _path_of(lambda c: c.skills(path="a/b").list())
    by_mixture = _path_of(lambda c: (c.skills / "a")(path="b").list())

    assert by_operator == f"/v2/metadata/skills/{BUCKET}/a/b/"
    assert by_operator == by_keyword == by_mixture


def test_path_descends_and_bucket_is_kept():
    assert (
        _path_of(lambda c: (c.skills / "writing")(bucket="public").list())
        == "/v2/metadata/skills/public/writing/"
    )


def test_url_replaces_both_bucket_and_path():
    assert (
        _path_of(
            lambda c: c.skills(bucket="other", path="ignored")(
                url="skills/elsewhere/deep/skill"
            ).download()
        )
        == "/v2/skills/elsewhere/deep/skill"
    )


def test_files_url_round_trips_a_listing_entry():
    # An entry of a files listing carries the "/files/" segment, so it cannot
    # go back through skills(url=...) - the files reference parses it instead.
    assert (
        _path_of(
            lambda c: c.skills.files(
                url=f"{SKILL_URL}/files/references/api.md"
            ).read()
        )
        == f"/v2/skills/{BUCKET}/writing/tone-of-voice/files/references/api.md"
    )


def test_files_url_splits_after_the_first_segment():
    # Core's route requires at least one segment before "files"
    # ("(?<path>.+?)/files/"), so a skill named "files" resolves the same way.
    assert (
        _path_of(
            lambda c: c.skills.files(
                url=f"skills/{BUCKET}/files/files/a.md"
            ).read()
        )
        == f"/v2/skills/{BUCKET}/files/files/a.md"
    )


def test_files_url_without_a_files_segment_is_rejected():
    client = _client([])

    with pytest.raises(InvalidDialURLError, match="must address a file"):
        client.skills.files(url=SKILL_URL)


@pytest.mark.parametrize(
    "call, message",
    [
        (lambda ref: ref(url="x", bucket="b"), "cannot be combined"),
        (lambda ref: ref(url="x", path="p"), "cannot be combined"),
        (lambda ref: ref(), "is required"),
    ],
)
def test_bad_argument_combinations_are_type_errors(call, message):
    # The overloads already reject these statically, so reaching them is a
    # programming error rather than a bad URL.
    client = _client([])

    with pytest.raises(TypeError, match=message):
        call(client.skills)


# --- immutability and laziness -------------------------------------------


def test_narrowing_leaves_the_original_untouched():
    captured: list[httpx.Request] = []
    client = _client(captured)

    root = client.skills
    sub = root / "writing"

    assert root is not sub
    assert root.path == ()
    assert sub.path == ("writing",)

    root.list()
    assert captured[0].url.path == f"/v2/metadata/skills/{BUCKET}/"


@pytest.mark.parametrize(
    "build",
    [
        lambda c: c.skills,
        lambda c: c.skills.files,
        lambda c: _async_client([]).skills,
        lambda c: _async_client([]).skills.files,
    ],
)
def test_references_are_immutable(build):
    reference = build(_client([]))

    with pytest.raises(TypeError):
        reference.path = ("mutated",)


def test_building_a_reference_issues_no_requests():
    captured: list[httpx.Request] = []
    client = _client(captured)

    chain = (client.skills / "writing" / "tone-of-voice").files(path="refs")

    assert captured == []
    assert client._get_my_bucket.call_count == 0
    assert chain.skill_path == ("writing", "tone-of-voice")


def test_own_bucket_is_resolved_once_and_shared():
    client = _client([])

    client.skills.list()
    (client.skills / "writing").list()

    assert client._get_my_bucket.call_count == 1


@pytest.mark.parametrize(
    "build",
    [
        lambda c: c.skills(bucket="public").list(),
        lambda c: c.skills(url=SKILL_URL).download(),
    ],
)
def test_explicit_bucket_skips_the_lookup(build):
    client = _client([])

    build(client)

    assert client._get_my_bucket.call_count == 0


# --- shape guards run before any I/O -------------------------------------


@pytest.mark.parametrize(
    "call, message",
    [
        (lambda c: c.skills.download(), "points at the bucket root"),
        (lambda c: c.skills.files.list(), "points at the bucket root"),
        (
            lambda c: c.skills(url=SKILL_URL).files.read(),
            "no file path was given",
        ),
    ],
)
def test_shape_guards_precede_bucket_resolution(call, message):
    captured: list[httpx.Request] = []
    client = _client(captured)

    with pytest.raises(InvalidDialURLError, match=message):
        call(client)

    assert captured == []
    # The guard has to come first, or a doomed call still costs a round-trip.
    assert client._get_my_bucket.call_count == 0


# --- segment validation --------------------------------------------------


@pytest.mark.parametrize(
    "bad",
    ["", "   ", "/abs", "a//b", ".", "..", "%2e%2e", ".%2e", "a%2fb", "refs/"],
)
@pytest.mark.parametrize(
    "aim",
    [
        lambda ref, value: ref(path=value),
        lambda ref, value: ref / value,
    ],
)
def test_every_path_surface_validates_segments(aim, bad):
    client = _client([])

    with pytest.raises(InvalidDialURLError):
        aim(client.skills, bad)
    with pytest.raises(InvalidDialURLError):
        aim(client.skills(url=SKILL_URL).files, bad)


@pytest.mark.parametrize("bad", ["", "a/b", "..", "a%2fb"])
def test_bucket_is_validated_as_a_single_segment(bad):
    client = _client([])

    with pytest.raises(InvalidDialURLError):
        client.skills(bucket=bad)


def test_root_reference_has_no_phantom_dot_segment():
    # PurePosixPath("") is PurePosixPath("."), which would put a "." in the
    # URL. Segments are stored as a tuple precisely to avoid that.
    client = _client([])

    assert client.skills.path == ()
    assert _path_of(lambda c: c.skills.list()).endswith(f"/{BUCKET}/")


# --- filenames -----------------------------------------------------------


def test_archive_is_named_after_the_skill():
    client = _client([])

    assert client.skills(url=SKILL_URL).download().filename == (
        "tone-of-voice.zip"
    )


def test_read_returns_a_human_readable_filename():
    client = _client([])

    response = (
        client.skills(url=SKILL_URL).files(path="refs/api%20schema.md").read()
    )

    assert response.filename == "api schema.md"


# --- async mirror --------------------------------------------------------


@pytest.mark.asyncio
async def test_async_chain_builds_without_awaiting():
    captured: list[httpx.Request] = []
    client = _async_client(captured)

    skill = client.skills / "writing" / "tone-of-voice"
    files = skill.files(path="references")
    assert captured == []

    await files.list(recursive=True)

    assert captured[0].url.path == (
        f"/v2/metadata/skills/{BUCKET}/writing/tone-of-voice/files/references"
    )
    assert client._get_my_bucket.await_count == 1


# --- node_type derivation ------------------------------------------------

# Real listings captured from DIAL Core (2026-09-04), one per mode. A
# recursive listing flattens the tree to leaf files at every depth; a
# non-recursive one returns the immediate children, and reports its
# subfolders as "ITEM" with a trailing slash. Neither carries an etag.
REAL_RECURSIVE_LISTING: dict[str, Any] = {
    "name": "files",
    "parentPath": "all-three-conventionss",
    "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
    "url": (
        "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
        "/all-three-conventionss/files/"
    ),
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
    "items": [
        {
            "name": "SKILL.md",
            "parentPath": "all-three-conventionss/files",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/all-three-conventionss/files/SKILL.md"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            "updatedAt": 1788267212576,
        },
        {
            "name": "regions.csv",
            "parentPath": "all-three-conventionss/files/assets",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/all-three-conventionss/files/assets/regions.csv"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            "updatedAt": 1788267212609,
        },
        {
            "name": "extract.py",
            "parentPath": "all-three-conventionss/files/scripts",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/all-three-conventionss/files/scripts/extract.py"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            "updatedAt": 1788267212641,
        },
    ],
}


def test_real_recursive_listing_is_left_alone():
    page = SkillFileMetadata(**REAL_RECURSIVE_LISTING)

    assert page.node_type == "FOLDER"
    assert [item.node_type for item in page.items or []] == ["ITEM"] * 3
    assert [item.name for item in page.items or []] == [
        "SKILL.md",
        "regions.csv",
        "extract.py",
    ]


def test_trailing_slash_derives_folder():
    payload: dict[str, Any] = {
        "bucket": BUCKET,
        "url": f"{SKILL_URL}/files/references/",
        "nodeType": "ITEM",
        "resourceType": "SKILL",
    }

    assert SkillFileItem(**payload).node_type == "FOLDER"


def test_no_trailing_slash_derives_item():
    # The derivation is symmetric, as the review asked for: the url is the
    # only input. A listing root scoped to a subfolder is requested without
    # a trailing slash, so this is the case to watch - see the PR thread.
    payload: dict[str, Any] = {
        "bucket": BUCKET,
        "url": f"{SKILL_URL}/files/references",
        "nodeType": "FOLDER",
        "resourceType": "SKILL",
    }

    assert SkillFileMetadata(**payload).node_type == "ITEM"


# The same skill listed non-recursively: files and directories side by side,
# every one of them "ITEM", directories distinguished only by trailing "/".
REAL_NON_RECURSIVE_LISTING: dict[str, Any] = {
    "name": "files",
    "parentPath": "skill-creator",
    "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
    "url": (
        "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
        "/skill-creator/files/"
    ),
    "nodeType": "FOLDER",
    "resourceType": "SKILL",
    "items": [
        {
            "name": "SKILL.md",
            "parentPath": "skill-creator/files",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/skill-creator/files/SKILL.md"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
            "updatedAt": 1788530552986,
        },
        {
            "name": "agents",
            "parentPath": "skill-creator/files",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/skill-creator/files/agents/"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
        },
        {
            "name": "scripts",
            "parentPath": "skill-creator/files",
            "bucket": "4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc",
            "url": (
                "skills/4T56XoBkFtVqFQFmwHtbkUbjx8zLC8Sypb3xrJH4MACc"
                "/skill-creator/files/scripts/"
            ),
            "nodeType": "ITEM",
            "resourceType": "SKILL",
        },
    ],
}


def test_real_non_recursive_listing_corrects_subfolders():
    page = SkillFileMetadata(**REAL_NON_RECURSIVE_LISTING)

    # Core sent "ITEM" for all three; the validator corrects the two
    # directories from the trailing "/" of their url.
    assert [(i.name, i.node_type) for i in page.items or []] == [
        ("SKILL.md", "ITEM"),
        ("agents", "FOLDER"),
        ("scripts", "FOLDER"),
    ]
    # Directory entries carry no timestamp, and nothing here carries an etag.
    items = page.items or []
    assert [i.updated_at for i in items] == [1788530552986, None, None]
    assert all(i.etag is None for i in items)
