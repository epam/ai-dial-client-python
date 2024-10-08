import uuid
from time import time
from typing import AsyncIterator, Iterator, Union

import openai
from openai.types.chat import ChatCompletion as OpenAIChatCompletion
from openai.types.chat import ChatCompletionChunk as OpenAIChatCompletionChunk

from aidial_client._exception import DialException
from aidial_client.types.chat import ChatCompletionChunk, ChatCompletionResponse


def convert_openai_error(
    error: Union[openai.APIError, openai.APIStatusError],
) -> DialException:
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
    response_id = None
    try:
        for chunk in openai_response:
            response_id = chunk.id
            yield ChatCompletionChunk(**chunk.model_dump())
    except openai.APIError as e:
        yield ChatCompletionChunk(
            id=response_id or str(uuid.uuid4()),
            object="chat.completion.chunk",
            choices=[],
            created=int(time.time()),
            model=None,
            usage=None,
            error=convert_openai_error(e).json_error(),
        )


async def convert_openai_async_stream(
    openai_response: AsyncIterator[OpenAIChatCompletionChunk],
) -> AsyncIterator[ChatCompletionChunk]:
    response_id = None
    try:
        async for chunk in openai_response:
            response_id = chunk.id
            yield ChatCompletionChunk(**chunk.model_dump())
    except openai.APIError as e:
        yield ChatCompletionChunk(
            id=response_id or str(uuid.uuid4()),
            object="chat.completion.chunk",
            choices=[],
            created=int(time.time()),
            model=None,
            usage=None,
            error=convert_openai_error(e).json_error(),
        )
