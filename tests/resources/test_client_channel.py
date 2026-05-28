import json
from http import HTTPStatus
from typing import Any, List

import httpx
import pytest

from aidial_client import Dial
from aidial_client._client import AsyncDial
from aidial_client._exception import (
    DialException,
    InvalidRequestError,
    ParsingDataError,
)
from aidial_client.types.client_channel import (
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
)
from tests.client_mock import (
    MockStreamIterator,
    get_async_client_mock,
    get_client_mock,
)

SINGLE_SUCCESS = {"jsonrpc": "2.0", "result": "success", "id": "1"}
BATCH_PAYLOAD = [
    {"jsonrpc": "2.0", "result": "success", "id": "1"},
    {"jsonrpc": "2.0", "result": "denied", "id": "2"},
]
ERROR_PAYLOAD = {
    "jsonrpc": "2.0",
    "error": {"code": -32000, "message": "boom"},
    "id": "1",
}


def _sse_chunks(*lines: str) -> List[bytes]:
    """Encode a sequence of SSE lines as one byte stream chunk."""
    return [("\n".join(lines) + "\n").encode()]


def _data(payload: Any) -> str:
    return f"data: {json.dumps(payload)}"


def _single_event(payload: Any) -> List[bytes]:
    return _sse_chunks(": heartbeat", "", _data(payload), "")


def test_interact_single_request_sync():
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(SINGLE_SUCCESS)
    )
    responses = client.client_channel.interact(
        channel_id="abc",
        request=JsonRpcRequest(
            method="toolset/signin", params={"toolsetId": "X"}, id="1"
        ),
    )
    assert len(responses) == 1
    assert isinstance(responses[0], JsonRpcResponse)
    assert responses[0].result == "success"
    assert responses[0].id == "1"
    assert responses[0].error is None


@pytest.mark.asyncio
async def test_interact_single_request_async():
    client = get_async_client_mock(
        status_code=200, stream_chunks_mock=_single_event(SINGLE_SUCCESS)
    )
    responses = await client.client_channel.interact(
        channel_id="abc",
        request=JsonRpcRequest(
            method="toolset/signin", params={"toolsetId": "X"}, id="1"
        ),
    )
    assert len(responses) == 1
    assert responses[0].result == "success"


def test_interact_batch_request_sync():
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(BATCH_PAYLOAD)
    )
    requests = [
        JsonRpcRequest(
            method="toolset/signin", params={"toolsetId": "A"}, id="1"
        ),
        JsonRpcRequest(
            method="toolset/signin", params={"toolsetId": "B"}, id="2"
        ),
    ]
    responses = client.client_channel.interact(
        channel_id="abc", request=requests
    )
    assert len(responses) == 2
    assert responses[0].result == "success"
    assert responses[0].id == "1"
    assert responses[1].result == "denied"
    assert responses[1].id == "2"


@pytest.mark.asyncio
async def test_interact_batch_request_async():
    client = get_async_client_mock(
        status_code=200, stream_chunks_mock=_single_event(BATCH_PAYLOAD)
    )
    requests = [
        JsonRpcRequest(method="m", id="1"),
        JsonRpcRequest(method="m", id="2"),
    ]
    responses = await client.client_channel.interact(
        channel_id="abc", request=requests
    )
    assert len(responses) == 2
    assert [r.id for r in responses] == ["1", "2"]


def test_interact_error_response_sync():
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(ERROR_PAYLOAD)
    )
    responses = client.client_channel.interact(
        channel_id="abc", request=JsonRpcRequest(method="m", id="1")
    )
    assert len(responses) == 1
    assert responses[0].result is None
    assert isinstance(responses[0].error, JsonRpcError)
    assert responses[0].error.code == -32000
    assert responses[0].error.message == "boom"


@pytest.mark.asyncio
async def test_interact_error_response_async():
    client = get_async_client_mock(
        status_code=200, stream_chunks_mock=_single_event(ERROR_PAYLOAD)
    )
    responses = await client.client_channel.interact(
        channel_id="abc", request=JsonRpcRequest(method="m", id="1")
    )
    assert responses[0].error is not None
    assert responses[0].error.code == -32000


def test_interact_heartbeats_skipped_sync():
    chunks = _sse_chunks(
        ": heartbeat",
        "",
        ": heartbeat",
        "",
        ": heartbeat",
        "",
        _data(SINGLE_SUCCESS),
        "",
    )
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    responses = client.client_channel.interact(
        channel_id="abc", request=JsonRpcRequest(method="m", id="1")
    )
    assert responses[0].result == "success"


def test_interact_malformed_json_raises_sync():
    chunks = _sse_chunks("data: not-json", "")
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )


def test_interact_no_data_event_raises_sync():
    chunks = _sse_chunks(": heartbeat", "", ": heartbeat", "")
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(DialException) as exc_info:
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )
    assert exc_info.value.status_code == HTTPStatus.GATEWAY_TIMEOUT


def test_interact_truncated_stream_does_not_yield_phantom_event_sync():
    # No trailing blank line — incomplete event must NOT be flushed.
    chunks = _sse_chunks('data: {"jsonrpc":"2.0","resu')
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(DialException) as exc_info:
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )
    assert exc_info.value.status_code == HTTPStatus.GATEWAY_TIMEOUT


def test_interact_http_error_raises_sync():
    body = json.dumps({"error": {"message": "Unauthorized"}}).encode()
    client = get_client_mock(status_code=401, stream_chunks_mock=[body])
    with pytest.raises(DialException) as exc_info:
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"


@pytest.mark.asyncio
async def test_interact_http_error_raises_async():
    body = json.dumps({"error": {"message": "Unauthorized"}}).encode()
    client = get_async_client_mock(status_code=401, stream_chunks_mock=[body])
    with pytest.raises(DialException) as exc_info:
        await client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )
    assert exc_info.value.status_code == 401


def test_interact_sends_channel_header_and_body_sync():
    captured: dict = {}

    def send_mock(request: httpx.Request, **kwargs):
        captured["request"] = request
        return httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(
                mock_chunks=_single_event(SINGLE_SUCCESS)
            ),
        )

    client = Dial(api_key="dummy", base_url="http://dial.core")
    client._http_client._internal_http_client.send = send_mock

    client.client_channel.interact(
        channel_id="my-channel",
        request=JsonRpcRequest(method="toolset/signin", id="1"),
    )

    request = captured["request"]
    assert request.headers["X-DIAL-CLIENT-CHANNEL-ID"] == "my-channel"
    assert request.headers["api-key"] == "dummy"
    assert request.url.path == "/v1/ops/client-channel/interact"
    body = json.loads(request.content)
    assert body == {"jsonrpc": "2.0", "method": "toolset/signin", "id": "1"}


def test_interact_rejects_notification_request_sync():
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(SINGLE_SUCCESS)
    )
    with pytest.raises(InvalidRequestError):
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m")
        )


def test_interact_rejects_batch_with_notification_sync():
    client = get_client_mock(
        status_code=200, stream_chunks_mock=_single_event(BATCH_PAYLOAD)
    )
    with pytest.raises(InvalidRequestError):
        client.client_channel.interact(
            channel_id="abc",
            request=[
                JsonRpcRequest(method="m", id="1"),
                JsonRpcRequest(method="m"),
            ],
        )


def test_interact_rejects_heartbeat_shaped_payload_sync():
    chunks = _single_event({"type": "heartbeat", "ts": 1234})
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )


def test_interact_rejects_null_payload_sync():
    chunks = _sse_chunks("data: null", "")
    client = get_client_mock(status_code=200, stream_chunks_mock=chunks)
    with pytest.raises(ParsingDataError):
        client.client_channel.interact(
            channel_id="abc", request=JsonRpcRequest(method="m", id="1")
        )


def test_interact_preserves_integer_id_sync():
    captured: dict = {}

    def send_mock(request: httpx.Request, **kwargs):
        captured["request"] = request
        return httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(
                mock_chunks=_single_event(
                    {"jsonrpc": "2.0", "result": "ok", "id": 42}
                )
            ),
        )

    client = Dial(api_key="dummy", base_url="http://dial.core")
    client._http_client._internal_http_client.send = send_mock

    responses = client.client_channel.interact(
        channel_id="x",
        request=JsonRpcRequest(method="m", id=42),
    )
    body = json.loads(captured["request"].content)
    assert body["id"] == 42 and isinstance(body["id"], int)
    assert responses[0].id == 42 and isinstance(responses[0].id, int)


@pytest.mark.asyncio
async def test_interact_batch_body_serialized_as_array_async():
    captured: dict = {}

    async def send_mock(request: httpx.Request, **kwargs):
        captured["request"] = request
        return httpx.Response(
            status_code=200,
            request=request,
            stream=MockStreamIterator(mock_chunks=_single_event(BATCH_PAYLOAD)),
        )

    client = AsyncDial(api_key="dummy", base_url="http://dial.core")
    client._http_client._internal_http_client.send = send_mock

    await client.client_channel.interact(
        channel_id="ch",
        request=[
            JsonRpcRequest(method="m", id="1"),
            JsonRpcRequest(method="m", id="2"),
        ],
    )

    body = json.loads(captured["request"].content)
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == "1"
    assert body[1]["id"] == "2"
