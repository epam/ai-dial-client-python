from typing import TypeVar

import httpx

from aidial_client._internal_types._model import (
    ExtraAllowModel,
    ExtraForbidModel,
)
from aidial_client.types.file import FileDownloadResponse

ResponseT = TypeVar(
    "ResponseT",
    bound=ExtraAllowModel
    | ExtraForbidModel
    | bytes
    | str
    | dict
    | httpx.Response
    | FileDownloadResponse
    | None,
)
NoneType = type(None)
