from abc import ABC, abstractmethod
from pathlib import PurePosixPath
from typing import Dict, Generic, Optional, TypeVar, Union
from urllib.parse import urljoin

import openai
from httpx import Timeout

import aidial_client.resources as resources
from aidial_client._auth import (
    AsyncAuthValue,
    AuthType,
    AuthValueT,
    SyncAuthValue,
    process_auth,
)
from aidial_client._constants import (
    API_PREFIX,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    OPENAI_PREFIX,
)
from aidial_client._http_client import AsyncHTTPClient, SyncHTTPClient
from aidial_client._internal_types._defaults import NOT_GIVEN, NotGiven
from aidial_client.helpers._url import enforce_trailing_slash
from aidial_client.types.bucket import AppData

_HttpClientT = TypeVar(
    "_HttpClientT", bound=Union[AsyncHTTPClient, SyncHTTPClient]
)


class BaseDialClient(Generic[_HttpClientT, AuthValueT], ABC):
    _auth_type: AuthType
    _auth_value: AuthValueT
    _base_url: str
    _http_client: _HttpClientT
    _auth_headers: Dict[str, str]
    _my_bucket: Optional[str]
    _my_appdata: Union[AppData, None, NotGiven]

    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[AuthValueT] = None,
        bearer_token: Optional[AuthValueT] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: Union[float, Timeout, None] = DEFAULT_TIMEOUT,
        api_version: Optional[str] = None,
        http_client: Optional[_HttpClientT] = None,
    ):
        self._auth_type, self._auth_value = process_auth(
            api_key=api_key, bearer_token=bearer_token
        )
        self._max_retries = max_retries
        self._timeout = timeout
        self._base_url = enforce_trailing_slash(base_url)
        self._api_version = api_version
        self._http_client = http_client or self._create_http_client()
        self._my_bucket = None
        self._my_appdata = NOT_GIVEN
        self._init_resources()

    @abstractmethod
    def _init_resources(self) -> None: ...

    @abstractmethod
    def _create_http_client(self) -> _HttpClientT: ...

    def is_dial_url(self, absolute_url: str) -> bool:
        return enforce_trailing_slash(absolute_url).startswith(self._base_url)

    @property
    def api_url(self) -> str:
        return urljoin(self._base_url, API_PREFIX)

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    def api_version(self) -> Optional[str]:
        return self._api_version


class Dial(BaseDialClient[SyncHTTPClient, SyncAuthValue]):
    def _init_resources(self) -> None:
        openai_client = openai.AzureOpenAI(
            api_key="-",
            api_version="-",
            base_url=urljoin(self._base_url, OPENAI_PREFIX),
            http_client=self._http_client.internal_http_client,
        )
        self.chat = resources.Chat(
            http_client=self._http_client,
            completions=resources.chat.ChatCompletions(
                http_client=self._http_client,
                default_api_version=self.api_version,
                openai_client=openai_client,
            ),
        )
        self.bucket = resources.Bucket(http_client=self._http_client)
        self.metadata = resources.Metadata(http_client=self._http_client)
        self.files = resources.Files(
            http_client=self._http_client,
            metadata=self.metadata,
            dial_api_url=self.api_url,
        )
        self.deployments = resources.Deployments(http_client=self._http_client)
        self.application = resources.Application(http_client=self._http_client)

    def _create_http_client(self) -> SyncHTTPClient:
        return SyncHTTPClient(
            self._base_url,
            self._auth_value,
            self._auth_type,
            self._max_retries,
            self._timeout,
        )

    def _get_my_bucket(self) -> str:
        # Wrapper for convenience of unit tests
        return self.bucket.get_bucket()

    def my_bucket(self) -> str:
        if self._my_bucket is None:
            self._my_bucket = self._get_my_bucket()
        return self._my_bucket

    def my_files_home(self) -> PurePosixPath:
        return "files" / PurePosixPath(self.my_bucket())

    def my_conversations_home(self) -> PurePosixPath:
        return "conversations" / PurePosixPath(self.my_bucket())

    def my_prompts_home(self) -> PurePosixPath:
        return "prompts" / PurePosixPath(self.my_bucket())

    def _get_my_appdata(self) -> Optional[AppData]:
        return self.bucket.get_appdata()

    def my_appdata(self) -> Optional[AppData]:
        if isinstance(self._my_appdata, NotGiven):
            self._my_appdata = self._get_my_appdata()
        return self._my_appdata

    def my_appdata_home(self) -> Optional[PurePosixPath]:
        appdata = self.my_appdata()
        if appdata:
            return PurePosixPath(appdata.raw)
        return None

    def auth_headers(self) -> Dict[str, str]:
        return self._http_client.auth_headers()


class AsyncDial(BaseDialClient[AsyncHTTPClient, AsyncAuthValue]):
    def _init_resources(self) -> None:
        openai_client = openai.AsyncAzureOpenAI(
            # set empty string, we will override
            # it with our client values during request
            api_key="",
            api_version="",
            base_url=urljoin(self._base_url, OPENAI_PREFIX),
            http_client=self._http_client.internal_http_client,
            timeout=self._http_client._timeout,
            max_retries=self._http_client._max_retries,
        )
        self.chat = resources.AsyncChat(
            http_client=self._http_client,
            completions=resources.chat.AsyncChatCompletions(
                http_client=self._http_client,
                default_api_version=self.api_version,
                openai_client=openai_client,
            ),
        )
        self.bucket = resources.AsyncBucket(http_client=self._http_client)
        self.metadata = resources.AsyncMetadata(http_client=self._http_client)
        self.files = resources.AsyncFiles(
            http_client=self._http_client,
            metadata=self.metadata,
            dial_api_url=self.api_url,
        )
        self.deployments = resources.AsyncDeployments(
            http_client=self._http_client
        )
        self.application = resources.AsyncApplication(
            http_client=self._http_client
        )

    def _create_http_client(self) -> AsyncHTTPClient:
        return AsyncHTTPClient(
            self._base_url,
            self._auth_value,
            self._auth_type,
            self._max_retries,
            self._timeout,
        )

    async def _get_my_bucket(self) -> str:
        # Wrapper for convenience of unit tests
        return await self.bucket.get_bucket()

    async def my_bucket(self) -> str:
        if self._my_bucket is None:
            self._my_bucket = await self._get_my_bucket()
        return self._my_bucket

    async def my_files_home(self) -> PurePosixPath:
        return "files" / PurePosixPath(await self.my_bucket())

    async def my_conversations_home(self) -> PurePosixPath:
        return "conversations" / PurePosixPath(await self.my_bucket())

    async def my_prompts_home(self) -> PurePosixPath:
        return "prompts" / PurePosixPath(await self.my_bucket())

    async def _get_my_appdata(self) -> Optional[AppData]:
        return await self.bucket.get_appdata()

    async def my_appdata(self) -> Optional[AppData]:
        if isinstance(self._my_appdata, NotGiven):
            self._my_appdata = await self._get_my_appdata()
        return self._my_appdata

    async def my_appdata_home(self) -> Optional[PurePosixPath]:
        appdata = await self.my_appdata()
        if appdata:
            return PurePosixPath(appdata.raw)
        return None

    async def auth_headers(self) -> Dict[str, str]:
        return await self._http_client.auth_headers()
