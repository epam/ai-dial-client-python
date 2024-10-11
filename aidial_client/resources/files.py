from pathlib import PurePosixPath
from typing import Optional, Union
from urllib.parse import urljoin

import httpx

from aidial_client._constants import API_PREFIX
from aidial_client._exception import DialException, InvalidBucketError
from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import (
    FileTypes,
    FinalRequestOptions,
)
from aidial_client.helpers.storage_resource import DialStorageResourceMixin
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.metadata import AsyncMetadata, Metadata
from aidial_client.types.file import FileDownloadResponse
from aidial_client.types.metadata import FileMetadata


def _error_processor(error: httpx.HTTPStatusError) -> Optional[DialException]:
    try:
        response = error.response
        error_message = response.text
        if (
            response.status_code == 400
            # TODO: move it to response.code check,
            #  when adapter will return it for this particular error
            and "Url has invalid bucket" in error_message
        ):
            return InvalidBucketError(error_message)
    except Exception:
        return None
    else:
        return None


class Files(Resource, DialStorageResourceMixin):
    metadata: Metadata
    resource_type: str = "files"

    def upload(
        self, url: Union[str, PurePosixPath], file: FileTypes
    ) -> FileMetadata:
        return self.http_client.request(
            cast_to=FileMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                files={"file": file},
            ),
            error_processor=_error_processor,
        )

    def download(self, url: Union[str, PurePosixPath]) -> FileDownloadResponse:
        storage_resource = self.get_storage_resource(str(url))
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, storage_resource.api_path),
            ),
            error_processor=_error_processor,
        )
        assert storage_resource.filename
        return FileDownloadResponse(
            response=response, filename=storage_resource.filename
        )

    def delete(self, url: Union[str, PurePosixPath]) -> None:
        return self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            error_processor=_error_processor,
        )

    def get_metadata(self, url: Union[str, PurePosixPath]) -> FileMetadata:
        return self.metadata.get(
            resource="files",
            relative_url=self.get_api_path(str(url)),
        )


class AsyncFiles(AsyncResource, DialStorageResourceMixin):
    metadata: AsyncMetadata
    resource_type: str = "files"

    async def upload(
        self, url: Union[str, PurePosixPath], file: FileTypes
    ) -> FileMetadata:

        return await self.http_client.request(
            cast_to=FileMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                files={"file": file},
            ),
            error_processor=_error_processor,
        )

    async def download(
        self, url: Union[str, PurePosixPath]
    ) -> FileDownloadResponse:
        storage_resource = self.get_storage_resource(str(url))
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, storage_resource.api_path),
            ),
            error_processor=_error_processor,
        )
        assert storage_resource.filename
        return FileDownloadResponse(
            response=response, filename=storage_resource.filename
        )

    async def delete(self, url: Union[str, PurePosixPath]) -> None:
        return await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
            ),
            error_processor=_error_processor,
        )

    async def get_metadata(
        self, url: Union[str, PurePosixPath]
    ) -> FileMetadata:
        return await self.metadata.get(
            resource="files",
            relative_url=self.get_api_path(str(url)),
        )
