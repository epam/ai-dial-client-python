from typing import Literal

from typing_extensions import Required, TypedDict

from aidial_client.types.chat.function import (
    FunctionCallParam,
    FunctionCallSpecParam,
    FunctionParam,
)


class ToolParam(TypedDict):
    type: Literal["function"]
    function: FunctionParam


class ToolCallParam(TypedDict):
    id: Required[str]
    type: Required[Literal["function"]]
    function: FunctionCallParam


class ToolCallSpecParam(TypedDict, total=False):
    type: Required[Literal["function"]]
    function: FunctionCallSpecParam
