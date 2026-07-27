from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import PurePosixPath
from typing import Literal
from urllib.parse import urljoin

import httpx

from aidial_client._constants import API_PREFIX
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
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
from aidial_client.types.metadata import FileItem, FileMetadata


def _move_copy_body(
    resource: DialStorageResourceMixin,
    source: str | PurePosixPath,
    destination: str | PurePosixPath,
    overwrite: bool,
) -> dict[str, object]:
    return {
        "sourceUrl": resource.get_encoded_api_path(str(source)),
        "destinationUrl": resource.get_encoded_api_path(str(destination)),
        "overwrite": overwrite,
    }


def _files_error_processor(
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


class Files(Resource, DialStorageResourceMixin):
    metadata: Metadata
    resource_type: str = "files"

    def upload(
        self,
        url: str | PurePosixPath,
        file: FileTypes,
        etag_if_match: str | None = None,
        etag_if_none_match: Literal["*"] | None = None,
    ) -> FileItem:
        return self.http_client.request(
            cast_to=FileItem,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_encoded_api_path(str(url))),
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
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> FileDownloadResponse:
        options, filename = self._prepare_download_request(url, etag_if_match)
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_files_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    def delete(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> None:
        return self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_encoded_api_path(str(url))),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )

    def move_to(
        self,
        source: str | PurePosixPath,
        destination: str | PurePosixPath,
        overwrite: bool = False,
    ) -> None:
        return self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=urljoin(API_PREFIX, "ops/resource/move"),
                json_data=_move_copy_body(self, source, destination, overwrite),
            ),
            on_http_error=_files_error_processor,
        )

    def copy_to(
        self,
        source: str | PurePosixPath,
        destination: str | PurePosixPath,
        overwrite: bool = False,
    ) -> None:
        return self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=urljoin(API_PREFIX, "ops/resource/copy"),
                json_data=_move_copy_body(self, source, destination, overwrite),
            ),
            on_http_error=_files_error_processor,
        )

    def get_metadata(
        self,
        url: str | PurePosixPath,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata:
        return self.metadata.get(
            resource="files",
            relative_url=self.get_encoded_api_path(str(url)),
            limit=limit,
            token=token,
        )


class AsyncFiles(AsyncResource, DialStorageResourceMixin):
    metadata: AsyncMetadata
    resource_type: str = "files"

    async def upload(
        self,
        url: str | PurePosixPath,
        file: FileTypes,
        etag_if_match: str | None = None,
        etag_if_none_match: Literal["*"] | None = None,
    ) -> FileItem:
        return await self.http_client.request(
            cast_to=FileItem,
            options=FinalRequestOptions(
                method="PUT",
                url=urljoin(API_PREFIX, self.get_encoded_api_path(str(url))),
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
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> FileDownloadResponse:
        options, filename = self._prepare_download_request(url, etag_if_match)
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_files_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    @asynccontextmanager
    async def stream_download(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> AsyncIterator[FileDownloadResponse]:
        options, filename = self._prepare_download_request(url, etag_if_match)
        async with self.http_client.stream(
            options=options,
            on_http_error=_files_error_processor,
        ) as response:
            yield FileDownloadResponse(response=response, filename=filename)

    async def delete(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None = None,
    ) -> None:
        return await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="DELETE",
                url=urljoin(API_PREFIX, self.get_encoded_api_path(str(url))),
                headers=remove_none(
                    {
                        "If-Match": etag_if_match,
                    }
                ),
            ),
            on_http_error=_files_error_processor,
        )

    async def move_to(
        self,
        source: str | PurePosixPath,
        destination: str | PurePosixPath,
        overwrite: bool = False,
    ) -> None:
        return await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=urljoin(API_PREFIX, "ops/resource/move"),
                json_data=_move_copy_body(self, source, destination, overwrite),
            ),
            on_http_error=_files_error_processor,
        )

    async def copy_to(
        self,
        source: str | PurePosixPath,
        destination: str | PurePosixPath,
        overwrite: bool = False,
    ) -> None:
        return await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=urljoin(API_PREFIX, "ops/resource/copy"),
                json_data=_move_copy_body(self, source, destination, overwrite),
            ),
            on_http_error=_files_error_processor,
        )

    async def get_metadata(
        self,
        url: str | PurePosixPath,
        *,
        limit: int | None = None,
        token: str | None = None,
    ) -> FileMetadata:
        return await self.metadata.get(
            resource="files",
            relative_url=self.get_encoded_api_path(str(url)),
            limit=limit,
            token=token,
        )
