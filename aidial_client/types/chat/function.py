from typing import Required

from typing_extensions import TypedDict


class FunctionParam(TypedDict, total=False):
    name: Required[str]
    description: str | None
    parameters: dict | None
    strict: bool | None


class FunctionCallParam(TypedDict):
    name: Required[str]
    arguments: Required[str]


class FunctionCallSpecParam(TypedDict):
    name: Required[str]
