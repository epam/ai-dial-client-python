from typing import Any, Dict, List, Literal, Optional, Union

from typing_extensions import TypedDict

from aidial_client.types.chat.addon import Addon
from aidial_client.types.chat.function import (
    FunctionCallSpecParam,
    FunctionParam,
)
from aidial_client.types.chat.request_param import Message, ResponseFormat
from aidial_client.types.chat.tool import ToolCallSpecParam, ToolParam


class ChatCompletionRequestCustomFields(TypedDict, total=False):
    configuration: Optional[Dict[str, Any]]


class ChatCompletionRequest(TypedDict, total=False):
    model: str
    temperature: Optional[float]
    top_p: Optional[float]
    stream: Optional[bool]
    stop: Optional[Union[str, List[str]]]
    max_tokens: Optional[int]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    logit_bias: Optional[Dict]
    user: Optional[str]
    messages: List[Message]
    data_sources: List[Any]
    n: Optional[int]
    seed: Optional[int]
    logprobs: Optional[bool]
    top_logprobs: Optional[float]
    response_format: Optional[ResponseFormat]
    tools: Optional[List[ToolParam]]
    tool_choice: Optional[Union[Literal["none", "auto"], ToolCallSpecParam]]
    functions: Optional[List[FunctionParam]]
    function_call: Optional[
        Union[Literal["none", "auto"], FunctionCallSpecParam]
    ]
    addons: Optional[Addon]
    max_prompt_tokens: Optional[Union[Literal["infinity"], int]]
    custom_fields: Optional[ChatCompletionRequestCustomFields]
