from typing import Dict, List, Literal, Optional, Union

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
    attachments: Optional[List[AttachmentParam]]
    state: Optional[Dict]


class SystemMessageParam(TypedDict, total=False):
    role: Required[Literal["system"]]
    content: Required[str]
    custom_content: Optional[CustomContentParam]
    name: Optional[str]


class UserMessageParam(TypedDict, total=False):
    role: Required[Literal["user"]]
    content: Required[str]
    custom_content: Optional[CustomContentParam]
    name: Optional[str]


class AssistantMessageParam(TypedDict, total=False):
    role: Required[Literal["assistant"]]
    content: Optional[str]
    custom_content: Optional[CustomContentParam]
    function_call: Optional[FunctionCallParam]
    tool_calls: List[ToolCallParam]
    name: Optional[str]


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
