import pytest

from aidial_client._exception import DialException
from aidial_client.types.toolset import ToolsetInfo
from tests.client_mock import get_async_client_mock, get_client_mock

TOOLSET_MOCK = {
    "id": "toolsets/bucket/folder/my-toolset",
    "toolset": "toolsets/bucket/folder/my-toolset",
    "display_name": "My Toolset",
    "display_version": "1.0.0",
    "description": "A test toolset",
    "icon_url": "http://toolset/icon.svg",
    "owner": "owner-name",
    "object": "toolset",
    "status": "succeeded",
    "reference": "ff5584b7-a82b-4f4f-bf42-5bf74a3893d6",
    "description_keywords": ["keyword1", "keyword2"],
    "max_retry_attempts": 3,
    "created_at": 1672534800,
    "updated_at": 1672534900,
    "transport": "HTTP",
    "allowed_tools": ["tool1", "tool2"],
    "features": {
        "rate": True,
        "tokenize": False,
        "truncate_prompt": False,
        "configuration": False,
        "system_prompt": True,
        "tools": True,
        "seed": False,
        "url_attachments": False,
        "folder_attachments": False,
    },
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_get_toolset():
    client = get_client_mock(status_code=200, json_mock=TOOLSET_MOCK)
    result = client.toolset.get("my-toolset")
    assert isinstance(result, ToolsetInfo)
    assert result.id == "toolsets/bucket/folder/my-toolset"
    assert result.toolset == "toolsets/bucket/folder/my-toolset"
    assert result.transport == "HTTP"
    assert result.allowed_tools == ["tool1", "tool2"]
    assert result.display_name == "My Toolset"


@pytest.mark.asyncio
async def test_async_get_toolset():
    client = get_async_client_mock(status_code=200, json_mock=TOOLSET_MOCK)
    result = await client.toolset.get("my-toolset")
    assert isinstance(result, ToolsetInfo)
    assert result.id == "toolsets/bucket/folder/my-toolset"
    assert result.toolset == "toolsets/bucket/folder/my-toolset"
    assert result.transport == "HTTP"
    assert result.allowed_tools == ["tool1", "tool2"]


# ---------------------------------------------------------------------------
# Optional / nested fields
# ---------------------------------------------------------------------------


def test_get_toolset_features():
    client = get_client_mock(status_code=200, json_mock=TOOLSET_MOCK)
    result = client.toolset.get("my-toolset")
    assert result.features is not None
    assert result.features.rate is True
    assert result.features.tools is True
    assert result.reference == "ff5584b7-a82b-4f4f-bf42-5bf74a3893d6"
    assert result.description_keywords == ["keyword1", "keyword2"]
    assert result.max_retry_attempts == 3


def test_get_toolset_missing_optional_fields():
    minimal = {"id": "ts", "toolset": "ts"}
    client = get_client_mock(status_code=200, json_mock=minimal)
    result = client.toolset.get("ts")
    assert isinstance(result, ToolsetInfo)
    assert result.transport is None
    assert result.allowed_tools == []
    assert result.features is None
    assert result.description_keywords == []


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_get_toolset_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        client.toolset.get("my-toolset")


@pytest.mark.asyncio
async def test_async_get_toolset_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        await client.toolset.get("my-toolset")
