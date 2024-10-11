from typing import AsyncIterator, Iterator

import openai
from openai.types.chat import ChatCompletion as OpenAIChatCompletion
from openai.types.chat import ChatCompletionChunk as OpenAIChatCompletionChunk

from aidial_client._exception import DialException
from aidial_client.types.chat import ChatCompletionChunk, ChatCompletionResponse


def convert_openai_error(error: openai.APIError) -> DialException:
    status_code = (
        error.status_code if isinstance(error, openai.APIStatusError) else 500
    )
    display_message = None
    if (
        hasattr(error, "body")
        and error.body is not None
        and isinstance(error.body, dict)
    ):
        display_message = error.body.get("display_message", None)
    return DialException(
        message=error.message,
        status_code=status_code,
        type=error.type,
        param=error.param,
        code=error.code,
        display_message=display_message,
    )


def convert_openai_response(
    openai_response: OpenAIChatCompletion,
) -> ChatCompletionResponse:
    return ChatCompletionResponse(**openai_response.model_dump())


def convert_openai_stream(
    openai_response: Iterator[OpenAIChatCompletionChunk],
) -> Iterator[ChatCompletionChunk]:
    try:
        for chunk in openai_response:
            yield ChatCompletionChunk(**chunk.model_dump())
    except openai.APIError as e:
        raise convert_openai_error(e) from e


async def convert_openai_async_stream(
    openai_response: AsyncIterator[OpenAIChatCompletionChunk],
) -> AsyncIterator[ChatCompletionChunk]:
    try:
        async for chunk in openai_response:
            yield ChatCompletionChunk(**chunk.model_dump())
    except openai.APIError as e:
        raise convert_openai_error(e) from e
