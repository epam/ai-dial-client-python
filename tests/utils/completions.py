"""Shared helpers for the `test_completions_*` tests"""

from typing import Any

from aidial_client import AsyncDial, Dial
from aidial_client._utils._dict import remove_none
from aidial_client.types.chat import (
    ChatCompletionChunk,
    ChatCompletionMessage,
    ChatCompletionMessageDelta,
    ChatCompletionResponse,
    Message,
)
from tests.client_mock import get_async_client_mock, get_client_mock
from tests.utils.chunks import create_sse_data_field

DIAL_MODEL = "gpt-4o"
MESSAGES: list[Message] = [{"role": "user", "content": "2+3="}]

Completion = ChatCompletionResponse | ChatCompletionChunk


def block_response(
    *,
    content: str | None = "5",
    custom_content: dict | None = None,
    usage: dict | None = None,
    statistics: dict | None = None,
) -> dict[str, Any]:
    """Non-streaming chat completion response body"""
    return remove_none(
        {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 1723806872,
            "model": DIAL_MODEL,
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "stop",
                    "message": remove_none(
                        {
                            "role": "assistant",
                            "content": content,
                            "custom_content": custom_content,
                        }
                    ),
                }
            ],
            "usage": usage,
            "statistics": statistics,
        }
    )


def as_single_chunk(response: dict[str, Any]) -> list[bytes]:
    """The very same response body delivered as a single streaming chunk"""
    choices = [
        {
            **{key: value for key, value in choice.items() if key != "message"},
            "delta": choice["message"],
        }
        for choice in response["choices"]
    ]
    return [
        create_sse_data_field(
            {**response, "object": "chat.completion.chunk", "choices": choices}
        )
    ]


def message_of(
    completion: Completion,
) -> ChatCompletionMessage | ChatCompletionMessageDelta:
    if isinstance(completion, ChatCompletionChunk):
        return completion.choices[0].delta
    return completion.choices[0].message


async def create_completion(
    *,
    is_async: bool,
    stream: bool,
    response: dict[str, Any] | None = None,
    sent_requests: list | None = None,
    **request_params: Any,
) -> Completion:
    """
    Runs a chat completion against the mocked response,
    either in sync or async and either in streaming or non-streaming mode.
    """
    response = response or block_response()
    request_params.setdefault("messages", MESSAGES)
    response_mock: dict[str, Any] = (
        {"stream_chunks_mock": as_single_chunk(response)}
        if stream
        else {"json_mock": response}
    )
    if is_async:
        async_client = get_async_client_mock(
            status_code=200, sent_requests=sent_requests, **response_mock
        )
        return await _create_async(async_client, stream, request_params)

    client = get_client_mock(
        status_code=200, sent_requests=sent_requests, **response_mock
    )
    return _create_sync(client, stream, request_params)


def _create_sync(client: Dial, stream: bool, params: dict[str, Any]):
    if not stream:
        return client.chat.completions.create(
            deployment_name=DIAL_MODEL, stream=False, **params
        )

    chunks = client.chat.completions.create(
        deployment_name=DIAL_MODEL, stream=True, **params
    )
    return _single(list(chunks))


async def _create_async(
    client: AsyncDial, stream: bool, params: dict[str, Any]
):
    if not stream:
        return await client.chat.completions.create(
            deployment_name=DIAL_MODEL, stream=False, **params
        )

    chunks = await client.chat.completions.create(
        deployment_name=DIAL_MODEL, stream=True, **params
    )
    return _single([chunk async for chunk in chunks])


def _single(chunks: list[ChatCompletionChunk]) -> ChatCompletionChunk:
    assert len(chunks) == 1, f"expected a single chunk, got {len(chunks)}"
    return chunks[0]
