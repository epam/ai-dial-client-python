from typing import Any, AsyncIterator, Dict, Iterator, List, Optional

import httpx
from httpx._content import AsyncIteratorByteStream, IteratorByteStream

from aidial_client import Dial
from aidial_client._client import AsyncDial


class MockStreamIterator(IteratorByteStream, AsyncIteratorByteStream):
    def __init__(self, mock_chunks: List[bytes]):
        class Stream:
            def __iter__(self) -> Iterator[bytes]:
                for chunk in mock_chunks:
                    yield chunk

            async def __aiter__(self) -> AsyncIterator[bytes]:
                for chunk in mock_chunks:
                    yield chunk

        AsyncIteratorByteStream.__init__(self, stream=Stream())
        IteratorByteStream.__init__(self, stream=Stream())


def get_client_mock(
    status_code: Optional[int],
    json_mock: Optional[Dict[str, Any]] = None,
    stream_chunks_mock: Optional[List[bytes]] = None,
    exception_mock: Optional[Exception] = None,
) -> Dial:
    client_mock = Dial(
        api_key="dummy",
        base_url="http://dial.core",
    )

    def send_mock(request: httpx.Request, **kwargs):
        if json_mock is not None:
            assert status_code
            mock_response = httpx.Response(
                status_code=status_code, request=request, json=json_mock
            )
            mock_response.request = request
            return mock_response
        elif stream_chunks_mock is not None:
            assert status_code
            mock_response = httpx.Response(
                status_code=status_code,
                request=request,
                stream=MockStreamIterator(mock_chunks=stream_chunks_mock),
            )
            mock_response.request = request
            return mock_response
        elif exception_mock is not None:
            raise exception_mock
        else:
            raise NotImplementedError()

    client_mock._http_client._client.send = send_mock
    return client_mock


def get_async_client_mock(
    status_code: Optional[int],
    json_mock: Optional[Dict[str, Any]] = None,
    stream_chunks_mock: Optional[List[bytes]] = None,
    exception_mock: Optional[Exception] = None,
) -> AsyncDial:
    client_mock = AsyncDial(
        api_key="dummy",
        base_url="http://dial.core",
    )

    async def send_mock(request: httpx.Request, **kwargs):
        if json_mock is not None:
            assert status_code
            mock_response = httpx.Response(
                status_code=status_code, request=request, json=json_mock
            )
            mock_response.request = request
            return mock_response
        elif stream_chunks_mock is not None:
            assert status_code
            mock_response = httpx.Response(
                status_code=status_code,
                request=request,
                stream=MockStreamIterator(mock_chunks=stream_chunks_mock),
            )
            mock_response.request = request
            return mock_response
        elif exception_mock is not None:
            raise exception_mock
        else:
            raise NotImplementedError()

    client_mock._http_client._client.send = send_mock
    return client_mock
