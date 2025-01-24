from pathlib import PurePosixPath
from typing import Literal, Optional, Union
from urllib.parse import urljoin

import httpx

from aidial_client._constants import API_PREFIX
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
    InvalidDialURLError,
    ResourceNotFoundError,
)
from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import (
    FileTypes,
    FinalRequestOptions,
)
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import DialStorageResourceMixin
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.resources.metadata import AsyncMetadata, Metadata
from aidial_client.types.file import FileDownloadResponse
from aidial_client.types.metadata import FileMetadata


def _files_error_processor(
    http_status_error: httpx.HTTPStatusError,
) -> Optional[DialException]:
    if http_status_error.response.status_code == 412:
        return EtagMismatchError(
            message=http_status_error.response.text,
        )
    elif http_status_error.response.status_code == 404:
        return ResourceNotFoundError(
            message=http_status_error.response.text,
        )
    return None


class Files(Resource, DialStorageResourceMixin):
    metadata: Metadata
    resource_type: str = "files"

    def upload(
        self,
        url: Union[str, PurePosixPath],
        file: FileTypes,
        etag_if_match: Optional[str] = None,
        etag_if_none_match: Optional[Literal["*"]] = None,
    ) -> FileMetadata:
        return self.http_client.request(
            cast_to=FileMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                files={"file": file},
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )

    def download(
        self,
        url: Union[str, PurePosixPath],
        etag_if_match: Optional[str] = None,
    ) -> FileDownloadResponse:
        storage_resource = self.get_storage_resource(str(url))
        if storage_resource.filename is None:
            raise InvalidDialURLError("URL points to a directory, not a file")
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, storage_resource.api_path),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )
        return FileDownloadResponse(
            response=response, filename=storage_resource.filename
        )

    def delete(
        self,
        url: Union[str, PurePosixPath],
        etag_if_match: Optional[str] = None,
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
            on_http_error=_files_error_processor,
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
        self,
        url: Union[str, PurePosixPath],
        file: FileTypes,
        etag_if_match: Optional[str] = None,
        etag_if_none_match: Optional[Literal["*"]] = None,
    ) -> FileMetadata:

        return await self.http_client.request(
            cast_to=FileMetadata,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_api_path(str(url))),
                files={"file": file},
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                        "If-None-Match": etag_if_none_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )

    async def download(
        self,
        url: Union[str, PurePosixPath],
        etag_if_match: Optional[str] = None,
    ) -> FileDownloadResponse:
        storage_resource = self.get_storage_resource(str(url))
        if storage_resource.filename is None:
            raise InvalidDialURLError("URL points to a directory, not a file")
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(API_PREFIX, storage_resource.api_path),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )
        return FileDownloadResponse(
            response=response, filename=storage_resource.filename
        )

    async def delete(
        self,
        url: Union[str, PurePosixPath],
        etag_if_match: Optional[str] = None,
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
            on_http_error=_files_error_processor,
        )

    async def get_metadata(
        self, url: Union[str, PurePosixPath]
    ) -> FileMetadata:
        return await self.metadata.get(
            resource="files",
            relative_url=self.get_api_path(str(url)),
        )
