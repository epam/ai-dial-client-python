from typing import Literal, overload
from urllib.parse import urljoin

from typing_extensions import assert_never

from aidial_client._constants import METADATA_PREFIX
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import StorageResourceType
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.metadata import (
    ConversationMetadata,
    FileMetadata,
    PromptMetadata,
)


def _get_cast_to(
    resource: StorageResourceType,
) -> type[FileMetadata] | type[ConversationMetadata] | type[PromptMetadata]:
    if resource == "files":
        return FileMetadata
    elif resource == "conversations":
        return ConversationMetadata
    elif resource == "prompts":
        return PromptMetadata
    else:
        assert_never(resource)


class Metadata(Resource):
    @overload
    def get(
        self,
        resource: Literal["files"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata: ...

    @overload
    def get(
        self,
        resource: Literal["conversations"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> ConversationMetadata: ...

    @overload
    def get(
        self,
        resource: Literal["prompts"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> PromptMetadata: ...

    def get(
        self,
        resource: StorageResourceType,
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata | ConversationMetadata | PromptMetadata:
        return self.http_client.request(
            cast_to=_get_cast_to(resource),
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(METADATA_PREFIX, relative_url),
                params=remove_none({"limit": limit, "token": token}),
            ),
        )


class AsyncMetadata(AsyncResource):
    @overload
    async def get(
        self,
        resource: Literal["files"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata: ...

    @overload
    async def get(
        self,
        resource: Literal["conversations"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> ConversationMetadata: ...

    @overload
    async def get(
        self,
        resource: Literal["prompts"],
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> PromptMetadata: ...

    async def get(
        self,
        resource: StorageResourceType,
        relative_url: str,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata | ConversationMetadata | PromptMetadata:
        return await self.http_client.request(
            cast_to=_get_cast_to(resource),
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(METADATA_PREFIX, relative_url),
                params=remove_none({"limit": limit, "token": token}),
            ),
        )
