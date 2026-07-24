from typing import cast

import httpx

from aidial_client._exception import ParsingDataError
from aidial_client._internal_types._generic import NoneType, ResponseT
from aidial_client._internal_types._model import (
    ExtraAllowModel,
    ExtraForbidModel,
)


def process_block_response(
    cast_to: type[ResponseT], response: httpx.Response
) -> ResponseT:
    if cast_to == httpx.Response:
        return cast(ResponseT, response)
    elif cast_to is bytes:
        return cast(ResponseT, response.content)
    elif cast_to is str:
        return cast(ResponseT, response.text)
    elif cast_to == NoneType:
        return cast(ResponseT, None)
    elif cast_to is dict:
        try:
            return cast(ResponseT, response.json())
        except Exception as e:
            raise ParsingDataError(
                message=f"Error during parsing of response data: {str(e)}"
            )
    elif issubclass(cast_to, ExtraForbidModel | ExtraAllowModel):
        try:
            data = response.json()
            return cast_to(**data)
        except Exception as e:
            raise ParsingDataError(
                message=f"Error during parsing of response data: {str(e)}"
            )
    else:
        raise NotImplementedError("This cast_to type is not supported.")
