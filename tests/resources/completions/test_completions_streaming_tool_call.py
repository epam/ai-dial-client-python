import inspect
from collections.abc import Iterable

import pytest

from aidial_client.types.chat import ChatCompletionChunk, ToolParam
from tests.client_mock import get_async_client_mock, get_client_mock
from tests.utils.chunks import create_mock_chunk, create_sse_data_field

_TOOL_DEFINITION: ToolParam = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Performs WEB search.",
        "parameters": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "The search query or question to search for on the web",
                }
            },
            "required": ["request"],
        },
    },
}

_DELTA_CHUNKS: list[dict] = [
    {
        "role": "assistant",
        "tool_calls": [
            {
                "index": 0,
                "id": "call_giAQRJYhG7UEMKwTU5dkuOKq",
                "function": {"arguments": "", "name": "web_search"},
                "type": "function",
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": '{"', "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": "request", "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": '":"', "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": "current", "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": " weather", "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": " in", "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": " Paris", "name": None},
                "type": None,
            }
        ],
    },
    {
        "role": None,
        "tool_calls": [
            {
                "index": 0,
                "id": None,
                "function": {"arguments": '"}', "name": None},
                "type": None,
            }
        ],
    },
    {"role": None, "tool_calls": None},
]

_STREAM_CHUNKS_MOCK: list[bytes] = [
    *[
        create_sse_data_field(create_mock_chunk(delta=delta))
        for delta in _DELTA_CHUNKS
    ],
    create_sse_data_field(
        create_mock_chunk(
            finish_reason="tool_calls",
            usage={
                "prompt_tokens": 20,
                "completion_tokens": 10,
                "total_tokens": 30,
            },
        )
    ),
]


def _validate_chunks(chunks: list[ChatCompletionChunk]):
    assert all(len(chunk.choices) for chunk in chunks)
    assert all(chunk.choices[0].delta for chunk in chunks)
    assert all(chunk.choices[0].delta.tool_calls for chunk in chunks[:-2])
    assert all(chunk.choices[0].delta.content is None for chunk in chunks)
    total_arguments = "".join(
        chunk.choices[0].delta.tool_calls[0].function.arguments or ""  # type: ignore[index,union-attr]
        for chunk in chunks[:-2]
    )
    assert total_arguments == '{"request":"current weather in Paris"}'

    # Last chunk has no content, but usage and stop_reason
    assert chunks[-1].choices[0].delta.content is None
    assert chunks[-1].choices[0].finish_reason == "tool_calls"
    assert chunks[-1].usage
    assert chunks[-1].usage.total_tokens == 30
    assert chunks[-1].usage.prompt_tokens == 20
    assert chunks[-1].usage.completion_tokens == 10


def test_sync_streaming_tool_call():
    client = get_client_mock(
        status_code=200,
        stream_chunks_mock=_STREAM_CHUNKS_MOCK,
    )

    response = client.chat.completions.create(
        deployment_name="gpt-35-turbo",
        messages=[{"role": "user", "content": "what's the weather in Paris?"}],
        tools=[_TOOL_DEFINITION],
        stream=True,
    )
    assert isinstance(response, Iterable)
    chunks = list(response)
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)


@pytest.mark.asyncio
async def test_async_streaming_tool_call():
    async_client = get_async_client_mock(
        status_code=200,
        stream_chunks_mock=_STREAM_CHUNKS_MOCK,
    )
    response = await async_client.chat.completions.create(
        deployment_name="gpt-35-turbo",
        messages=[{"role": "user", "content": "what's the weather in Paris?"}],
        tools=[_TOOL_DEFINITION],
        stream=True,
    )

    assert inspect.isasyncgen(response)
    chunks = [chunk async for chunk in response]
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)
    _validate_chunks(chunks)
