import pytest

from aidial_client._exception import DialException, ResourceNotFoundError
from aidial_client.types.metadata import PromptMetadata
from aidial_client.types.prompt import Prompt
from tests.client_mock import get_async_client_mock, get_client_mock

PROMPT_MOCK = {
    "id": "prompts/test-bucket/my-folder/my-prompt",
    "name": "my-prompt",
    "folderId": "my-folder",
    "content": "You are a helpful assistant.",
}

PROMPT_NO_CONTENT_MOCK = {
    "id": "prompts/test-bucket/my-folder/my-prompt",
    "name": "my-prompt",
    "folderId": "my-folder",
}

PROMPT_METADATA_MOCK = {
    "name": "my-prompt",
    "parentPath": "my-folder",
    "bucket": "test-bucket",
    "url": "prompts/test-bucket/my-folder/my-prompt",
    "nodeType": "ITEM",
    "resourceType": "PROMPT",
    "items": [],
}


# ---------------------------------------------------------------------------
# prompts.get()
# ---------------------------------------------------------------------------


def test_get_prompt():
    client = get_client_mock(status_code=200, json_mock=PROMPT_MOCK)
    result = client.prompts.get("prompts/test-bucket/my-folder/my-prompt")
    assert isinstance(result, Prompt)
    assert result.id == "prompts/test-bucket/my-folder/my-prompt"
    assert result.name == "my-prompt"
    assert result.folder_id == "my-folder"
    assert result.content == "You are a helpful assistant."


@pytest.mark.asyncio
async def test_async_get_prompt():
    client = get_async_client_mock(status_code=200, json_mock=PROMPT_MOCK)
    result = await client.prompts.get("prompts/test-bucket/my-folder/my-prompt")
    assert isinstance(result, Prompt)
    assert result.id == "prompts/test-bucket/my-folder/my-prompt"
    assert result.name == "my-prompt"
    assert result.folder_id == "my-folder"
    assert result.content == "You are a helpful assistant."


def test_get_prompt_no_content():
    client = get_client_mock(status_code=200, json_mock=PROMPT_NO_CONTENT_MOCK)
    result = client.prompts.get("prompts/test-bucket/my-folder/my-prompt")
    assert isinstance(result, Prompt)
    assert result.content is None


def test_get_prompt_not_found():
    client = get_client_mock(
        status_code=404,
        json_mock={
            "error": {
                "message": "Not found",
                "type": "not_found",
            }
        },
    )
    with pytest.raises(ResourceNotFoundError):
        client.prompts.get("prompts/test-bucket/nonexistent/prompt")


@pytest.mark.asyncio
async def test_async_get_prompt_not_found():
    client = get_async_client_mock(
        status_code=404,
        json_mock={
            "error": {
                "message": "Not found",
                "type": "not_found",
            }
        },
    )
    with pytest.raises(ResourceNotFoundError):
        await client.prompts.get("prompts/test-bucket/nonexistent/prompt")


def test_get_prompt_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={
            "error": {
                "message": "Unauthorized",
                "type": "auth_error",
            }
        },
    )
    with pytest.raises(DialException):
        client.prompts.get("prompts/test-bucket/my-folder/my-prompt")


@pytest.mark.asyncio
async def test_async_get_prompt_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={
            "error": {
                "message": "Unauthorized",
                "type": "auth_error",
            }
        },
    )
    with pytest.raises(DialException):
        await client.prompts.get("prompts/test-bucket/my-folder/my-prompt")


# ---------------------------------------------------------------------------
# prompts.get_metadata()
# ---------------------------------------------------------------------------


def test_get_prompt_metadata():
    client = get_client_mock(status_code=200, json_mock=PROMPT_METADATA_MOCK)
    result = client.prompts.get_metadata(
        "prompts/test-bucket/my-folder/my-prompt"
    )
    assert isinstance(result, PromptMetadata)
    assert result.node_type == "ITEM"
    assert result.bucket == "test-bucket"


@pytest.mark.asyncio
async def test_async_get_prompt_metadata():
    client = get_async_client_mock(
        status_code=200, json_mock=PROMPT_METADATA_MOCK
    )
    result = await client.prompts.get_metadata(
        "prompts/test-bucket/my-folder/my-prompt"
    )
    assert isinstance(result, PromptMetadata)
    assert result.node_type == "ITEM"
    assert result.bucket == "test-bucket"
