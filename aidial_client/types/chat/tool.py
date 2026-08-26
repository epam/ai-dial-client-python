from typing import Any, Literal

from typing_extensions import Required, TypedDict

from aidial_client.types.chat.cache import CacheBreakpointParam
from aidial_client.types.chat.function import (
    FunctionCallParam,
    FunctionCallSpecParam,
    FunctionParam,
)


class ToolCustomFieldsParam(TypedDict, total=False):
    cache_breakpoint: CacheBreakpointParam | None


class ToolParam(TypedDict, total=False):
    type: Required[Literal["function"]]
    function: Required[FunctionParam]
    custom_fields: ToolCustomFieldsParam | None


class StaticFunctionParam(TypedDict, total=False):
    name: Required[str]
    description: str | None
    configuration: dict[str, Any] | None


class StaticToolParam(TypedDict):
    type: Literal["static_function"]
    static_function: StaticFunctionParam


class ToolCallParam(TypedDict):
    id: Required[str]
    type: Required[Literal["function"]]
    function: FunctionCallParam


class ToolCallSpecParam(TypedDict, total=False):
    type: Required[Literal["function"]]
    function: FunctionCallSpecParam
