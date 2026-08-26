from typing import Any, Literal

from typing_extensions import Required, TypedDict

from aidial_client.types.chat.cache import (
    CacheBreakpointParam,
    PromptCacheBreakpointParam,
)
from aidial_client.types.chat.function import FunctionCallParam
from aidial_client.types.chat.tool import ToolCallParam


class ResponseFormatText(TypedDict):
    type: Literal["text"]


class ResponseFormatJsonObject(TypedDict):
    type: Literal["json_object"]


class ResponseFormatJsonSchemaObject(TypedDict, total=False):
    name: Required[str]
    schema: Required[dict[str, Any]]
    description: str | None
    strict: bool | None


class ResponseFormatJsonSchema(TypedDict):
    type: Literal["json_schema"]
    json_schema: ResponseFormatJsonSchemaObject


ResponseFormat = (
    ResponseFormatText | ResponseFormatJsonObject | ResponseFormatJsonSchema
)


class AttachmentParam(TypedDict, total=False):
    type: str
    title: str
    data: str
    url: str
    reference_type: str
    reference_url: str


class StageParam(TypedDict, total=False):
    name: Required[str]
    status: Required[Literal["completed", "failed"]]
    content: str | None
    attachments: list[AttachmentParam] | None


class CustomContentParam(TypedDict, total=False):
    stages: list[StageParam] | None
    attachments: list[AttachmentParam] | None
    state: dict | None
    form_value: Any | None
    form_schema: Any | None


class MessageCustomFieldsParam(TypedDict, total=False):
    cache_breakpoint: CacheBreakpointParam | None


class MessageContentTextPartParam(TypedDict, total=False):
    type: Required[Literal["text"]]
    text: Required[str]
    prompt_cache_breakpoint: PromptCacheBreakpointParam | None


class ImageURLParam(TypedDict, total=False):
    url: Required[str]
    detail: Literal["auto", "low", "high"] | None


class MessageContentImagePartParam(TypedDict, total=False):
    type: Required[Literal["image_url"]]
    image_url: Required[ImageURLParam]
    prompt_cache_breakpoint: PromptCacheBreakpointParam | None


class InputFileParam(TypedDict, total=False):
    file_data: str | None
    file_id: str | None
    filename: str | None


class MessageContentFilePartParam(TypedDict, total=False):
    type: Required[Literal["file"]]
    file: Required[InputFileParam]
    prompt_cache_breakpoint: PromptCacheBreakpointParam | None


class InputAudioParam(TypedDict):
    data: str
    """Either "wav", "mp3" or any other format supported by the model"""
    format: str


class MessageContentAudioPartParam(TypedDict, total=False):
    type: Required[Literal["input_audio"]]
    input_audio: Required[InputAudioParam]
    prompt_cache_breakpoint: PromptCacheBreakpointParam | None


class MessageContentRefusalPartParam(TypedDict):
    type: Literal["refusal"]
    refusal: str


MessageContentPartParam = (
    MessageContentTextPartParam
    | MessageContentImagePartParam
    | MessageContentFilePartParam
    | MessageContentAudioPartParam
    | MessageContentRefusalPartParam
)

MessageContentParam = str | list[MessageContentPartParam]


class SystemMessageParam(TypedDict, total=False):
    role: Required[Literal["system"]]
    content: Required[MessageContentParam]
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None
    name: str | None


class DeveloperMessageParam(TypedDict, total=False):
    role: Required[Literal["developer"]]
    content: Required[MessageContentParam]
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None
    name: str | None


class UserMessageParam(TypedDict, total=False):
    role: Required[Literal["user"]]
    content: Required[MessageContentParam]
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None
    name: str | None


class AssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    content: MessageContentParam | None
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None
    function_call: FunctionCallParam | None
    tool_calls: list[ToolCallParam]
    refusal: str | None
    name: str | None


class ToolMessageParam(TypedDict, total=False):
    role: Required[Literal["tool"]]
    content: Required[MessageContentParam]
    tool_call_id: Required[str]
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None


class FunctionMessageParam(TypedDict, total=False):
    role: Required[Literal["function"]]
    content: Required[MessageContentParam]
    """Name of function call"""
    name: Required[str]
    custom_content: CustomContentParam | None
    custom_fields: MessageCustomFieldsParam | None


Message = (
    SystemMessageParam
    | DeveloperMessageParam
    | UserMessageParam
    | AssistantMessageParam
    | ToolMessageParam
    | FunctionMessageParam
)
