import pytest

from aidial_client._exception import InvalidDialURLError, NotDialURLError
from aidial_client.helpers.storage_resource import DialStorageResourceMixin

DIAL_API_URL = "https://dial.core/v1/"
RESOURCE_TYPES = ["files", "conversations", "prompts"]


@pytest.mark.parametrize(
    "resource_type, url, expected",
    [
        ("files", "files/bucket/file.txt", "files/bucket/file.txt"),
        (
            "conversations",
            "conversations/bucket/conv.json",
            "conversations/bucket/conv.json",
        ),
        ("prompts", "prompts/bucket/prompt.txt", "prompts/bucket/prompt.txt"),
        (
            "files",
            "files/bucket/%E6%88%91%E7%9A%84%E6%96%87%E4%BB%B6%E5%A4%B9/%E6%88%91%E7%9A%84%E6%96%87%E4%BB%B6%20%281%29.pdf",  # noqa # noqa
            "files/bucket/%E6%88%91%E7%9A%84%E6%96%87%E4%BB%B6%E5%A4%B9/%E6%88%91%E7%9A%84%E6%96%87%E4%BB%B6%20%281%29.pdf",  # noqa
        ),
    ],
)
def test_get_api_path_relative_url(resource_type, url, expected):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    result = mixin.get_api_path(url)
    assert result == expected


@pytest.mark.parametrize(
    "resource_type, url, expected",
    [
        (
            "files",
            f"{DIAL_API_URL}files/bucket/file.txt",
            "files/bucket/file.txt",
        ),
        (
            "conversations",
            f"{DIAL_API_URL}conversations/bucket/conv.json",
            "conversations/bucket/conv.json",
        ),
        (
            "prompts",
            f"{DIAL_API_URL}prompts/bucket/prompt.txt",
            "prompts/bucket/prompt.txt",
        ),
    ],
)
def test_get_api_path_absolute_url(resource_type, url, expected):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    result = mixin.get_api_path(url)
    assert result == expected


@pytest.mark.parametrize("resource_type", RESOURCE_TYPES)
def test_get_api_path_invalid_dial_url(resource_type):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    url = "https://other-dial.core/v1/files/bucket/file.txt"
    with pytest.raises(NotDialURLError) as e:
        mixin.get_api_path(url)
    assert e.value.message == f"Provided URL is not DIAL URL: {url}"


@pytest.mark.parametrize(
    "resource_type, url",
    [
        ("files", "https://dial.core/v1/conversations/bucket/conv.json"),
        (
            "conversations",
            "https://dial.core/v1/prompts/bucket/prompt.txt",
        ),
        ("prompts", "https://dial.core/v1/files/bucket/file.txt"),
    ],
)
def test_get_api_path_invalid_resource_type(resource_type, url):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    with pytest.raises(
        InvalidDialURLError, match="Invalid resource type for URL"
    ):
        mixin.get_api_path(url)


@pytest.mark.parametrize(
    "resource_type, url",
    [
        ("files", "https://dial.core/v1/files/file.txt"),
        ("conversations", "https://dial.core/v1/conversations/conv.json"),
        ("prompts", "https://dial.core/v1/prompts/prompt.txt"),
    ],
)
def test_get_api_path_missing_bucket(resource_type, url):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    with pytest.raises(InvalidDialURLError, match="Missing bucket in URL"):
        mixin.get_api_path(url)


@pytest.mark.parametrize("resource_type", RESOURCE_TYPES)
def test_get_api_path_invalid_path(resource_type):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    url = "https://dial.core/v2/files/bucket/file.txt"
    with pytest.raises(
        InvalidDialURLError,
        match="Provided URL path .* does not match with DIAL API URL",
    ):
        mixin.get_api_path(
            url,
        )


@pytest.mark.parametrize(
    "resource_type, url, expected",
    [
        (
            "files",
            f"{DIAL_API_URL}files/bucket/file.txt?param=value",
            "files/bucket/file.txt",
        ),
        (
            "conversations",
            f"{DIAL_API_URL}conversations/bucket/conv.json?param=value",
            "conversations/bucket/conv.json",
        ),
        (
            "prompts",
            f"{DIAL_API_URL}prompts/bucket/prompt.txt?param=value",
            "prompts/bucket/prompt.txt",
        ),
    ],
)
def test_get_api_path_with_query_params(resource_type, url, expected):
    mixin = DialStorageResourceMixin(
        resource_type=resource_type, dial_api_url=DIAL_API_URL
    )
    result = mixin.get_api_path(url)
    assert result == expected
