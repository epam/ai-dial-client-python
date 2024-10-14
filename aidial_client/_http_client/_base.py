from abc import ABC, abstractmethod
from http import HTTPStatus
from random import uniform
from typing import Dict, Generic, Optional, TypeVar, Union

import httpx

from aidial_client._auth import AuthType, AuthValueT
from aidial_client._constants import INITIAL_RETRY_DELAY, MAX_RETRY_DELAY
from aidial_client._exception import DialException
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._type_guard import is_mapping
from aidial_client.helpers._url import enforce_trailing_slash

_HttpInternalClientT = TypeVar(
    "_HttpInternalClientT", bound=Union[httpx.Client, httpx.AsyncClient]
)


class BaseHTTPClient(ABC, Generic[_HttpInternalClientT, AuthValueT]):
    _internal_http_client: _HttpInternalClientT
    _auth_value: AuthValueT
    _auth_type: AuthType

    def __init__(
        self,
        base_url: str,
        auth_value: AuthValueT,
        auth_type: AuthType,
        max_retries: int,
        timeout: Union[float, httpx.Timeout, None],
        internal_http_client: Optional[_HttpInternalClientT] = None,
    ):
        self.base_url = httpx.URL(enforce_trailing_slash(base_url))
        self._auth_value = auth_value
        self._auth_type = auth_type
        self._max_retries = max_retries
        self._timeout = timeout
        self._internal_http_client = (
            internal_http_client or self._create_internal_client()
        )

    @abstractmethod
    def _create_internal_client(
        self,
    ) -> _HttpInternalClientT: ...

    def _prepare_url(self, url: str) -> httpx.URL:
        parsed_url = httpx.URL(url)
        if parsed_url.is_relative_url:
            merge_raw_path = (
                self.base_url.raw_path + parsed_url.raw_path.lstrip(b"/")
            )
            return self.base_url.copy_with(raw_path=merge_raw_path.rstrip(b"/"))
        return parsed_url

    def _build_request(
        self,
        options: FinalRequestOptions,
        auth_headers: Dict[str, str],
    ) -> httpx.Request:
        custom_headers = options.headers or {}
        return self._internal_http_client.build_request(
            headers={**auth_headers, **custom_headers},
            method=options.method,
            url=self._prepare_url(options.url),
            params=(
                httpx.QueryParams(options.params) if options.params else None
            ),
            json=options.json_data,
            files=options.files,
            timeout=options.get_timeout(self._timeout),
        )

    def _remaining_retries(
        self, remaining_retries, options: FinalRequestOptions
    ) -> int:
        return (
            remaining_retries
            if remaining_retries is not None
            else options.get_max_retries(self._max_retries)
        )

    def _should_retry(self, response: httpx.Response) -> bool:
        if response.status_code == HTTPStatus.REQUEST_TIMEOUT:
            return True

        if response.status_code == HTTPStatus.CONFLICT:
            return True

        if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            return True

        return False

    def _calculate_retry_sleep_seconds(
        self,
        remaining_retries: int,
        options: FinalRequestOptions,
    ) -> float:
        max_retries = options.get_max_retries(self._max_retries)

        nb_retries = max_retries - remaining_retries

        # Apply exponential backoff, but not more than the max.
        sleep_seconds = min(
            INITIAL_RETRY_DELAY * pow(2.0, nb_retries), MAX_RETRY_DELAY
        )
        timeout = sleep_seconds + uniform(-0.5, 0.5)
        return max(0, timeout)

    def _make_dial_error_from_response(
        self,
        response: httpx.Response,
    ) -> DialException:
        if response.is_closed and not response.is_stream_consumed:
            # We can't read the response body as it has been closed
            # before it was read. This can happen if an event hook
            # raises a status error.
            return DialException(
                message="Stream was interrupted",
                status_code=response.status_code,
            )

        try:
            message_data = response.json()
            assert is_mapping(message_data)
            error_data = message_data["error"]
            assert is_mapping(error_data)
            return DialException.from_error_data(
                status_code=response.status_code,
                error_data=error_data,
            )
        except Exception:
            return DialException(
                message=response.text, status_code=response.status_code
            )

    @property
    def internal_http_client(self) -> _HttpInternalClientT:
        return self._internal_http_client
