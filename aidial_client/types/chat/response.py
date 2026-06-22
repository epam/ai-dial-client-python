from typing import Literal

from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._compatibility.pydantic_v1 import root_validator
from aidial_client._internal_types._model import ExtraAllowModel

if PYDANTIC_V2:
    from pydantic import model_validator


class Attachment(ExtraAllowModel):
    type: str | None = None
    title: str | None = None
    data: str | None = None
    url: str | None = None
    reference_type: str | None = None
    reference_url: str | None = None

    if PYDANTIC_V2:

        @model_validator(mode="before")
        @classmethod
        def validate_data_or_url_v2(cls, values):
            if (
                isinstance(values, dict)
                and "data" not in values
                and "url" not in values
            ):
                raise ValueError("Either data or URL must be provided")
            return values

    else:

        @root_validator(pre=True)
        def validate_data_or_url_v1(cls, values):
            if "data" not in values and "url" not in values:
                raise ValueError("Either data or URL must be provided")
            return values


class CustomContent(ExtraAllowModel):
    attachments: list[Attachment] | None = None
    state: dict | None = None


class CompletionUsage(ExtraAllowModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class FunctionCall(ExtraAllowModel):
    arguments: str
    name: str


class FunctionCallDelta(ExtraAllowModel):
    arguments: str | None = None
    name: str | None = None


class ChatCompletionMessageToolCall(ExtraAllowModel):
    id: str
    function: FunctionCall
    type: Literal["function"]


class ToolCallDelta(ExtraAllowModel):
    index: int
    id: str | None = None
    function: FunctionCallDelta | None = None
    type: Literal["function"] | None = None


class ChatCompletionMessage(ExtraAllowModel):
    role: Literal["assistant"]
    content: str | None = None
    custom_content: CustomContent | None = None
    function_call: FunctionCall | None = None
    tool_calls: list[ChatCompletionMessageToolCall] | None = None


class ChatCompletionMessageDelta(ExtraAllowModel):
    role: Literal["assistant"] | None = None
    content: str | None = None
    custom_content: CustomContent | None = None
    function_call: FunctionCallDelta | None = None
    tool_calls: list[ToolCallDelta] | None = None


class Choice(ExtraAllowModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: str | None


class ChoiceDelta(ExtraAllowModel):
    index: int
    delta: ChatCompletionMessageDelta
    finish_reason: str | None = None


class ChatCompletionResponse(ExtraAllowModel):
    id: str
    object: Literal["chat.completion"]
    choices: list[Choice]
    created: int
    model: str | None = None
    usage: CompletionUsage | None = None


class ChatCompletionChunk(ExtraAllowModel):
    id: str
    object: Literal["chat.completion.chunk"]
    choices: list[ChoiceDelta]
    created: int
    model: str | None = None
    usage: CompletionUsage | None = None
