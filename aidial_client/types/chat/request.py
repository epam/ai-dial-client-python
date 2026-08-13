from typing import Any, Literal

from typing_extensions import TypedDict

from aidial_client.types.chat.cache import CacheBreakpointParam
from aidial_client.types.chat.function import (
    FunctionCallSpecParam,
    FunctionParam,
)
from aidial_client.types.chat.request_param import Message, ResponseFormat
from aidial_client.types.chat.tool import (
    StaticToolParam,
    ToolCallSpecParam,
    ToolParam,
)

ReasoningEffort = Literal["none", "minimal", "low", "medium", "high"]


class StreamOptions(TypedDict, total=False):
    include_usage: bool | None


class ChatCompletionRequestCustomFields(TypedDict, total=False):
    configuration: dict[str, Any] | None
    cache_breakpoint: CacheBreakpointParam | None


class ChatCompletionRequest(TypedDict, total=False):
    model: str
    temperature: float | None
    top_p: float | None
    stream: bool | None
    stream_options: StreamOptions | None
    stop: str | list[str] | None
    max_tokens: int | None
    max_completion_tokens: int | None
    presence_penalty: float | None
    frequency_penalty: float | None
    logit_bias: dict | None
    user: str | None
    messages: list[Message]
    data_sources: list[Any]
    n: int | None
    seed: int | None
    logprobs: bool | None
    top_logprobs: int | None
    reasoning_effort: ReasoningEffort | None
    response_format: ResponseFormat | None
    tools: list[ToolParam | StaticToolParam] | None
    tool_choice: Literal["none", "auto", "required"] | ToolCallSpecParam | None
    parallel_tool_calls: bool | None
    functions: list[FunctionParam] | None
    function_call: Literal["none", "auto"] | FunctionCallSpecParam | None
    max_prompt_tokens: Literal["infinity"] | int | None
    custom_fields: ChatCompletionRequestCustomFields | None
