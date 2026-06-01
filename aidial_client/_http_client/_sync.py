import time
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager, suppress
from http import HTTPStatus
from typing import Any

import httpx

from aidial_client._auth import SyncAuthValue, get_combined_auth_headers
from aidial_client._exception import DialException
from aidial_client._http_client._base import BaseHTTPClient
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven
from aidial_client._internal_types._generic import ResponseT
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._log import logger
from aidial_client._utils._response_processing import process_block_response


class SyncHTTPClient(BaseHTTPClient[httpx.Client, SyncAuthValue]):
    def _create_internal_client(self) -> httpx.Client:
        return httpx.Client()

    def _retry_request(
        self,
        options: FinalRequestOptions,
        cast_to: type[ResponseT],
        remaining_retries: int,
    ) -> ResponseT:
        remaining = remaining_retries - 1
        logger.debug(f"Retries left: {remaining}")

        sleep_time = self._calculate_retry_sleep_seconds(remaining, options)
        logger.info(f"Making retry to {options.url} in {sleep_time} seconds")
        time.sleep(sleep_time)

        return self.request(
            options=options,
            cast_to=cast_to,
            remaining_retries=remaining,
        )

    def auth_headers(self) -> dict[str, str]:
        return get_combined_auth_headers(
            api_key=self._api_key, bearer_token=self._bearer_token
        )

    def request(
        self,
        *,
        cast_to: type[ResponseT],
        options: FinalRequestOptions,
        remaining_retries: int | None = None,
        on_http_error: Callable[[httpx.HTTPStatusError], DialException | None]
        | None = None,
    ) -> ResponseT:
        retries = self._remaining_retries(remaining_retries, options)
        auth_headers = self.auth_headers()
        request = self._build_request(options, auth_headers)

        try:
            response = self._internal_http_client.send(request)

        except httpx.TimeoutException as err:
            logger.debug("Request failed by timeout")

            if retries > 0:
                return self._retry_request(
                    options,
                    cast_to,
                    retries,
                )

            raise DialException(
                message="Request timed out",
                status_code=HTTPStatus.REQUEST_TIMEOUT,
            ) from err
        except Exception as err:
            logger.debug("Unknown exception")
            if retries > 0:
                return self._retry_request(
                    options=options,
                    cast_to=cast_to,
                    remaining_retries=retries,
                )
            raise DialException(message="Unknown error during request") from err

        logger.debug(f"HTTP Response received with {response.status_code}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as err:
            logger.debug(
                f"Encountered error HTTP status: {err.response.status_code}"
                f"Content: {err.response.text}"
            )

            if retries > 0 and self._should_retry(err.response):
                err.response.close()
                return self._retry_request(
                    options=options,
                    cast_to=cast_to,
                    remaining_retries=retries,
                )
            # Try to get a custom error from response status_code/code/message
            custom_error = on_http_error(err) if on_http_error else None
            # or fallback to default processing
            raised_error = custom_error or self._make_dial_error_from_response(
                err.response
            )
            raise raised_error from err

        return process_block_response(cast_to=cast_to, response=response)

    @contextmanager
    def stream_sse(
        self,
        *,
        method: str,
        url: str,
        json_data: Any,
        headers: Mapping[str, str] | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Iterator[httpx.Response]:
        """Open an SSE streaming response. Yields the open httpx.Response.

        Auth headers are merged in. On non-2xx, reads the body and raises
        a DialException; transport errors (timeouts, network failures) are
        also wrapped so the caller always sees DialException. Retries are
        not performed for streaming requests.

        ``timeout`` defaults to the client-wide timeout; pass an explicit
        ``None`` (or ``httpx.Timeout(None)``) for no timeout.
        """
        merged_headers = {**self.auth_headers(), **(headers or {})}
        effective_timeout = (
            self._timeout if isinstance(timeout, NotGiven) else timeout
        )
        try:
            with self._internal_http_client.stream(
                method=method,
                url=self._prepare_url(url),
                headers=merged_headers,
                json=json_data,
                timeout=effective_timeout,
            ) as response:
                try:
                    response.raise_for_status()
                except httpx.HTTPStatusError as err:
                    with suppress(httpx.HTTPError):
                        response.read()
                    raise self._make_dial_error_from_response(
                        err.response
                    ) from err
                yield response
        except httpx.TimeoutException as err:
            raise DialException(
                message="Request timed out",
                status_code=HTTPStatus.REQUEST_TIMEOUT,
            ) from err
        except httpx.HTTPError as err:
            raise DialException(message=f"Request failed: {err}") from err
