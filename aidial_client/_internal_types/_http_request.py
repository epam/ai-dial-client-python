from collections.abc import Mapping, Sequence
from io import BufferedReader
from typing import (
    IO,
    Any,
    Literal,
    final,
)

from httpx import Timeout

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven

FileContent = (
    IO[bytes]
    | bytes
    | str
    # Somehow, pydantic doesn't recognize result of open('...', 'rb')
    # as IO[bytes] even though BufferedReader is a subclass of IO[bytes]
    | BufferedReader
)
FileTypes = (
    # file (or bytes)
    FileContent
    # (filename, file (or bytes))
    | tuple[str | None, FileContent]
    # (filename, file (or bytes), content_type)
    | tuple[str | None, FileContent, str | None]
    # (filename, file (or bytes), content_type, headers)
    | tuple[str | None, FileContent, str | None, Mapping[str, str]]
)

Params = Mapping[str, Any]
Headers = Mapping[str, Any]
Data = Mapping[str, Any]
RequestFiles = Mapping[str, FileTypes] | Sequence[tuple[str, FileTypes]]


@final
class FinalRequestOptions(BaseModel):
    class Config:
        arbitrary_types_allowed: bool = True

    method: Literal["GET", "PUT", "POST", "DELETE"]
    url: str
    params: Params | None = None
    headers: Headers | None = None
    max_retries: int | NotGiven = NOT_GIVEN
    timeout: float | Timeout | NotGiven | None = NOT_GIVEN
    files: RequestFiles | None = None
    json_data: Data | None = None

    def get_max_retries(self, max_retries: int) -> int:
        if isinstance(self.max_retries, NotGiven):
            return max_retries
        return self.max_retries

    def get_timeout(
        self, timeout: float | Timeout | None
    ) -> float | Timeout | None:
        if isinstance(self.timeout, NotGiven):
            return timeout
        return self.timeout
