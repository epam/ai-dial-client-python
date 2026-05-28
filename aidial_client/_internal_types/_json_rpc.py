from typing import Any, Dict, List, Literal, Optional, Union

from aidial_client._compatibility.pydantic_v1 import (
    BaseModel,
    Extra,
    Field,
    root_validator,
)


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
    jsonrpc: Literal["2.0"]
    result: Optional[Any] = None
    error: Optional[JsonRpcError] = None
    id: Optional[Union[int, str]] = Field(...)

    class Config:
        smart_union = True
        extra = Extra.allow

    @root_validator(pre=True)
    def _validate_result_xor_error(cls, values):
        """Per JSON-RPC 2.0 (https://www.jsonrpc.org/specification#response_object),
        either ``result`` or ``error`` MUST be included (presence-wise — ``null``
        is a valid result value), and both MUST NOT be included.
        """
        if not isinstance(values, dict):
            return values
        has_result = "result" in values
        has_error = "error" in values
        if has_result and has_error:
            raise ValueError(
                "JSON-RPC response must not contain both 'result' and 'error'"
            )
        if not has_result and not has_error:
            raise ValueError(
                "JSON-RPC response must contain either 'result' or 'error'"
            )
        return values


class JsonRpcResponses(BaseModel):
    """Pydantic root model that accepts a single JSON-RPC response object or
    a batch array, normalizing both to a list via the ``responses`` property.
    """

    __root__: Union[JsonRpcResponse, List[JsonRpcResponse]]

    class Config:
        smart_union = True

    @property
    def responses(self) -> List[JsonRpcResponse]:
        if isinstance(self.__root__, list):
            return self.__root__
        return [self.__root__]
