from pathlib import PurePosixPath
from typing import Any, Literal
from urllib.parse import urljoin

import httpx

from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._constants import API_PREFIX
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
    ResourceNotFoundError,
)
from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import DialStorageResourceMixin
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.metadata import AsyncMetadata, Metadata
from aidial_client.types.metadata import PromptMetadata
from aidial_client.types.prompt import Prompt


def _prompts_error_processor(
    http_status_error: httpx.HTTPStatusError,
) -> DialException | None:
    if http_status_error.response.status_code == 412:
        return EtagMismatchError(
            message=http_status_error.response.text,
        )
    elif http_status_error.response.status_code == 404:
        return ResourceNotFoundError(
            message=http_status_error.response.text,
        )
    return None


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
    ) -> PromptMetadata:
        return self.http_client.request(
            cast_to=PromptMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                json_data=_prompt_to_json(prompt),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=_prompts_error_processor,
        )

    def get(self, url: str | PurePosixPath) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            on_http_error=_prompts_error_processor,
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
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_prompts_error_processor,
        )

    def get_metadata(self, url: str | PurePosixPath) -> PromptMetadata:
        return self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(str(url)),
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
    ) -> PromptMetadata:
        return await self.http_client.request(
            cast_to=PromptMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                json_data=_prompt_to_json(prompt),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=_prompts_error_processor,
        )

    async def get(self, url: str | PurePosixPath) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return await self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            on_http_error=_prompts_error_processor,
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
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_prompts_error_processor,
        )

    async def get_metadata(self, url: str | PurePosixPath) -> PromptMetadata:
        return await self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(str(url)),
        )
