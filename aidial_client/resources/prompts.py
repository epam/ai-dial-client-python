from pathlib import PurePosixPath
from typing import Any, Literal
from urllib.parse import urljoin

from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._constants import API_PREFIX
from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import (
    DialStorageResourceMixin,
    storage_error_processor,
)
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.metadata import AsyncMetadata, Metadata
from aidial_client.types.metadata import PromptItem, PromptMetadata
from aidial_client.types.prompt import Prompt


def _prompt_to_json(prompt: Prompt) -> dict[str, Any]:
    if PYDANTIC_V2:
        return prompt.model_dump(by_alias=True)  # type: ignore
    return prompt.dict(by_alias=True)


class Prompts(Resource, DialStorageResourceMixin):
    metadata: Metadata
    resource_type: str = "prompts"

    def save(
        self,
        url: str | PurePosixPath,
        prompt: Prompt,
        etag_if_match: str | None = None,
        etag_if_none_match: Literal["*"] | None = None,
    ) -> PromptItem:
        return self.http_client.request(
            cast_to=PromptItem,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
                json_data=_prompt_to_json(prompt),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=storage_error_processor,
        )

    def get(self, url: str | PurePosixPath) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
            ),
            on_http_error=storage_error_processor,
        )

    def delete(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> None:
        return self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=storage_error_processor,
        )

    def get_metadata(self, url: str | PurePosixPath) -> PromptMetadata:
        return self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(url),
        )


class AsyncPrompts(AsyncResource, DialStorageResourceMixin):
    metadata: AsyncMetadata
    resource_type: str = "prompts"

    async def save(
        self,
        url: str | PurePosixPath,
        prompt: Prompt,
        etag_if_match: str | None = None,
        etag_if_none_match: Literal["*"] | None = None,
    ) -> PromptItem:
        return await self.http_client.request(
            cast_to=PromptItem,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
                json_data=_prompt_to_json(prompt),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=storage_error_processor,
        )

    async def get(self, url: str | PurePosixPath) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return await self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
            ),
            on_http_error=storage_error_processor,
        )

    async def delete(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> None:
        return await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_api_path(url)),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=storage_error_processor,
        )

    async def get_metadata(self, url: str | PurePosixPath) -> PromptMetadata:
        return await self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(url),
        )
