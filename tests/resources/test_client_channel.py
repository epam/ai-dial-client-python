import json
import logging
from http import HTTPStatus
from typing import Any

import httpx
import pytest

from aidial_client import Dial, SigninResult
from aidial_client._client import AsyncDial
from aidial_client._exception import (
    DialException,
    InvalidRequestError,
    ParsingDataError,
)
from aidial_client._internal_types._json_rpc import JsonRpcRequest
from tests.client_mock import (
    MockStreamIterator,
    get_async_client_mock,
    get_client_mock,
)


def _sse_chunks(*lines: str) -> list[bytes]:
    """Encode a sequence of SSE lines as one byte stream chunk."""
    return [("\n".join(lines) + "\n").encode()]


def _data(payload: Any) -> str:
    return f"data: {json.dumps(payload)}"


def _single_event(payload: Any) -> list[bytes]:
    return _sse_chunks(_data(payload), "")


def _signin_response(id_: str, result: str) -> dict:
    return {"jsonrpc": "2.0", "id": id_, "result": result}


def _signin_error_response(id_: str, message: str = "boom") -> dict:
    return {
        "jsonrpc": "2.0",
        "id": id_,
        "error": {"code": -32000, "message": message},
    }


# ----------------------------------------------------------------------------
# signin_toolsets — happy paths
# ----------------------------------------------------------------------------


def test_signin_single_toolset_success_sync():
    client = get_client_mock(
        status_code=200,
        stream_chunks_mock=_single_event(_signin_response("1", "success")),
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["toolsets/public/a"]
    )
    assert out == {"toolsets/public/a": SigninResult.SUCCESS}


@pytest.mark.asyncio
async def test_signin_single_toolset_success_async():
    client = get_async_client_mock(
        status_code=200,
        stream_chunks_mock=_single_event(_signin_response("1", "success")),
    )
    out = await client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["toolsets/public/a"]
    )
    assert out == {"toolsets/public/a": SigninResult.SUCCESS}


def test_signin_batch_mixed_outcomes_sync():
    payload = [
        _signin_response("1", "success"),
        _signin_response("2", "denied"),
        _signin_error_response("3"),
    ]
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a", "b", "c"]
    )
    assert out == {
        "a": SigninResult.SUCCESS,
        "b": SigninResult.DENIED,
        "c": SigninResult.ERROR,
    }


@pytest.mark.asyncio
async def test_signin_batch_mixed_outcomes_async():
    payload = [
        _signin_response("1", "success"),
        _signin_response("2", "denied"),
    ]
    client = get_async_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = await client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a", "b"]
    )
    assert out == {"a": SigninResult.SUCCESS, "b": SigninResult.DENIED}


def test_signin_out_of_order_responses_matched_by_id_sync():
    # Server returns responses in arrival order, NOT request order.
    payload = [
        _signin_response("2", "denied"),
        _signin_response("1", "success"),
    ]
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a", "b"]
    )
    assert out == {"a": SigninResult.SUCCESS, "b": SigninResult.DENIED}


def test_signin_missing_response_for_toolset_maps_to_error_sync():
    payload = [_signin_response("1", "success")]
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a", "b"]
    )
    assert out == {"a": SigninResult.SUCCESS, "b": SigninResult.ERROR}


def test_signin_unknown_result_string_maps_to_error_sync():
    payload = [{"jsonrpc": "2.0", "id": "1", "result": "weird-value"}]
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a"]
    )
    assert out == {"a": SigninResult.ERROR}


def test_signin_empty_toolset_list_returns_empty_dict_sync():
    client = get_client_mock(status_code=200, stream_chunks_mock=[b""])
    out = client.client_channel.signin_toolsets(channel_id="ch", toolset_ids=[])
    assert out == {}


def test_signin_rejects_single_string_as_toolset_ids_sync():
    # A plain str satisfies Sequence[str] at runtime; reject explicitly so
    # it doesn't iterate the string and send one request per character.
    client = get_client_mock(status_code=200, stream_chunks_mock=[b""])
    with pytest.raises(InvalidRequestError):
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids="toolsets/public/x"
        )


def test_signin_rejects_duplicate_toolset_ids_sync():
    client = get_client_mock(status_code=200, stream_chunks_mock=[b""])
    with pytest.raises(InvalidRequestError):
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a", "a"]
        )


def test_signin_accepts_iterator_as_toolset_ids_sync():
    # A one-shot iterable would silently produce {} without materialization;
    # the wrapper must list() the input before using it twice.
    payload = [
        _signin_response("1", "success"),
        _signin_response("2", "denied"),
    ]
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(payload)
    )
    out = client.client_channel.signin_toolsets(
        channel_id="ch",
        toolset_ids=iter(["a", "b"]),  # type: ignore[arg-type]
    )
    assert out == {"a": SigninResult.SUCCESS, "b": SigninResult.DENIED}


def test_signin_batch_level_error_raises_dial_exception_sync():
    # Server-level JSON-RPC error: id=null with an error object (e.g. parse
    # error -32700). Must raise instead of silently mapping all toolsets
    # to SigninResult.ERROR.
    chunks = _single_event(
        {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
        }
    )
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(DialException) as exc_info:
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert "Parse error" in exc_info.value.message
    assert "-32700" in exc_info.value.message


# ----------------------------------------------------------------------------
# signin_toolsets — transport errors
# ----------------------------------------------------------------------------


def test_signin_no_data_event_raises_sync():
    chunks = _sse_chunks(": heartbeat", "", ": heartbeat", "")
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(DialException) as exc_info:
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert exc_info.value.status_code == HTTPStatus.GATEWAY_TIMEOUT


def test_signin_http_401_raises_with_message_sync():
    body = json.dumps({"error": {"message": "Unauthorized"}}).encode()
    client = get_client_mock(status_code=401, stream_chunks_mock=[body])
    with pytest.raises(DialException) as exc_info:
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"


@pytest.mark.asyncio
async def test_signin_http_401_raises_async():
    body = json.dumps({"error": {"message": "Unauthorized"}}).encode()
    client = get_async_client_mock(status_code=401, stream_chunks_mock=[body])
    with pytest.raises(DialException) as exc_info:
        await client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"


def test_signin_unknown_transport_error_wrapped_sync():
    client = get_client_mock(
        status_code=200, exception_mock=httpx.ConnectError("boom")
    )
    with pytest.raises(DialException) as exc_info:
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert "boom" in exc_info.value.message
    assert "Request failed" in exc_info.value.message


def test_signin_timeout_wrapped_sync():
    client = get_client_mock(
        status_code=200, exception_mock=httpx.ReadTimeout("slow")
    )
    with pytest.raises(DialException) as exc_info:
        client.client_channel.signin_toolsets(
            channel_id="ch", toolset_ids=["a"]
        )
    assert exc_info.value.status_code == HTTPStatus.REQUEST_TIMEOUT


# ----------------------------------------------------------------------------
# Wire-format checks
# ----------------------------------------------------------------------------


def test_signin_sends_channel_header_and_jsonrpc_body_sync():
    captured: dict = {}

    def send_mock(request: httpx.Request, **_kwargs):
        captured["request"] = request
        return httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(
                mock_chunks=_single_event(_signin_response("1", "success"))
            ),
        )

    client = Dial(api_key="dummy", base_url="http://dial.core")
    client._http_client._internal_http_client.send = send_mock

    client.client_channel.signin_toolsets(
        channel_id="my-channel", toolset_ids=["toolsets/public/x"]
    )

    request = captured["request"]
    assert request.headers["X-DIAL-CLIENT-CHANNEL-ID"] == "my-channel"
    assert request.headers["api-key"] == "dummy"
    assert request.url.path == "/v1/ops/client-channel/interact"
    body = json.loads(request.content)
    # Wire body is always an array, even for a single request.
    assert body == [
        {
            "jsonrpc": "2.0",
            "method": "toolset/signin",
            "params": {"toolsetId": "toolsets/public/x"},
            "id": "1",
        }
    ]


@pytest.mark.asyncio
async def test_signin_batch_body_serialized_as_array_async():
    captured: dict = {}

    async def send_mock(request: httpx.Request, **_kwargs):
        captured["request"] = request
        return httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(
                mock_chunks=_single_event(
                    [
                        _signin_response("1", "success"),
                        _signin_response("2", "success"),
                    ]
                )
            ),
        )

    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._http_client._internal_http_client.send = send_mock

    await client.client_channel.signin_toolsets(
        channel_id="ch", toolset_ids=["a", "b"]
    )

    body = json.loads(captured["request"].content)
    assert isinstance(body, list) and len(body) == 2
    assert body[0]["params"] == {"toolsetId": "a"}
    assert body[1]["params"] == {"toolsetId": "b"}


# ----------------------------------------------------------------------------
# Internal _interact — protocol-level coverage
# ----------------------------------------------------------------------------


def test_interact_result_null_is_valid_sync():
    # {result: null} is a successful response per JSON-RPC spec — must not
    # raise ParsingDataError as the old code did.
    chunks = _single_event({"jsonrpc": "2.0", "id": "1", "result": None})
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    responses = client.client_channel._interact(
        channel_id="ch",
        requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
    )
    assert len(responses) == 1
    assert responses[0].result is None
    assert responses[0].error is None


def test_interact_response_missing_id_raises_parsing_error_sync():
    chunks = _single_event({"jsonrpc": "2.0", "result": "ok"})
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel._interact(
            channel_id="ch",
            requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
        )


def test_interact_response_with_both_result_and_error_raises_sync():
    chunks = _single_event(
        {
            "jsonrpc": "2.0",
            "id": "1",
            "result": "ok",
            "error": {"code": -1, "message": "x"},
        }
    )
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel._interact(
            channel_id="ch",
            requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
        )


def test_interact_response_with_neither_result_nor_error_raises_sync():
    chunks = _single_event({"jsonrpc": "2.0", "id": "1"})
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel._interact(
            channel_id="ch",
            requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
        )


def test_interact_malformed_json_raises_sync():
    chunks = _sse_chunks("data: not-json", "")
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel._interact(
            channel_id="ch",
            requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
        )


def test_interact_heartbeats_skipped_sync():
    chunks = _sse_chunks(
        ": heartbeat",
        "",
        ": heartbeat",
        "",
        _data(_signin_response("1", "success")),
        "",
    )
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    responses = client.client_channel._interact(
        channel_id="ch",
        requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
    )
    assert responses[0].result == "success"


def test_interact_truncated_stream_warns_and_no_phantom_event_sync(caplog):
    # No trailing blank line — incomplete event must NOT be flushed, and a
    # warning must be emitted by the SSE parser.
    chunks = _sse_chunks('data: {"jsonrpc":"2.0","resu')
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with (
        caplog.at_level(logging.WARNING, logger="aidial_client"),
        pytest.raises(DialException) as exc_info,
    ):
        client.client_channel._interact(
            channel_id="ch",
            requests=[JsonRpcRequest(jsonrpc="2.0", method="m", id="1")],
        )
    assert exc_info.value.status_code == HTTPStatus.GATEWAY_TIMEOUT
    assert any(
        "Uncommitted data chunks in SSE stream" in rec.message
        for rec in caplog.records
    )
