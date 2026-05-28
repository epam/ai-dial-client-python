from http import HTTPStatus
from typing import Any, List, Optional, Sequence, Union

import httpx

from aidial_client._compatibility.pydantic_v1 import ValidationError
from aidial_client._exception import (
    DialException,
    InvalidRequestError,
    ParsingDataError,
)
from aidial_client._http_client._sse import aiter_data_events, iter_data_events
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven
from aidial_client._internal_types._json_rpc import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcResponses,
)
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.client_channel import SigninResult

_CLIENT_CHANNEL_HEADER = "X-DIAL-CLIENT-CHANNEL-ID"
_INTERACT_URL = "v1/ops/client-channel/interact"
_SIGNIN_METHOD = "toolset/signin"


def _normalize_toolset_ids(toolset_ids: Sequence[str]) -> List[str]:
    """Validate ``toolset_ids`` and return a stable list.

    Catches three caller mistakes that would otherwise produce silent garbage:
    a single string (str is itself a ``Sequence[str]``), a one-shot iterable
    (consumed by the build step, leaving the mapping step with nothing), and
    duplicate ids (the per-toolset result dict cannot represent two outcomes
    for the same key).
    """
    if isinstance(toolset_ids, str):
        raise InvalidRequestError(
            "toolset_ids must be a sequence of toolset ids, not a single str"
        )
    materialized = list(toolset_ids)
    if len(set(materialized)) != len(materialized):
        raise InvalidRequestError("toolset_ids must not contain duplicates")
    return materialized


def _serialize_requests(requests: Sequence[JsonRpcRequest]) -> Any:
    """Serialize a sequence of JsonRpcRequest to the wire form.

    Always emits an array. DIAL Core accepts both an object and an array
    body, but emitting a consistent shape avoids the "wire shape depends
    on count" footgun and keeps the empty-input case safe.
    """
    return [r.dict(exclude_none=True) for r in requests]


def _parse_responses(payload: str) -> List[JsonRpcResponse]:
    try:
        return JsonRpcResponses.parse_raw(payload).responses
    except (ValidationError, ValueError) as err:
        raise ParsingDataError(
            message=(
                "Invalid JSON-RPC response in client-channel interact: "
                f"{err}"
            )
        ) from err


def _no_data_error() -> DialException:
    return DialException(
        message="Client-channel interact stream closed without a data event",
        status_code=HTTPStatus.GATEWAY_TIMEOUT,
    )


def _raise_if_batch_error(responses: Sequence[JsonRpcResponse]) -> None:
    """Per JSON-RPC 2.0, a response with ``id=null`` indicates the server
    could not associate the response with any request (parse error, invalid
    batch, etc.). Surface that as a ``DialException`` instead of silently
    mapping every toolset to ERROR.
    """
    for r in responses:
        if r.id is None and r.error is not None:
            raise DialException(
                message=(
                    f"Server-level JSON-RPC error "
                    f"({r.error.code}): {r.error.message}"
                ),
                status_code=HTTPStatus.BAD_GATEWAY,
            )


_RESULT_TO_OUTCOME = {
    SigninResult.SUCCESS.value: SigninResult.SUCCESS,
    SigninResult.DENIED.value: SigninResult.DENIED,
}


def _outcome_for(response: Optional[JsonRpcResponse]) -> SigninResult:
    if response is None or response.error is not None:
        return SigninResult.ERROR
    if not isinstance(response.result, str):
        return SigninResult.ERROR
    return _RESULT_TO_OUTCOME.get(response.result, SigninResult.ERROR)


def _build_signin_requests(
    toolset_ids: Sequence[str],
) -> List[JsonRpcRequest]:
    return [
        JsonRpcRequest(
            method=_SIGNIN_METHOD,
            params={"toolsetId": tid},
            id=str(idx),
        )
        for idx, tid in enumerate(toolset_ids, start=1)
    ]


def _map_signin_results(
    toolset_ids: Sequence[str],
    responses: Sequence[JsonRpcResponse],
) -> "dict[str, SigninResult]":
    by_id = {str(r.id): r for r in responses if r.id is not None}
    return {
        tid: _outcome_for(by_id.get(str(idx)))
        for idx, tid in enumerate(toolset_ids, start=1)
    }


class ClientChannel(Resource):
    def signin_toolsets(
        self,
        *,
        channel_id: str,
        toolset_ids: Sequence[str],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> "dict[str, SigninResult]":
        """Request interactive sign-in for one or more toolsets on the given
        client channel and return the per-toolset outcome.

        ``toolset_ids`` are typically DIAL toolset ids (e.g.
        ``"toolsets/public/my-toolset"``). The returned dict has one entry
        per input id; toolsets for which the server does not produce a
        response are mapped to :class:`SigninResult.ERROR`. Iteration order
        of the returned dict matches the order of ``toolset_ids``.

        Raises :class:`InvalidRequestError` if ``toolset_ids`` is a plain
        string or contains duplicates. Raises :class:`DialException` on HTTP
        errors, transport failures, server-level JSON-RPC errors (e.g. parse
        error returned with ``id=null``), or if the SSE stream closes
        without a response event.
        """
        ids = _normalize_toolset_ids(toolset_ids)
        if not ids:
            return {}
        responses = self._interact(
            channel_id=channel_id,
            requests=_build_signin_requests(ids),
            timeout=timeout,
        )
        _raise_if_batch_error(responses)
        return _map_signin_results(ids, responses)

    def _interact(
        self,
        *,
        channel_id: str,
        requests: Sequence[JsonRpcRequest],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> List[JsonRpcResponse]:
        with self.http_client.stream_sse(
            method="POST",
            url=_INTERACT_URL,
            json_data=_serialize_requests(requests),
            headers={_CLIENT_CHANNEL_HEADER: channel_id},
            timeout=timeout,
        ) as response:
            for payload in iter_data_events(response.iter_lines()):
                return _parse_responses(payload)
        raise _no_data_error()


class AsyncClientChannel(AsyncResource):
    async def signin_toolsets(
        self,
        *,
        channel_id: str,
        toolset_ids: Sequence[str],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> "dict[str, SigninResult]":
        ids = _normalize_toolset_ids(toolset_ids)
        if not ids:
            return {}
        responses = await self._interact(
            channel_id=channel_id,
            requests=_build_signin_requests(ids),
            timeout=timeout,
        )
        _raise_if_batch_error(responses)
        return _map_signin_results(ids, responses)

    async def _interact(
        self,
        *,
        channel_id: str,
        requests: Sequence[JsonRpcRequest],
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> List[JsonRpcResponse]:
        async with self.http_client.stream_sse(
            method="POST",
            url=_INTERACT_URL,
            json_data=_serialize_requests(requests),
            headers={_CLIENT_CHANNEL_HEADER: channel_id},
            timeout=timeout,
        ) as response:
            async for payload in aiter_data_events(response.aiter_lines()):
                return _parse_responses(payload)
        raise _no_data_error()
