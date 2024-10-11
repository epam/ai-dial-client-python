from typing import Dict, List, Literal, Optional, Union

from aidial_client._compatibility.pydantic_v1 import root_validator
from aidial_client._internal_types._model import ExtraAllowModel


class Attachment(ExtraAllowModel):
    type: Optional[str] = None
    title: Optional[str] = None
    data: Optional[str] = None
    url: Optional[str] = None
    reference_type: Optional[str] = None
    reference_url: Optional[str] = None

    @root_validator(pre=True)
    def validate_data_or_url(cls, values):
        if "data" not in values and "url" not in values:
            raise ValueError("Either data or url must be provided")
        return values


class CustomContent(ExtraAllowModel):
    attachments: Optional[List[Attachment]] = None
    state: Optional[Dict] = None


class CompletionUsage(ExtraAllowModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class FunctionCall(ExtraAllowModel):
    arguments: str
    name: str


class ChatCompletionMessageToolCall(ExtraAllowModel):
    id: str
    function: FunctionCall
    type: Literal["function"]


class ChatCompletionMessage(ExtraAllowModel):
    role: Literal["assistant"]
    content: Optional[str] = None
    custom_content: Optional[CustomContent] = None
    function_call: Optional[FunctionCall] = None
    tool_calls: Optional[List[ChatCompletionMessageToolCall]] = None


class Choice(ExtraAllowModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str]


class ChatCompletionResponse(ExtraAllowModel):
    id: str
    object: Literal["chat.completion"]
    choices: List[Choice]
    created: int
    model: Optional[str] = None
    usage: Optional[CompletionUsage] = None


class ChunkEmptyDelta(ExtraAllowModel):
    """
    Sometimes delta could be just empty, or have just content
    """

    content: Optional[str] = None
    object: Literal[None] = None
    tool_calls: Literal[None] = None
    role: Literal[None] = None


class ChoiceDelta(ExtraAllowModel):
    index: int
    delta: Union[ChatCompletionMessage, ChunkEmptyDelta]
    finish_reason: Optional[str] = None


class ChatCompletionChunk(ExtraAllowModel):
    id: str
    object: Literal["chat.completion.chunk"]
    choices: List[ChoiceDelta]
    created: int
    model: Optional[str] = None
    usage: Optional[CompletionUsage] = None
