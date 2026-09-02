import pytest

from aidial_client._exception import InvalidDialURLError, NotDialURLError
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
        (
            "https://dial.core/v1/conversations/my-bucket/conv-123.json",
            "https://dial.core/v1/",
            "conversations",
            {
                "resource_type": "conversations",
                "bucket": "my-bucket",
                "absolute_url": "https://dial.core/v1/conversations/my-bucket/conv-123.json",
                "relative_url": "/v1/conversations/my-bucket/conv-123.json",
                "api_path": "conversations/my-bucket/conv-123.json",
                "bucket_path": "conv-123.json",
                "filename": "conv-123.json",
            },
        ),
        (
            "https://dial.core/v1/files/my-bucket/subfolder/document.pdf",
            "https://dial.core/v1/",
            "files",
            {
                "resource_type": "files",
                "bucket": "my-bucket",
                "absolute_url": "https://dial.core/v1/files/my-bucket/subfolder/document.pdf",
                "relative_url": "/v1/files/my-bucket/subfolder/document.pdf",
                "api_path": "files/my-bucket/subfolder/document.pdf",
                "bucket_path": "subfolder/document.pdf",
                "filename": "document.pdf",
            },
        ),
    ],
)
def test_parse_storage_resource_valid(
    url, dial_api_url, resource_type, expected
):
    result = parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
        expected_resource_type=resource_type,
    )
    assert result.dict() == expected

    without_resource_type = parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
    )
    assert without_resource_type.dict() == expected


@pytest.mark.parametrize(
    "url, dial_api_url, resource_type",
    [
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
        (
            "/files/test-bucket/files.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "v1/files/test-bucket/files.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "/v1/files/test-bucket/files.txt",
            "https://dial.core/v1/",
            "files",
        ),
    ],
)
def test_parse_storage_resource_invalid_url(url, dial_api_url, resource_type):
    with pytest.raises(InvalidDialURLError):
        parse_storage_resource(
            url=url,
            dial_api_url=dial_api_url,
            expected_resource_type=resource_type,
        )


@pytest.mark.parametrize(
    "url, dial_api_url, expected_resource_type",
    [
        (
            "files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "prompts/my-bucket/prompt-123",
            "https://dial.core/v1/",
            "prompts",
        ),
        (
            "conversations/my-bucket/conversation-123",
            "https://dial.core/v1/",
            "conversations",
        ),
        (
            "https://dial.core/v1/files/my-bucket/file.txt",
            "https://dial.core/v1/",
            "files",
        ),
        (
            "https://dial.core/v1/prompts/my-bucket/prompt-123",
            "https://dial.core/v1/",
            "prompts",
        ),
        (
            "https://dial.core/v1/conversations/my-bucket/conversation-123",
            "https://dial.core/v1/",
            "conversations",
        ),
    ],
)
def test_parse_storage_resource_unknown_resource_type(
    url, dial_api_url, expected_resource_type
):
    storage_resource = parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
    )
    assert storage_resource.resource_type == expected_resource_type


def test_parse_storage_resource_non_dial_ignore():
    with pytest.raises(NotDialURLError):
        parse_storage_resource(
            url="https://example.com/files/my-bucket/file.txt",
            dial_api_url="https://dial.core/v1/",
            expected_resource_type="files",
        )


@pytest.mark.parametrize(
    "url, expected_api_path",
    [
        ("skills/my-bucket/my-skill", "skills/my-bucket/my-skill"),
        ("skills/my-bucket/group/my-skill", "skills/my-bucket/group/my-skill"),
        (
            "https://dial.core/v2/skills/my-bucket/my-skill",
            "skills/my-bucket/my-skill",
        ),
    ],
)
def test_parse_v2_skill_resource(url, expected_api_path):
    result = parse_storage_resource(
        url=url,
        dial_api_url="https://dial.core/v2/",
        expected_resource_type="skills",
        api_prefix="v2/",
    )
    assert result.resource_type == "skills"
    assert result.bucket == "my-bucket"
    assert result.api_path == expected_api_path


@pytest.mark.parametrize(
    "url, dial_api_url, resource_type, api_prefix",
    [
        ("skills/my-bucket", "https://dial.core/v2/", "skills", "v2/"),
        ("skills/my-bucket/", "https://dial.core/v2/", "skills", "v2/"),
        ("files/my-bucket", "https://dial.core/v1/", "files", "v1/"),
    ],
)
def test_parse_bucket_root_when_allowed(
    url, dial_api_url, resource_type, api_prefix
):
    result = parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
        expected_resource_type=resource_type,
        api_prefix=api_prefix,
        allow_bucket_root=True,
    )
    assert result.bucket == "my-bucket"
    assert result.bucket_path == ""
    assert result.filename is None
    assert result.api_path == f"{resource_type}/my-bucket"


@pytest.mark.parametrize(
    "url, dial_api_url, resource_type, api_prefix",
    [
        ("skills/my-bucket", "https://dial.core/v2/", "skills", "v2/"),
        ("files/my-bucket", "https://dial.core/v1/", "files", "v1/"),
    ],
)
def test_parse_bucket_root_rejected_by_default(
    url, dial_api_url, resource_type, api_prefix
):
    # A two-segment path is ambiguous ("files/my-file.txt" has the same
    # shape), so bucket-root parsing stays opt-in.
    with pytest.raises(InvalidDialURLError, match="Missing bucket in URL"):
        parse_storage_resource(
            url=url,
            dial_api_url=dial_api_url,
            expected_resource_type=resource_type,
            api_prefix=api_prefix,
        )


def test_parse_rejects_v2_api_prefix_as_relative_part():
    with pytest.raises(
        InvalidDialURLError, match="API prefix as relative part"
    ):
        parse_storage_resource(
            url="v2/skills/my-bucket/my-skill",
            dial_api_url="https://dial.core/v2/",
            expected_resource_type="skills",
            api_prefix="v2/",
        )


def test_parse_rejects_skills_url_for_v1_resource():
    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        parse_storage_resource(
            url="skills/my-bucket/my-skill",
            dial_api_url="https://dial.core/v1/",
            expected_resource_type="files",
        )
