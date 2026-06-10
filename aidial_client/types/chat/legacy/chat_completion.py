from collections.abc import Mapping
from enum import Enum
from typing import Any, Literal

from aidial_client._compatibility.pydantic_v1 import (
    ConstrainedFloat,
    ConstrainedInt,
    ConstrainedList,
    PositiveInt,
    StrictBool,
    StrictInt,
    StrictStr,
)
from aidial_client._internal_types._model import ExtraForbidModel


class FinishReason(str, Enum):
    STOP = "stop"
    LENGTH = "length"
    FUNCTION_CALL = "function_call"
    TOOL_CALLS = "tool_calls"
    CONTENT_FILTER = "content_filter"


class Status(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"


class Attachment(ExtraForbidModel):
    type: StrictStr | None = "text/markdown"
    title: StrictStr | None = None
    data: StrictStr | None = None
    url: StrictStr | None = None
    reference_type: StrictStr | None = None
    reference_url: StrictStr | None = None


class Stage(ExtraForbidModel):
    name: StrictStr
    status: Status
    content: StrictStr | None = None
    attachments: list[Attachment] | None = None


class CustomContent(ExtraForbidModel):
    stages: list[Stage] | None = None
    attachments: list[Attachment] | None = None
    state: Any | None = None


class FunctionCall(ExtraForbidModel):
    name: str
    arguments: str


class ToolCall(ExtraForbidModel):
    # OpenAI API doesn't strictly specify existence of the index field
    index: int | None
    id: StrictStr
    type: Literal["function"]
    function: FunctionCall


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class Message(ExtraForbidModel):
    role: Role
    content: StrictStr | None = None
    custom_content: CustomContent | None = None
    name: StrictStr | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: StrictStr | None = None
    function_call: FunctionCall | None = None


class Addon(ExtraForbidModel):
    name: StrictStr | None = None
    url: StrictStr | None = None


class Function(ExtraForbidModel):
    name: StrictStr
    description: StrictStr | None = None
    parameters: dict | None = None


class Temperature(ConstrainedFloat):
    ge = 0
    le = 2


class TopP(ConstrainedFloat):
    ge = 0
    le = 1


class N(ConstrainedInt):
    ge = 1
    le = 128


class Stop(ConstrainedList):
    max_items: int = 4
    __args__ = (StrictStr,)


class Penalty(ConstrainedFloat):
    ge = -2
    le = 2


class Tool(ExtraForbidModel):
    type: Literal["function"]
    function: Function


class FunctionChoice(ExtraForbidModel):
    name: StrictStr


class ToolChoice(ExtraForbidModel):
    type: Literal["function"]
    function: FunctionChoice


class ResponseFormat(ExtraForbidModel):
    type: Literal["text", "json_object"]


class AzureChatCompletionRequest(ExtraForbidModel):
    model: StrictStr | None = None
    messages: list[Message]
    functions: list[Function] | None = None
    function_call: Literal["auto", "none"] | FunctionChoice | None = None
    tools: list[Tool] | None = None
    tool_choice: Literal["auto", "none"] | ToolChoice | None = None
    stream: bool = False
    temperature: Temperature | None = None
    top_p: TopP | None = None
    n: N | None = None
    stop: StrictStr | Stop | None = None
    max_tokens: PositiveInt | None = None
    presence_penalty: Penalty | None = None
    frequency_penalty: Penalty | None = None
    logit_bias: Mapping[int, float] | None = None
    user: StrictStr | None = None
    seed: StrictInt | None = None
    logprobs: StrictBool | None = None
    top_logprobs: StrictInt | None = None
    response_format: ResponseFormat | None = None


class ChatCompletionRequestCustomFields(ExtraForbidModel):
    configuration: dict[str, Any] | None = None


class ChatCompletionRequest(AzureChatCompletionRequest):
    addons: list[Addon] | None = None
    max_prompt_tokens: PositiveInt | None = None
    custom_fields: ChatCompletionRequestCustomFields | None = None
