import inspect
from typing import Iterable, List

import pytest

from aidial_client.types.chat import ChatCompletionChunk
from tests.client_mock import get_async_client_mock, get_client_mock

STREAM_CHUNKS_MOCK: List[bytes] = [
    b'data: {"id":"chatcmpl-test","choices":[{"delta":{"content":"","role":"assistant"},"finish_reason":null,"index":0,"logprobs":null}],"created":1723806872,"model":"gpt-35-turbo","object":"chat.completion.chunk","system_fingerprint":null}\n\n',  # noqa: E501
    b'data: {"id":"chatcmpl-test","choices":[{"delta":{"content":"5"},"finish_reason":null,"index":0,"logprobs":null}],"created":1723806872,"model":"gpt-35-turbo","object":"chat.completion.chunk","system_fingerprint":null}\n\n'  # noqa: E501
    b'data: {"id":"chatcmpl-test","choices":[{"delta":{},"finish_reason":"stop","index":0,"logprobs":null}],"created":1723806872,"model":"gpt-35-turbo","object":"chat.completion.chunk","system_fingerprint":null,"usage":{"completion_tokens":1,"prompt_tokens":11,"total_tokens":12}}\n\n',  # noqa: E501
]


def _validate_chunks(chunks):
    assert all(len(chunk.choices) for chunk in chunks)
    assert all(chunk.choices[0].delta for chunk in chunks)
    # All except last chunk has some content
    assert all(
        chunk.choices[0].delta.content is not None for chunk in chunks[:-1]
    )
    total_content = "".join(
        chunk.choices[0].delta.content or "" for chunk in chunks
    )
    assert total_content == "5"

    # Last chunk has no content, but usage and stop_reason
    assert chunks[-1].choices[0].delta.content is None
    assert chunks[-1].choices[0].finish_reason == "stop"
    assert chunks[-1].usage
    assert chunks[-1].usage.total_tokens == 12
    assert chunks[-1].usage.prompt_tokens == 11
    assert chunks[-1].usage.completion_tokens == 1


def test_sync_streaming():
    client = get_client_mock(
        status_code=200,
        stream_chunks_mock=STREAM_CHUNKS_MOCK,
    )

    response = client.chat.completions.create(
        deployment_name="gpt-35-turbo",
        messages=[{"role": "user", "content": "2+3="}],
        stream=True,
    )
    assert isinstance(response, Iterable)
    chunks = [chunk for chunk in response]
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)


@pytest.mark.asyncio
async def test_async_streaming():
    async_client = get_async_client_mock(
        status_code=200,
        stream_chunks_mock=STREAM_CHUNKS_MOCK,
    )
    response = await async_client.chat.completions.create(
        deployment_name="gpt-35-turbo",
        messages=[{"role": "user", "content": "2+3="}],
        stream=True,
    )

    assert inspect.isasyncgen(response)
    chunks = [chunk async for chunk in response]
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)
