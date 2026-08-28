from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import PurePosixPath
from urllib.parse import unquote, urljoin

import httpx

from aidial_client._constants import API_V2_PREFIX, METADATA_V2_PREFIX
from aidial_client._exception import InvalidDialURLError
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import (
    DialStorageResourceMixin,
    _percent_encode_relative_url,
    storage_error_processor,
)
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.file import FileDownloadResponse
from aidial_client.types.metadata import SkillFileMetadata, SkillMetadata

# DIAL Core reserves this path segment to keep the
# ".../{path}/files/{filePath}" grammar unambiguous.
FILES_SEGMENT = "files"


def _relative_path_segments(path: str, param: str) -> list[str]:
    """
    Validate a path relative to the skill root and split it into segments.

    Unlike the ``url`` argument, this path is concatenated onto an
    already-parsed api path and never goes back through the url parser, so
    nothing else would catch a traversal segment. ``urljoin`` resolves "." and
    ".." while building the request, which shifts the bucket segment: a
    ``file_path`` of "../../../other-bucket/their-skill/files/SKILL.md" turns a
    validated "skills/my-bucket/my-skill" into a request against
    ``other-bucket``. Reject those segments instead.

    Each segment is checked *as it will decode*, because
    ``_percent_encode_relative_url`` normalizes with ``unquote`` before quoting:
    "%2e%2e" would otherwise pass a literal check here and still reach
    ``urljoin`` as "..", and "%2f" would smuggle in a separator.
    """
    if not path.strip():
        raise InvalidDialURLError(f"{param} must not be empty")
    if path.startswith("/"):
        raise InvalidDialURLError(
            f"{param} must be relative to the skill root, got: {path}"
        )

    segments = path.split("/")
    decoded = [unquote(segment) for segment in segments]
    if any(segment in (".", "..") for segment in decoded):
        raise InvalidDialURLError(
            f'"." and ".." are not allowed in {param}, got: {path}'
        )
    if any("/" in segment for segment in decoded):
        raise InvalidDialURLError(
            f"An encoded path separator is not allowed in {param}, got: {path}"
        )
    # A trailing slash is allowed (it denotes a folder) but an interior empty
    # segment is a malformed path.
    if any(segment == "" for segment in segments[:-1]):
        raise InvalidDialURLError(f"Empty path segment in {param}, got: {path}")
    return segments


class SkillsMixin(DialStorageResourceMixin):
    """
    URL and request shaping shared by the sync and async skills resources.

    A skill is a folder-shaped resource: the whole skill is addressed as a unit
    at "skills/{bucket}/{path}", and its bundled files hang off
    "skills/{bucket}/{path}/files/{filePath}".
    """

    resource_type: str = "skills"
    api_prefix: str = API_V2_PREFIX

    def _files_path(
        self, url: str | PurePosixPath, path: str | None = None
    ) -> str:
        api_path = f"{self.get_api_path(url)}/{FILES_SEGMENT}"
        # None is the "unset" signal; "" goes through the same validation as
        # file_path so the two entry points agree.
        if path is None:
            return api_path

        segments = _relative_path_segments(path, "path")
        if segments[-1] == "":
            # Scoping to a folder - drop the trailing empty segment.
            segments = segments[:-1]
        if not segments:
            return api_path
        relative = _percent_encode_relative_url("/".join(segments))
        return f"{api_path}/{relative}"

    @staticmethod
    def _listing_params(
        limit: int | None,
        token: str | None,
        recursive: bool | None,
    ) -> dict[str, object]:
        return remove_none(
            {"limit": limit, "token": token, "recursive": recursive}
        )

    def _prepare_metadata_request(
        self,
        url: str | PurePosixPath,
        *,
        limit: int | None,
        token: str | None,
        recursive: bool | None,
    ) -> FinalRequestOptions:
        # Core lists the bucket root when {path} is empty, so a bucket-root
        # url ("skills/my-bucket") is a valid target here.
        api_path = self.get_api_path(url, allow_bucket_root=True)
        # This route always addresses a folder, and the separator after
        # {bucket} in Core's route regex is literal:
        #   ^/v2/metadata/skills/(?<bucket>[a-zA-Z0-9]+)/(?<path>.*)$
        # so an empty {path} only matches with a trailing slash. api_path
        # comes from PurePosixPath and never carries one. Core strips a
        # trailing slash off {path} again, so appending it unconditionally
        # leaves the deeper paths resolving to the same folder as before.
        return FinalRequestOptions(
            method="GET",
            url=urljoin(METADATA_V2_PREFIX, f"{api_path}/"),
            params=self._listing_params(limit, token, recursive),
        )

    def _prepare_list_files_request(
        self,
        url: str | PurePosixPath,
        *,
        path: str | None,
        limit: int | None,
        token: str | None,
        recursive: bool | None,
    ) -> FinalRequestOptions:
        return FinalRequestOptions(
            method="GET",
            url=urljoin(METADATA_V2_PREFIX, self._files_path(url, path)),
            params=self._listing_params(limit, token, recursive),
        )

    def _prepare_get_file_request(
        self,
        url: str | PurePosixPath,
        file_path: str,
    ) -> tuple[FinalRequestOptions, str]:
        segments = _relative_path_segments(file_path, "file_path")
        if segments[-1] == "":
            raise InvalidDialURLError(
                f"file_path points to a directory, not a file: {file_path}"
            )

        relative = _percent_encode_relative_url("/".join(segments))
        api_path = f"{self.get_api_path(url)}/{FILES_SEGMENT}/{relative}"
        # No If-Match: unlike the /v1 reads, neither v2 read honours it -
        # ComplexResourceController.getFile never calls ProxyUtil.etag, and
        # the operation declares no If-Match parameter and no 412 response.
        options = FinalRequestOptions(
            method="GET",
            url=urljoin(API_V2_PREFIX, api_path),
        )
        return options, unquote(segments[-1])

    def _prepare_download_archive_request(
        self,
        url: str | PurePosixPath,
    ) -> tuple[FinalRequestOptions, str]:
        api_path = self.get_api_path(url)
        # See _prepare_get_file_request: Core ignores If-Match on this read
        # too (ComplexResourceController.get).
        options = FinalRequestOptions(
            method="GET",
            url=urljoin(API_V2_PREFIX, api_path),
        )
        # Core answers application/zip without a Content-Disposition header,
        # so name the archive after the skill.
        filename = f"{unquote(PurePosixPath(api_path).name)}.zip"
        return options, filename


class Skills(Resource, SkillsMixin):
    def get_metadata(
        self,
        url: str | PurePosixPath,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillMetadata:
        """
        List the skills and grouping folders at ``url``.

        Pass a bucket-root url (``client.my_skills_home()``) to list the whole
        bucket. Follow ``next_token`` until it is ``None`` to read every page.
        """
        return self.http_client.request(
            cast_to=SkillMetadata,
            options=self._prepare_metadata_request(
                url, limit=limit, token=token, recursive=recursive
            ),
            on_http_error=storage_error_processor,
        )

    def list_files(
        self,
        url: str | PurePosixPath,
        *,
        path: str | None = None,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillFileMetadata:
        """
        List the files of the skill at ``url``, optionally scoped to the
        ``path`` subfolder inside it.

        A page may hold fewer entries than ``limit``, so follow ``next_token``
        until it is ``None`` rather than assuming a single page is complete.
        """
        return self.http_client.request(
            cast_to=SkillFileMetadata,
            options=self._prepare_list_files_request(
                url,
                path=path,
                limit=limit,
                token=token,
                recursive=recursive,
            ),
            on_http_error=storage_error_processor,
        )

    def get_file(
        self,
        url: str | PurePosixPath,
        file_path: str,
    ) -> FileDownloadResponse:
        """
        Download a single file bundled in the skill at ``url``.

        ``file_path`` is relative to the skill root, e.g. "SKILL.md" or
        "references/api-schema.md".
        """
        options, filename = self._prepare_get_file_request(url, file_path)
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    def download(
        self,
        url: str | PurePosixPath,
    ) -> FileDownloadResponse:
        """
        Download the whole skill at ``url`` as a ZIP archive.
        """
        options, filename = self._prepare_download_archive_request(url)
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)


class AsyncSkills(AsyncResource, SkillsMixin):
    async def get_metadata(
        self,
        url: str | PurePosixPath,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillMetadata:
        """
        List the skills and grouping folders at ``url``.

        Pass a bucket-root url (``await client.my_skills_home()``) to list the
        whole bucket. Follow ``next_token`` until it is ``None`` to read every
        page.
        """
        return await self.http_client.request(
            cast_to=SkillMetadata,
            options=self._prepare_metadata_request(
                url, limit=limit, token=token, recursive=recursive
            ),
            on_http_error=storage_error_processor,
        )

    async def list_files(
        self,
        url: str | PurePosixPath,
        *,
        path: str | None = None,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillFileMetadata:
        """
        List the files of the skill at ``url``, optionally scoped to the
        ``path`` subfolder inside it.

        A page may hold fewer entries than ``limit``, so follow ``next_token``
        until it is ``None`` rather than assuming a single page is complete.
        """
        return await self.http_client.request(
            cast_to=SkillFileMetadata,
            options=self._prepare_list_files_request(
                url,
                path=path,
                limit=limit,
                token=token,
                recursive=recursive,
            ),
            on_http_error=storage_error_processor,
        )

    async def get_file(
        self,
        url: str | PurePosixPath,
        file_path: str,
    ) -> FileDownloadResponse:
        """
        Download a single file bundled in the skill at ``url``.

        ``file_path`` is relative to the skill root, e.g. "SKILL.md" or
        "references/api-schema.md".
        """
        options, filename = self._prepare_get_file_request(url, file_path)
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    @asynccontextmanager
    async def stream_file(
        self,
        url: str | PurePosixPath,
        file_path: str,
    ) -> AsyncIterator[FileDownloadResponse]:
        """
        Stream a single file bundled in the skill at ``url``.
        """
        options, filename = self._prepare_get_file_request(url, file_path)
        async with self.http_client.stream(
            options=options,
            on_http_error=storage_error_processor,
        ) as response:
            yield FileDownloadResponse(response=response, filename=filename)

    async def download(
        self,
        url: str | PurePosixPath,
    ) -> FileDownloadResponse:
        """
        Download the whole skill at ``url`` as a ZIP archive.
        """
        options, filename = self._prepare_download_archive_request(url)
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    @asynccontextmanager
    async def stream_download(
        self,
        url: str | PurePosixPath,
    ) -> AsyncIterator[FileDownloadResponse]:
        """
        Stream the whole skill at ``url`` as a ZIP archive.
        """
        options, filename = self._prepare_download_archive_request(url)
        async with self.http_client.stream(
            options=options,
            on_http_error=storage_error_processor,
        ) as response:
            yield FileDownloadResponse(response=response, filename=filename)
