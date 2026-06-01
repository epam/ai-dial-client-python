from typing import Literal, Union

from typing_extensions import Required, TypedDict

from aidial_client.types.chat.function import FunctionCallParam
from aidial_client.types.chat.tool import ToolCallParam


class ResponseFormat(TypedDict, total=False):
    type: Literal["json_object", "text"]


class AttachmentParam(TypedDict, total=False):
    type: str
    title: str
    data: str
    url: str
    reference_type: str
    reference_url: str


class CustomContentParam(TypedDict, total=False):
    attachments: list[AttachmentParam] | None
    state: dict | None


class SystemMessageParam(TypedDict, total=False):
    role: Required[Literal["system"]]
    content: Required[str]
    custom_content: CustomContentParam | None
    name: str | None


class UserMessageParam(TypedDict, total=False):
    role: Required[Literal["user"]]
    content: Required[str]
    custom_content: CustomContentParam | None
    name: str | None


class AssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    content: str | None
    custom_content: CustomContentParam | None
    function_call: FunctionCallParam | None
    tool_calls: list[ToolCallParam]
    name: str | None


class ToolMessageParam(TypedDict, total=False):
    role: Required[Literal["tool"]]
    content: Required[str]
    tool_call_id: Required[str]


class FunctionMessageParam(TypedDict, total=False):
    role: Required[Literal["function"]]
    content: Required[str]
    """Name of function call"""
    name: Required[str]


Message = Union[
    SystemMessageParam,
    UserMessageParam,
    AssistantMessageParam,
    ToolMessageParam,
    FunctionMessageParam,
]
