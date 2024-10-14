from typing import Literal, Type, Union, overload
from urllib.parse import urljoin

from typing_extensions import assert_never

from aidial_client._constants import METADATA_PREFIX
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.helpers.storage_resource import StorageResourceType
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.metadata import (
    ConversationMetadata,
    FileMetadata,
    PromptMetadata,
)


def _get_cast_to(
    resource: StorageResourceType,
) -> Union[
    Type[FileMetadata], Type[ConversationMetadata], Type[PromptMetadata]
]:
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
        self, resource: Literal["files"], relative_url: str
    ) -> FileMetadata: ...

    @overload
    def get(
        self, resource: Literal["conversations"], relative_url: str
    ) -> ConversationMetadata: ...

    @overload
    def get(
        self, resource: Literal["prompts"], relative_url: str
    ) -> PromptMetadata: ...

    def get(
        self,
        resource: StorageResourceType,
        relative_url: str,
    ) -> Union[FileMetadata, ConversationMetadata, PromptMetadata]:
        return self.http_client.request(
            cast_to=_get_cast_to(resource),
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(METADATA_PREFIX, relative_url),
            ),
        )


class AsyncMetadata(AsyncResource):
    @overload
    async def get(
        self, resource: Literal["files"], relative_url: str
    ) -> FileMetadata: ...

    @overload
    async def get(
        self, resource: Literal["conversations"], relative_url: str
    ) -> ConversationMetadata: ...

    @overload
    async def get(
        self, resource: Literal["prompts"], relative_url: str
    ) -> PromptMetadata: ...

    async def get(
        self,
        resource: StorageResourceType,
        relative_url: str,
    ) -> Union[FileMetadata, ConversationMetadata, PromptMetadata]:
        return await self.http_client.request(
            cast_to=_get_cast_to(resource),
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(METADATA_PREFIX, relative_url),
            ),
        )
