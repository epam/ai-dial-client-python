import pytest

from aidial_client.types.chat import ChatCompletionChunk
from tests.client_mock import get_async_client_mock, get_client_mock
from tests.utils.chunks import create_mock_chunk, create_sse_data_field
from tests.utils.completions import DIAL_MODEL

_STREAM_CHUNKS_MOCK: list[bytes] = [
    create_sse_data_field(
        create_mock_chunk(delta={"content": "", "role": "assistant"})
    )
    + create_sse_data_field(create_mock_chunk(delta={"content": "5"})),
    create_sse_data_field(
        create_mock_chunk(
            finish_reason="stop",
            usage={
                "completion_tokens": 1,
                "prompt_tokens": 11,
                "total_tokens": 12,
            },
        )
    ),
]


def _validate_chunks(chunks: list[ChatCompletionChunk]):
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
        stream_chunks_mock=_STREAM_CHUNKS_MOCK,
    )

    response = client.chat.completions.create(
        deployment_name=DIAL_MODEL,
        messages=[{"role": "user", "content": "2+3="}],
        stream=True,
    )
    chunks = list(response)
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)


@pytest.mark.asyncio
async def test_async_streaming():
    async_client = get_async_client_mock(
        status_code=200,
        stream_chunks_mock=_STREAM_CHUNKS_MOCK,
    )
    response = await async_client.chat.completions.create(
        deployment_name=DIAL_MODEL,
        messages=[{"role": "user", "content": "2+3="}],
        stream=True,
    )

    chunks = [chunk async for chunk in response]
    assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)
    _validate_chunks(chunks)
