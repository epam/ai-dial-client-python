import json
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock

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


def _make_capturing_client(captured: List[httpx.Request]) -> Dial:
    client = Dial(api_key="dummy", base_url="http://dial.core")

    def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=PROMPT_METADATA_MOCK
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = Mock(return_value="test-bucket")
    return client


def _body(request: httpx.Request) -> Dict[str, Any]:
    return json.loads(request.content.decode())


def _make_async_capturing_client(
    captured: List[httpx.Request],
) -> AsyncDial:
    client = AsyncDial(api_key="dummy", base_url="http://dial.core")

    async def send_mock(request: httpx.Request, **_: Any) -> httpx.Response:
        captured.append(request)
        response = httpx.Response(
            status_code=200, request=request, json=PROMPT_METADATA_MOCK
        )
        response.request = request
        return response

    client._http_client._internal_http_client.send = send_mock
    client._get_my_bucket = AsyncMock(return_value="test-bucket")
    return client


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


# ---------------------------------------------------------------------------
# prompts.save()
# ---------------------------------------------------------------------------


def test_save_prompt():
    client = get_client_mock(status_code=200, json_mock=PROMPT_METADATA_MOCK)
    prompt = Prompt(**PROMPT_MOCK)

    result = client.prompts.save(
        "prompts/test-bucket/my-folder/my-prompt", prompt=prompt
    )

    assert isinstance(result, PromptMetadata)
    assert result.node_type == "ITEM"
    assert result.bucket == "test-bucket"


@pytest.mark.asyncio
async def test_async_save_prompt():
    client = get_async_client_mock(
        status_code=200, json_mock=PROMPT_METADATA_MOCK
    )
    prompt = Prompt(**PROMPT_MOCK)

    result = await client.prompts.save(
        "prompts/test-bucket/my-folder/my-prompt", prompt=prompt
    )

    assert isinstance(result, PromptMetadata)
    assert result.node_type == "ITEM"
    assert result.bucket == "test-bucket"


def test_save_prompt_sends_json_and_etag_headers():
    captured: List[httpx.Request] = []
    client = _make_capturing_client(captured)
    prompt = Prompt(**PROMPT_MOCK)

    result = client.prompts.save(
        url=client.my_prompts_home() / "my-folder/my-prompt",
        prompt=prompt,
        etag_if_match="etag-1",
        etag_if_none_match="*",
    )

    assert isinstance(result, PromptMetadata)
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "PUT"
    assert request.url.path == "/v1/prompts/test-bucket/my-folder/my-prompt"
    assert request.headers["if-match"] == "etag-1"
    assert request.headers["if-none-match"] == "*"
    assert _body(request) == {
        "id": "prompts/test-bucket/my-folder/my-prompt",
        "name": "my-prompt",
        "folderId": "my-folder",
        "content": "You are a helpful assistant.",
    }


@pytest.mark.asyncio
async def test_async_save_prompt_sends_json_and_etag_headers():
    captured: List[httpx.Request] = []
    client = _make_async_capturing_client(captured)
    prompt = Prompt(**PROMPT_MOCK)

    result = await client.prompts.save(
        url=await client.my_prompts_home() / "my-folder/my-prompt",
        prompt=prompt,
        etag_if_match="etag-1",
        etag_if_none_match="*",
    )

    assert isinstance(result, PromptMetadata)
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "PUT"
    assert request.url.path == "/v1/prompts/test-bucket/my-folder/my-prompt"
    assert request.headers["if-match"] == "etag-1"
    assert request.headers["if-none-match"] == "*"
    assert _body(request) == {
        "id": "prompts/test-bucket/my-folder/my-prompt",
        "name": "my-prompt",
        "folderId": "my-folder",
        "content": "You are a helpful assistant.",
    }


def test_save_prompt_etag_mismatch():
    client = get_client_mock(
        status_code=412,
        json_mock={
            "error": {
                "message": "Precondition Failed",
                "type": "etag_mismatch",
            }
        },
    )
    prompt = Prompt(**PROMPT_MOCK)

    with pytest.raises(EtagMismatchError):
        client.prompts.save(
            "prompts/test-bucket/my-folder/my-prompt",
            prompt=prompt,
            etag_if_match="invalid_etag",
        )


@pytest.mark.asyncio
async def test_async_save_prompt_etag_mismatch():
    client = get_async_client_mock(
        status_code=412,
        json_mock={
            "error": {
                "message": "Precondition Failed",
                "type": "etag_mismatch",
            }
        },
    )
    prompt = Prompt(**PROMPT_MOCK)

    with pytest.raises(EtagMismatchError):
        await client.prompts.save(
            "prompts/test-bucket/my-folder/my-prompt",
            prompt=prompt,
            etag_if_match="invalid_etag",
        )


def test_save_prompt_rejects_non_prompt_url():
    client = get_client_mock(status_code=200, json_mock=PROMPT_METADATA_MOCK)
    prompt = Prompt(**PROMPT_MOCK)

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        client.prompts.save("files/test-bucket/my-folder/my-prompt", prompt)


@pytest.mark.asyncio
async def test_async_save_prompt_rejects_non_prompt_url():
    client = get_async_client_mock(
        status_code=200, json_mock=PROMPT_METADATA_MOCK
    )
    prompt = Prompt(**PROMPT_MOCK)

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        await client.prompts.save(
            "files/test-bucket/my-folder/my-prompt", prompt
        )


# ---------------------------------------------------------------------------
# prompts.delete()
# ---------------------------------------------------------------------------


def test_delete_prompt():
    client = get_client_mock(status_code=200, json_mock={})

    result = client.prompts.delete("prompts/test-bucket/my-folder/my-prompt")
    assert result is None


@pytest.mark.asyncio
async def test_async_delete_prompt():
    client = get_async_client_mock(status_code=200, json_mock={})

    result = await client.prompts.delete(
        "prompts/test-bucket/my-folder/my-prompt"
    )
    assert result is None


def test_delete_prompt_sends_etag_header():
    captured: List[httpx.Request] = []
    client = _make_capturing_client(captured)

    result = client.prompts.delete(
        url=client.my_prompts_home() / "my-folder/my-prompt",
        etag_if_match="etag-1",
    )

    assert result is None
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "DELETE"
    assert request.url.path == "/v1/prompts/test-bucket/my-folder/my-prompt"
    assert request.headers["if-match"] == "etag-1"


@pytest.mark.asyncio
async def test_async_delete_prompt_sends_etag_header():
    captured: List[httpx.Request] = []
    client = _make_async_capturing_client(captured)

    result = await client.prompts.delete(
        url=await client.my_prompts_home() / "my-folder/my-prompt",
        etag_if_match="etag-1",
    )

    assert result is None
    assert len(captured) == 1
    request = captured[0]
    assert request.method == "DELETE"
    assert request.url.path == "/v1/prompts/test-bucket/my-folder/my-prompt"
    assert request.headers["if-match"] == "etag-1"


def test_delete_prompt_etag_mismatch():
    client = get_client_mock(
        status_code=412,
        json_mock={
            "error": {
                "message": "Precondition Failed",
                "type": "etag_mismatch",
            }
        },
    )

    with pytest.raises(EtagMismatchError):
        client.prompts.delete(
            "prompts/test-bucket/my-folder/my-prompt",
            etag_if_match="invalid_etag",
        )


@pytest.mark.asyncio
async def test_async_delete_prompt_etag_mismatch():
    client = get_async_client_mock(
        status_code=412,
        json_mock={
            "error": {
                "message": "Precondition Failed",
                "type": "etag_mismatch",
            }
        },
    )

    with pytest.raises(EtagMismatchError):
        await client.prompts.delete(
            "prompts/test-bucket/my-folder/my-prompt",
            etag_if_match="invalid_etag",
        )


def test_delete_prompt_rejects_non_prompt_url():
    client = get_client_mock(status_code=200, json_mock={})

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        client.prompts.delete("files/test-bucket/my-folder/my-prompt")


@pytest.mark.asyncio
async def test_async_delete_prompt_rejects_non_prompt_url():
    client = get_async_client_mock(status_code=200, json_mock={})

    with pytest.raises(InvalidDialURLError, match="Invalid resource type"):
        await client.prompts.delete("files/test-bucket/my-folder/my-prompt")
