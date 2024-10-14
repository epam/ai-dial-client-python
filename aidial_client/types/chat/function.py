from typing import Dict, Optional

from typing_extensions import Required, TypedDict


class FunctionParam(TypedDict, total=False):
    name: Required[str]
    description: Optional[str]
    parameters: Optional[Dict]


class FunctionCallParam(TypedDict):
    name: Required[str]
    arguments: Required[str]


class FunctionCallSpecParam(TypedDict):
    name: Required[str]
