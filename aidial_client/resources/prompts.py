from pathlib import PurePosixPath
from typing import Optional, Union
from urllib.parse import urljoin

import httpx

from aidial_client._constants import API_PREFIX
from aidial_client._exception import DialException, ResourceNotFoundError
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.helpers.storage_resource import DialStorageResourceMixin
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.metadata import AsyncMetadata, Metadata
from aidial_client.types.metadata import PromptMetadata
from aidial_client.types.prompt import Prompt


def _prompts_error_processor(
    http_status_error: httpx.HTTPStatusError,
) -> Optional[DialException]:
    if http_status_error.response.status_code == 404:
        return ResourceNotFoundError(
            message=http_status_error.response.text,
        )
    return None


class Prompts(Resource, DialStorageResourceMixin):
    metadata: Metadata
    resource_type: str = "prompts"

    def get(self, url: Union[str, PurePosixPath]) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            on_http_error=_prompts_error_processor,
        )

    def get_metadata(self, url: Union[str, PurePosixPath]) -> PromptMetadata:
        return self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(str(url)),
        )


class AsyncPrompts(AsyncResource, DialStorageResourceMixin):
    metadata: AsyncMetadata
    resource_type: str = "prompts"

    async def get(self, url: Union[str, PurePosixPath]) -> Prompt:
        """Fetch a single prompt by its storage path."""
        return await self.http_client.request(
            cast_to=Prompt,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            on_http_error=_prompts_error_processor,
        )

    async def get_metadata(
        self, url: Union[str, PurePosixPath]
    ) -> PromptMetadata:
        return await self.metadata.get(
            resource="prompts",
            relative_url=self.get_api_path(str(url)),
        )
