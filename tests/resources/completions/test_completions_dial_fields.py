"""DIAL-specific chat completion request and response fields"""

from typing import Any

import pytest

from tests.resources.completions.conftest import (
    GetCompletion,
    GetMessage,
    GetRequestBody,
)

pytestmark = pytest.mark.asyncio

_STAGE = {
    "index": 0,
    "name": "Thinking",
    "status": "completed",
    "content": "...",
    "attachments": [{"index": 0, "url": "http://a.com", "title": "Source"}],
}

_FORM_SCHEMA = {"type": "object", "properties": {"city": {"type": "string"}}}
_FORM_VALUE = {"city": "Paris"}
_STATE = {"thread_id": "42", "step": 2}

_USAGE_PER_MODEL = [
    {
        "index": 0,
        "model": "gpt-4o",
        "prompt_tokens": 11,
        "completion_tokens": 1,
        "total_tokens": 12,
    }
]
_DISCARDED_MESSAGES = [0, 1]

_REQUEST_PARAMS: dict[str, Any] = {
    "tools": [
        {
            "type": "function",
            "function": {"name": "f", "parameters": {}, "strict": True},
            "custom_fields": {"cache_breakpoint": {"expire_at": "1h"}},
        },
        {
            "type": "static_function",
            "static_function": {"name": "s", "configuration": {"a": 1}},
        },
    ],
    "tool_choice": "required",
    "parallel_tool_calls": False,
    "max_completion_tokens": 100,
    "max_prompt_tokens": 200,
    "reasoning_effort": "minimal",
    "response_format": {
        "type": "json_schema",
        "json_schema": {"name": "res", "schema": {"type": "object"}},
    },
    "stream_options": {"include_usage": True},
    "custom_fields": {
        "configuration": {"a": 1},
        "cache_breakpoint": {"expire_at": "5m"},
    },
}

_MESSAGES: list[Any] = [
    {
        "role": "developer",
        "content": "Be brief",
        "custom_fields": {"cache_breakpoint": {"expire_at": "1h"}},
    },
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "What is on the picture?"},
            {
                "type": "image_url",
                "image_url": {"url": "http://a.com/b.png", "detail": "low"},
            },
        ],
        "custom_content": {
            "attachments": [{"type": "image/png", "url": "b.png"}]
        },
    },
]


class TestRequestFields:
    """DIAL-specific request fields must reach the request body as-is"""

    @pytest.mark.parametrize("param", list(_REQUEST_PARAMS))
    async def test_request_param(
        self, get_request_body: GetRequestBody, param: str
    ):
        body = await get_request_body(messages=_MESSAGES, **_REQUEST_PARAMS)

        assert body[param] == _REQUEST_PARAMS[param]

    async def test_request_messages(self, get_request_body: GetRequestBody):
        body = await get_request_body(messages=_MESSAGES, **_REQUEST_PARAMS)

        assert body["messages"] == _MESSAGES


class TestCustomContent:
    async def test_response_stages(self, get_message: GetMessage):
        message = await get_message(custom_content={"stages": [_STAGE]})

        assert message.custom_content and message.custom_content.stages
        stage = message.custom_content.stages[0]
        assert stage.model_dump(exclude_none=True) == _STAGE

    async def test_response_form_schema(self, get_message: GetMessage):
        message = await get_message(
            custom_content={"form_schema": _FORM_SCHEMA}
        )

        assert message.custom_content
        assert message.custom_content.form_schema == _FORM_SCHEMA

    async def test_response_form_value(self, get_message: GetMessage):
        message = await get_message(custom_content={"form_value": _FORM_VALUE})

        assert message.custom_content
        assert message.custom_content.form_value == _FORM_VALUE

    async def test_response_state(self, get_message: GetMessage):
        message = await get_message(custom_content={"state": _STATE})

        assert message.custom_content
        assert message.custom_content.state == _STATE


class TestStatistics:
    async def test_response_usage_per_model(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            statistics={"usage_per_model": _USAGE_PER_MODEL}
        )

        assert completion.statistics and completion.statistics.usage_per_model
        assert [
            usage.model_dump(exclude_none=True)
            for usage in completion.statistics.usage_per_model
        ] == _USAGE_PER_MODEL

    async def test_response_discarded_messages(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            statistics={"discarded_messages": _DISCARDED_MESSAGES}
        )

        assert completion.statistics
        assert completion.statistics.discarded_messages == _DISCARDED_MESSAGES
