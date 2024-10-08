from typing import Type, cast

import httpx

from aidial_client._exception import ParsingDataException
from aidial_client._internal_types._generic import NoneType, ResponseT
from aidial_client._internal_types._model import (
    ExtraAllowModel,
    ExtraForbidModel,
)


def default_process_non_stream(
    cast_to: Type[ResponseT], response: httpx.Response
) -> ResponseT:
    if cast_to == httpx.Response:
        return cast(ResponseT, response)
    elif cast_to == bytes:
        return cast(ResponseT, response.content)
    elif cast_to == str:
        return cast(ResponseT, response.text)
    elif cast_to == NoneType:
        return cast(ResponseT, None)
    elif issubclass(cast_to, ExtraForbidModel) or issubclass(
        cast_to, ExtraAllowModel
    ):
        try:
            data = response.json()
            return cast_to(**data)
        except Exception as e:
            raise ParsingDataException(
                message=f"Error during parsing of response data: {str(e)}"
            )
    else:
        raise NotImplementedError("This cast_to type is not supported yet")
