import asyncio
from http import HTTPStatus
from typing import Callable, Dict, Optional, Type

import httpx

from aidial_client._auth import AsyncAuthValue, aget_auth_headers
from aidial_client._exception import DialException
from aidial_client._http_client._base import BaseHTTPClient
from aidial_client._internal_types._generic import ResponseT
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._log import logger
from aidial_client._utils._response_processing import process_block_response


class AsyncHTTPClient(BaseHTTPClient[httpx.AsyncClient, AsyncAuthValue]):
    def _create_internal_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            timeout=self._timeout,
        )

    async def auth_headers(self) -> Dict[str, str]:
        return await aget_auth_headers(
            auth_value=self._auth_value, auth_type=self._auth_type
        )

    async def _retry_request(
        self,
        *,
        options: FinalRequestOptions,
        cast_to: Type[ResponseT],
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
        cast_to: Type[ResponseT],
        remaining_retries: Optional[int] = None,
        on_http_error: Optional[
            Callable[[httpx.HTTPStatusError], Optional[DialException]]
        ] = None,
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
            # Try to get custom error from response status_code/code/message
            custom_error = on_http_error(err) if on_http_error else None
            # or fallback to default processing
            raised_error = custom_error or self._make_dial_error_from_response(
                err.response
            )
            raise raised_error from err

        return process_block_response(cast_to=cast_to, response=response)
