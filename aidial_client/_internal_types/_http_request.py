from io import BufferedReader
from typing import (
    IO,
    Any,
    Literal,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
    final,
)

from httpx import Timeout

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven

FileContent = Union[
    IO[bytes],
    bytes,
    str,
    # Somehow, pydantic doesn't recognize result of open('...', 'rb') as IO[bytes]
    # even though BufferedReader is a subclass of IO[bytes]
    BufferedReader,
]
FileTypes = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    Tuple[Optional[str], FileContent, Optional[str]],
    # (filename, file (or bytes), content_type, headers)
    Tuple[Optional[str], FileContent, Optional[str], Mapping[str, str]],
]

Params = Mapping[str, Any]
Headers = Mapping[str, Any]
Data = Mapping[str, Any]
RequestFiles = Union[Mapping[str, FileTypes], Sequence[Tuple[str, FileTypes]]]


@final
class FinalRequestOptions(BaseModel):
    class Config:
        arbitrary_types_allowed: bool = True

    method: Literal["GET", "PUT", "POST", "DELETE"]
    url: str
    params: Optional[Params] = None
    headers: Optional[Headers] = None
    max_retries: Union[int, NotGiven] = NOT_GIVEN
    timeout: Union[float, Timeout, NotGiven, None] = NOT_GIVEN
    files: Optional[RequestFiles] = None
    json_data: Optional[Data] = None

    def get_max_retries(self, max_retries: int) -> int:
        if isinstance(self.max_retries, NotGiven):
            return max_retries
        return self.max_retries

    def get_timeout(
        self, timeout: Union[float, Timeout, None]
    ) -> Union[float, Timeout, None]:
        if isinstance(self.timeout, NotGiven):
            return timeout
        return self.timeout
