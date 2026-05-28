from typing import Any, Dict, List, Literal, Optional, Union

from aidial_client._compatibility.pydantic_v1 import BaseModel, Extra


class JsonRpcError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

    class Config:
        extra = Extra.allow


class JsonRpcRequest(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Optional[Union[List[Any], Dict[str, Any]]] = None
    id: Optional[Union[int, str]] = None

    class Config:
        smart_union = True


class JsonRpcResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None
    id: Optional[Union[int, str]] = None

    class Config:
        smart_union = True
        extra = Extra.allow
