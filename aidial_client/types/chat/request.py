from typing import Any, Literal

from typing_extensions import TypedDict

from aidial_client.types.chat.addon import Addon
from aidial_client.types.chat.function import (
    FunctionCallSpecParam,
    FunctionParam,
)
from aidial_client.types.chat.request_param import Message, ResponseFormat
from aidial_client.types.chat.tool import ToolCallSpecParam, ToolParam


class ChatCompletionRequestCustomFields(TypedDict, total=False):
    configuration: dict[str, Any] | None


class ChatCompletionRequest(TypedDict, total=False):
    model: str
    temperature: float | None
    top_p: float | None
    stream: bool | None
    stop: str | list[str] | None
    max_tokens: int | None
    presence_penalty: float | None
    frequency_penalty: float | None
    logit_bias: dict | None
    user: str | None
    messages: list[Message]
    data_sources: list[Any]
    n: int | None
    seed: int | None
    logprobs: bool | None
    top_logprobs: float | None
    response_format: ResponseFormat | None
    tools: list[ToolParam] | None
    tool_choice: Literal["none", "auto"] | ToolCallSpecParam | None
    functions: list[FunctionParam] | None
    function_call: Literal["none", "auto"] | FunctionCallSpecParam | None
    addons: Addon | None
    max_prompt_tokens: Literal["infinity"] | int | None
    custom_fields: ChatCompletionRequestCustomFields | None
