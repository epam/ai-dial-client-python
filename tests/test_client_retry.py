from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from aidial_client._exception import DialException
from tests.client_mock import get_async_client_mock, get_client_mock


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (httpx.TimeoutException("Request timed out"), "Request timed out"),
        (Exception("Unknown"), "Unknown error during request"),
    ],
)
def test_exception_retry_sync(exception, expected_message):
    client = get_client_mock(
        status_code=None,
        exception_mock=exception,
    )
    retry_request_mock = Mock()
    remaining_retries_mock = Mock()
    client._http_client._remaining_retries = remaining_retries_mock
    client._http_client._retry_request = retry_request_mock

    # If retries are not exhausted, the request should be retried
    remaining_retries_mock.return_value = 1
    client.bucket.get_bucket()
    assert retry_request_mock.call_count == 1
    # After retries are exhausted, the exception should be raised
    remaining_retries_mock.return_value = 0
    with pytest.raises(Exception) as e:
        client.bucket.get_bucket()
    assert isinstance(e.value, DialException)
    assert e.value.message == expected_message
    # Retry request should not be called again
    assert retry_request_mock.call_count == 1


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (httpx.TimeoutException("Request timed out"), "Request timed out"),
        (Exception("Unknown"), "Unknown error during request"),
    ],
)
@pytest.mark.asyncio
async def test_exception_retry_async(exception, expected_message):
    client = get_async_client_mock(
        status_code=None,
        exception_mock=exception,
    )
    retry_request_mock = AsyncMock()
    remaining_retries_mock = Mock()
    client._http_client._remaining_retries = remaining_retries_mock
    client._http_client._retry_request = retry_request_mock

    # If retries are not exhausted, the request should be retried
    remaining_retries_mock.return_value = 1
    await client.bucket.get_bucket()
    assert retry_request_mock.call_count == 1
    # After retries are exhausted, the exception should be raised
    remaining_retries_mock.return_value = 0
    with pytest.raises(Exception) as e:
        await client.bucket.get_bucket()
    assert isinstance(e.value, DialException)
    assert e.value.message == expected_message
    assert retry_request_mock.call_count == 1


@pytest.mark.parametrize(
    "status_code, is_retry_called",
    [
        (HTTPStatus.REQUEST_TIMEOUT, True),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.CONFLICT, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.NOT_FOUND, False),
    ],
)
def test_status_codes_retries(status_code, is_retry_called):
    client = get_client_mock(status_code=status_code, json_mock={})
    remaining_retries_mock = Mock()
    remaining_retries_mock.return_value = 1
    client._http_client._remaining_retries = remaining_retries_mock
    retry_request_mock = Mock()
    client._http_client._retry_request = retry_request_mock

    if is_retry_called:
        client.bucket.get_bucket()
        assert retry_request_mock.called == is_retry_called
    else:
        with pytest.raises(DialException) as e:
            client.bucket.get_bucket()
        assert e.value.status_code == status_code  # type: ignore
        assert not retry_request_mock.called


@pytest.mark.parametrize(
    "status_code, is_retry_called",
    [
        (HTTPStatus.REQUEST_TIMEOUT, True),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.CONFLICT, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.NOT_FOUND, False),
    ],
)
@pytest.mark.asyncio
async def test_status_codes_retries_async(status_code, is_retry_called):
    client = get_async_client_mock(status_code=status_code, json_mock={})
    remaining_retries_mock = Mock()
    remaining_retries_mock.return_value = 1
    client._http_client._remaining_retries = remaining_retries_mock
    retry_request_mock = AsyncMock()
    client._http_client._retry_request = retry_request_mock

    if is_retry_called:
        await client.bucket.get_bucket()
        assert retry_request_mock.called == is_retry_called
    else:
        with pytest.raises(DialException) as e:
            await client.bucket.get_bucket()
        assert e.value.status_code == status_code  # type: ignore
