import pytest

from aidial_client._exception import InvalidDialURLError
from aidial_client.helpers.storage_resource import parse_storage_resource


@pytest.mark.parametrize(
    "url, dial_api_url, resource_type, expected",
    [
        (
            "files/my-bucket/my-folder/my-file.txt",
            "https://dial.core/v1/",
            "files",
            {
                "resource_type": "files",
                "bucket": "my-bucket",
                "absolute_url": "https://dial.core/v1/files/my-bucket/my-folder/my-file.txt",  # noqa: E501
                "relative_url": "/v1/files/my-bucket/my-folder/my-file.txt",
                "api_path": "files/my-bucket/my-folder/my-file.txt",
                "bucket_path": "my-folder/my-file.txt",
                "filename": "my-file.txt",
            },
        ),
        (
            "/v1/conversations/my-bucket/conversation-123",
            "https://dial.core/v1/",
            "conversations",
            {
                "resource_type": "conversations",
                "bucket": "my-bucket",
                "absolute_url": "https://dial.core/v1/conversations/my-bucket/conversation-123",  # noqa: E501
                "relative_url": "/v1/conversations/my-bucket/conversation-123",
                "api_path": "conversations/my-bucket/conversation-123",
                "bucket_path": "conversation-123",
                "filename": "conversation-123",
            },
        ),
        (
            "prompts/my-bucket/prompt-456.txt",
            "https://dial.core/v1/",
            "prompts",
            {
                "resource_type": "prompts",
                "bucket": "my-bucket",
                "absolute_url": "https://dial.core/v1/prompts/my-bucket/prompt-456.txt",  # noqa: E501
                "relative_url": "/v1/prompts/my-bucket/prompt-456.txt",
                "api_path": "prompts/my-bucket/prompt-456.txt",
                "bucket_path": "prompt-456.txt",
                "filename": "prompt-456.txt",
            },
        ),
    ],
)
def test_parse_storage_resource_valid(
    url, dial_api_url, resource_type, expected
):
    result = parse_storage_resource(
        url, dial_api_url, resource_type, ignore_non_dial_url=False
    )
    assert result.dict() == expected


@pytest.mark.parametrize(
    "url, dial_api_url, resource_type",
    [
        (
            "https://example.com/files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "conversations",
        ),
        (
            "files/file.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "v2/files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
        ),
    ],
)
def test_parse_storage_resource_invalid_url(url, dial_api_url, resource_type):
    with pytest.raises(InvalidDialURLError):
        parse_storage_resource(
            url, dial_api_url, resource_type, ignore_non_dial_url=False
        )


def test_parse_storage_resource_non_dial_ignore():
    with pytest.raises(InvalidDialURLError):
        parse_storage_resource(
            "https://example.com/files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
            ignore_non_dial_url=False,
        )
    assert (
        parse_storage_resource(
            "https://example.com/files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
            ignore_non_dial_url=True,
        )
        is None
    )
