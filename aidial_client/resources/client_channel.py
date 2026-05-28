import json
from http import HTTPStatus
from typing import Any, List, Union

import httpx

from aidial_client._compatibility.pydantic_v1 import ValidationError
from aidial_client._exception import (
    DialException,
    InvalidRequestError,
    ParsingDataError,
)
from aidial_client._http_client._sse import aiter_data_events, iter_data_events
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.client_channel import JsonRpcRequest, JsonRpcResponse

CLIENT_CHANNEL_HEADER = "X-DIAL-CLIENT-CHANNEL-ID"
_INTERACT_URL = "v1/ops/client-channel/interact"


def _serialize(
    request: Union[JsonRpcRequest, List[JsonRpcRequest]],
) -> Any:
    requests = request if isinstance(request, list) else [request]
    for r in requests:
        if r.id is None:
            raise InvalidRequestError(
                "JsonRpcRequest.id is required for client_channel.interact(): "
                "a request without an id is a JSON-RPC notification, which the "
                "server does not respond to — the call would block until the "
                "stream closes."
            )
    if isinstance(request, list):
        return [r.dict(exclude_none=True) for r in request]
    return request.dict(exclude_none=True)


def _parse_responses(payload: str) -> List[JsonRpcResponse]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as err:
        raise ParsingDataError(
            message=f"Malformed JSON in client-channel interact response: {err}"
        ) from err
    items = data if isinstance(data, list) else [data]
    parsed: List[JsonRpcResponse] = []
    for item in items:
        if not isinstance(item, dict):
            raise ParsingDataError(
                message=(
                    "Invalid JSON-RPC response in client-channel interact: "
                    f"expected object, got {type(item).__name__}"
                )
            )
        try:
            response = JsonRpcResponse(**item)
        except (TypeError, ValidationError) as err:
            raise ParsingDataError(
                message=(
                    "Invalid JSON-RPC response in client-channel interact: "
                    f"{err}"
                )
            ) from err
        if response.result is None and response.error is None:
            raise ParsingDataError(
                message=(
                    "Invalid JSON-RPC response in client-channel interact: "
                    "must contain either 'result' or 'error'"
                )
            )
        parsed.append(response)
    return parsed


def _no_data_error() -> DialException:
    return DialException(
        message="Client-channel interact stream closed without a data event",
        status_code=HTTPStatus.GATEWAY_TIMEOUT,
    )


class ClientChannel(Resource):
    def interact(
        self,
        *,
        channel_id: str,
        request: Union[JsonRpcRequest, List[JsonRpcRequest]],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> List[JsonRpcResponse]:
        """Send a JSON-RPC request (or batch) over the client channel and
        wait for the corresponding response event.

        Returns a list of ``JsonRpcResponse``. The wire response preserves the
        server-emitted order, which is not guaranteed to match request order;
        callers should correlate each response with its request via the
        ``id`` field, not by positional index.

        Raises ``DialException`` if the HTTP status is not 2xx, the stream
        closes without a response, or a transport error (timeout, network
        failure) occurs. Raises ``InvalidRequestError`` if any request has
        ``id=None`` (JSON-RPC notifications are not supported here — the
        server does not respond to them).
        """
        with self.http_client.stream_sse(
            method="POST",
            url=_INTERACT_URL,
            json_data=_serialize(request),
            headers={CLIENT_CHANNEL_HEADER: channel_id},
            timeout=timeout,
        ) as response:
            for payload in iter_data_events(response.iter_lines()):
                return _parse_responses(payload)
        raise _no_data_error()


class AsyncClientChannel(AsyncResource):
    async def interact(
        self,
        *,
        channel_id: str,
        request: Union[JsonRpcRequest, List[JsonRpcRequest]],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> List[JsonRpcResponse]:
        async with self.http_client.stream_sse(
            method="POST",
            url=_INTERACT_URL,
            json_data=_serialize(request),
            headers={CLIENT_CHANNEL_HEADER: channel_id},
            timeout=timeout,
        ) as response:
            async for payload in aiter_data_events(response.aiter_lines()):
                return _parse_responses(payload)
        raise _no_data_error()
