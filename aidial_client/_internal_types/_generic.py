from typing import TypeVar, Union

import httpx

from aidial_client._internal_types._model import (
    ExtraAllowModel,
    ExtraForbidModel,
)
from aidial_client.types.file import FileDownloadResponse

ResponseT = TypeVar(
    "ResponseT",
    bound=Union[
        ExtraAllowModel,
        ExtraForbidModel,
        bytes,
        str,
        httpx.Response,
        FileDownloadResponse,
        None,
    ],
)
NoneType = type(None)
