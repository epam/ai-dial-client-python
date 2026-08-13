"""
Fixtures running every test in 4 modes: sync/async and streaming/non-streaming.

The fixtures below are awaitable factories taking the fields of the mocked
response body (see `block_response`) and returning the parsed
completion/message, or - for `get_request_body` - the sent request body.
"""

import json
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
import pytest

from aidial_client.types.chat import (
    ChatCompletionMessage,
    ChatCompletionMessageDelta,
)
from tests.utils.completions import (
    Completion,
    block_response,
    create_completion,
    message_of,
)

GetCompletion = Callable[..., Awaitable[Completion]]
GetMessage = Callable[
    ..., Awaitable[ChatCompletionMessage | ChatCompletionMessageDelta]
]
GetRequestBody = Callable[..., Awaitable[dict[str, Any]]]


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def is_async(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture(params=[False, True], ids=["block", "stream"])
def stream(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture
def get_completion(is_async: bool, stream: bool) -> GetCompletion:
    async def _get(**response_fields: Any) -> Completion:
        return await create_completion(
            is_async=is_async,
            stream=stream,
            response=block_response(**response_fields),
        )

    return _get


@pytest.fixture
def get_message(get_completion: GetCompletion) -> GetMessage:
    async def _get(**response_fields: Any):
        return message_of(await get_completion(**response_fields))

    return _get


@pytest.fixture
def get_request_body(is_async: bool, stream: bool) -> GetRequestBody:
    async def _get(**request_params: Any) -> dict[str, Any]:
        sent_requests: list[httpx.Request] = []
        await create_completion(
            is_async=is_async,
            stream=stream,
            sent_requests=sent_requests,
            **request_params,
        )
        return json.loads(sent_requests[0].content)

    return _get
