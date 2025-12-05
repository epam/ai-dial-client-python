from typing import Optional, Union

import httpx

from aidial_client._auth import AsyncAuthValue, SyncAuthValue
from aidial_client._client import AsyncDial, Dial
from aidial_client._constants import (
    DEFAULT_CONNECTION_LIMITS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
)
from aidial_client._http_client import AsyncHTTPClient, SyncHTTPClient


class DialClientPool:
    def __init__(
        self,
        *,
        connection_limits: httpx.Limits = DEFAULT_CONNECTION_LIMITS,
        **kwargs,
    ):
        self._internal_http_client = httpx.Client(
            limits=connection_limits, **kwargs
        )

    def create_client(
        self,
        *,
        base_url: str,
        api_key: Optional[SyncAuthValue] = None,
        bearer_token: Optional[SyncAuthValue] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: Union[httpx.Timeout, float] = DEFAULT_TIMEOUT,
    ) -> Dial:
        return Dial(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            http_client=SyncHTTPClient(
                base_url=base_url,
                api_key=api_key,
                bearer_token=bearer_token,
                max_retries=max_retries,
                timeout=timeout,
                internal_http_client=self._internal_http_client,
            ),
        )


class AsyncDialClientPool:
    def __init__(
        self,
        *,
        connection_limits: httpx.Limits = DEFAULT_CONNECTION_LIMITS,
        **kwargs,
    ):
        self._internal_http_client = httpx.AsyncClient(
            limits=connection_limits, **kwargs
        )

    def create_client(
        self,
        *,
        base_url: str,
        api_key: Optional[AsyncAuthValue] = None,
        bearer_token: Optional[AsyncAuthValue] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: Union[httpx.Timeout, float] = DEFAULT_TIMEOUT,
    ) -> AsyncDial:
        return AsyncDial(
            base_url=base_url,
            api_key=api_key,
            bearer_token=bearer_token,
            http_client=AsyncHTTPClient(
                base_url=base_url,
                api_key=api_key,
                bearer_token=bearer_token,
                max_retries=max_retries,
                timeout=timeout,
                internal_http_client=self._internal_http_client,
            ),
        )
