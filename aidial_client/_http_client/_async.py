import asyncio
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager, suppress
from http import HTTPStatus
from typing import Any

import httpx

from aidial_client._auth import AsyncAuthValue, aget_combined_auth_headers
from aidial_client._exception import DialException
from aidial_client._http_client._base import BaseHTTPClient, ErrorHandler
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven
from aidial_client._internal_types._generic import ResponseT
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._log import logger
from aidial_client._utils._response_processing import process_block_response


class AsyncHTTPClient(BaseHTTPClient[httpx.AsyncClient, AsyncAuthValue]):
    def _create_internal_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self._timeout,
        )

    async def auth_headers(self) -> dict[str, str]:
        return await aget_combined_auth_headers(
            api_key=self._api_key, bearer_token=self._bearer_token
        )

    async def _retry_request(
        self,
        *,
        options: FinalRequestOptions,
        cast_to: type[ResponseT],
        remaining_retries: int,
    ) -> ResponseT:
        remaining = remaining_retries - 1
        logger.debug(f"Retries left: {remaining}")

        sleep_time = self._calculate_retry_sleep_seconds(remaining, options)
        logger.info(f"Making retry to {options.url} in {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

        return await self.request(
            options=options, cast_to=cast_to, remaining_retries=remaining
        )

    async def request(
        self,
        *,
        options: FinalRequestOptions,
        cast_to: type[ResponseT],
        remaining_retries: int | None = None,
        on_http_error: ErrorHandler | None = None,
    ) -> ResponseT:
        retries = self._remaining_retries(remaining_retries, options)
        auth_headers = await self.auth_headers()

        request = self._build_request(options, auth_headers)
        try:
            response = await self._internal_http_client.send(request)
        except httpx.TimeoutException as err:
            logger.debug("Request failed by timeout")

            if retries > 0:
                return await self._retry_request(
                    options=options,
                    cast_to=cast_to,
                    remaining_retries=retries,
                )

            raise DialException(
                message="Request timed out",
                status_code=HTTPStatus.REQUEST_TIMEOUT,
            ) from err
        except Exception as err:
            logger.debug("Unknown exception")
            if retries > 0:
                return await self._retry_request(
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
                return await self._retry_request(
                    options=options,
                    cast_to=cast_to,
                    remaining_retries=retries,
                )
            self._raise_for_status(response, on_http_error)

        return process_block_response(cast_to=cast_to, response=response)

    @asynccontextmanager
    async def stream(
        self,
        *,
        options: FinalRequestOptions,
        on_http_error: ErrorHandler | None = None,
    ) -> AsyncIterator[httpx.Response]:
        auth_headers = await self.auth_headers()
        request = self._build_request(options, auth_headers)
        try:
            response = await self._internal_http_client.send(
                request, stream=True
            )
        except httpx.TimeoutException as err:
            raise DialException(
                message="Request timed out",
                status_code=HTTPStatus.REQUEST_TIMEOUT,
            ) from err
        except httpx.HTTPError as err:
            raise DialException(message=f"Request failed: {err}") from err

        try:
            self._raise_for_status(response, on_http_error)
            yield response
        finally:
            await response.aclose()

    @asynccontextmanager
    async def stream_sse(
        self,
        *,
        method: str,
        url: str,
        json_data: Any,
        headers: Mapping[str, str] | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncIterator[httpx.Response]:
        """Open an SSE streaming response. Yields the open httpx.Response.

        Auth headers are merged in. On non-2xx, reads the body and raises
        a DialException; transport errors (timeouts, network failures) are
        also wrapped so the caller always sees DialException. Retries are
        not performed for streaming requests.

        ``timeout`` defaults to the client-wide timeout; pass an explicit
        ``None`` (or ``httpx.Timeout(None)``) for no timeout.
        """
        merged_headers = {**(await self.auth_headers()), **(headers or {})}
        effective_timeout = (
            self._timeout if isinstance(timeout, NotGiven) else timeout
        )
        try:
            async with self._internal_http_client.stream(
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
                        await response.aread()
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
