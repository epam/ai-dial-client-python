"""
Chained references to DIAL Core's ``/v2/skills`` API.

A skill is a folder-shaped resource: the whole skill is addressed as a unit at
"skills/{bucket}/{path}", and its bundled files hang off
"skills/{bucket}/{path}/files/{filePath}".

Rather than taking a hand-built URL per call, the resource is a reference that
is narrowed step by step - ``client.skills / "writing" / "tone-of-voice"`` -
so the URL is assembled from validated segments and cannot be typed wrong.
Each narrowing returns a new reference; references are immutable and issue no
requests until a terminal call (``list``/``read``/``download``/``stream``).

The invariant that splits the two kinds of error: **constructing a reference
validates segment syntax; a terminal call validates that the reference has
enough path for its route.**
"""

from collections.abc import AsyncIterator, Awaitable, Callable, Sequence
from contextlib import asynccontextmanager
from urllib.parse import unquote

import httpx
from typing_extensions import Self, overload

from aidial_client._constants import API_PREFIX_V2, METADATA_PREFIX_V2
from aidial_client._exception import InvalidDialURLError
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers.storage_resource import (
    DialStorageResourceMixin,
    StorageResourceTypeV2,
    _percent_encode_relative_url,
    _storage_error_processor,
    split_relative_segments,
)
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.file import FileDownloadResponse
from aidial_client.types.metadata import SkillFileMetadata, SkillMetadata

# DIAL Core reserves this path segment to keep the
# ".../{path}/files/{filePath}" grammar unambiguous.
_FILES_SEGMENT = "files"


def _encode(segments: Sequence[str]) -> str:
    """Percent-encode each segment, so none can contribute a separator."""
    return "/".join(_percent_encode_relative_url(seg) for seg in segments)


def _listing_params(
    limit: int | None,
    token: str | None,
    recursive: bool | None,
) -> dict[str, object]:
    return remove_none({"limit": limit, "token": token, "recursive": recursive})


def _validate_bucket(bucket: str) -> str:
    """A bucket is a URL segment too, so it gets the same treatment."""
    segments = split_relative_segments(bucket, "bucket")
    if len(segments) != 1:
        raise InvalidDialURLError(
            f"bucket must be a single path segment, got: {bucket!r}"
        )
    return segments[0]


class _RefCommon(DialStorageResourceMixin):
    """State and URL parsing shared by both kinds of reference."""

    resource_type: StorageResourceTypeV2 = "skills"
    bucket: str | None = None
    """None means "the caller's own bucket", resolved at terminal-call time."""

    def _split_url(self, url: str) -> tuple[str, tuple[str, ...]]:
        # allow_empty_bucket_path is unconditional: a reference does not know
        # which terminal call comes next, so "skills/my-bucket" must parse and
        # the shape guards decide later whether an empty path is acceptable.
        parsed = self.get_storage_resource(url, allow_empty_bucket_path=True)
        if parsed.bucket_path is None:
            return parsed.bucket, ()
        return parsed.bucket, tuple(parsed.bucket_path.rstrip("/").split("/"))


class _SkillsRefBase(_RefCommon):
    """A skill, a grouping folder, or the bucket root."""

    path: tuple[str, ...] = ()

    @overload
    def __call__(self, *, path: str, bucket: str | None = None) -> Self: ...
    @overload
    def __call__(self, *, bucket: str) -> Self: ...
    @overload
    def __call__(self, *, url: str) -> Self: ...

    def __call__(
        self,
        *,
        path: str | None = None,
        bucket: str | None = None,
        url: str | None = None,
    ) -> Self:
        if url is not None:
            if path is not None or bucket is not None:
                raise TypeError("url= cannot be combined with bucket= or path=")
            new_bucket, segments = self._split_url(url)
            return self.copy(update={"bucket": new_bucket, "path": segments})
        if path is None and bucket is None:
            raise TypeError("one of url=, bucket= or path= is required")

        update: dict[str, object] = {}
        if bucket is not None:
            update["bucket"] = _validate_bucket(bucket)
        if path is not None:
            update["path"] = (
                *self.path,
                *split_relative_segments(path, "path"),
            )
        return self.copy(update=update)

    def __truediv__(self, path: str) -> Self:
        return self(path=path)

    def __repr__(self) -> str:
        bucket = self.bucket if self.bucket is not None else "<my-bucket>"
        return f"{type(self).__name__}('skills/{bucket}/{'/'.join(self.path)}')"

    def _require_skill_path(self, operation: str) -> None:
        if not self.path:
            raise InvalidDialURLError(
                f"{operation} addresses one skill, but this reference points"
                " at the bucket root. Descend to a skill first, e.g."
                ' client.skills / "my-skill".'
            )

    def _metadata_url(self, bucket: str) -> str:
        """``GET /v2/metadata/skills/{bucket}/{path}/`` - a folder listing.

        The separator after ``{bucket}`` in Core's route regex is literal, so
        an empty ``{path}`` only matches with the trailing slash. Core strips a
        trailing slash off ``{path}`` again, so appending it unconditionally
        leaves deeper paths resolving to the same folder as before.
        """
        encoded = _encode(self.path)
        suffix = f"{encoded}/" if encoded else ""
        return f"{METADATA_PREFIX_V2}skills/{bucket}/{suffix}"

    def _archive_url(self, bucket: str) -> tuple[FinalRequestOptions, str]:
        """``GET /v2/skills/{bucket}/{path}`` - the skill as a ZIP archive.

        Core answers ``application/zip`` without a ``Content-Disposition``
        header, so name the archive after the skill.
        """
        options = FinalRequestOptions(
            method="GET",
            url=f"{API_PREFIX_V2}skills/{bucket}/{_encode(self.path)}",
        )
        return options, f"{unquote(self.path[-1])}.zip"


class _SkillFilesRefBase(_RefCommon):
    """The files bundled inside one skill, or a subfolder of them."""

    skill_path: tuple[str, ...] = ()
    path: tuple[str, ...] = ()

    @overload
    def __call__(self, *, path: str) -> Self: ...
    @overload
    def __call__(self, *, url: str) -> Self: ...

    def __call__(
        self,
        *,
        path: str | None = None,
        url: str | None = None,
    ) -> Self:
        if url is not None:
            if path is not None:
                raise TypeError("url= cannot be combined with path=")
            bucket, skill_path, file_path = self._split_files_url(url)
            return self.copy(
                update={
                    "bucket": bucket,
                    "skill_path": skill_path,
                    "path": file_path,
                }
            )
        if path is None:
            raise TypeError("one of url= or path= is required")
        return self.copy(
            update={
                "path": (*self.path, *split_relative_segments(path, "path"))
            }
        )

    def __truediv__(self, path: str) -> Self:
        return self(path=path)

    def __repr__(self) -> str:
        bucket = self.bucket if self.bucket is not None else "<my-bucket>"
        skill = "/".join(self.skill_path)
        return (
            f"{type(self).__name__}('skills/{bucket}/{skill}"
            f"/{_FILES_SEGMENT}/{'/'.join(self.path)}')"
        )

    def _split_files_url(
        self, url: str
    ) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        """Split ``skills/{bucket}/{path}/files/{filePath}`` back into parts.

        The search starts at index 1 because Core's route requires at least
        one segment before ``files`` (``(?<path>.+?)/files/``), so a skill
        named "files" resolves the same way here as it does there.
        """
        bucket, segments = self._split_url(url)
        try:
            index = segments.index(_FILES_SEGMENT, 1)
        except ValueError:
            raise InvalidDialURLError(
                f'url must address a file inside a skill ("…/{_FILES_SEGMENT}'
                f'/…"), got: {url!r}'
            ) from None
        return bucket, segments[:index], segments[index + 1 :]

    def _require_skill_path(self, operation: str) -> None:
        if not self.skill_path:
            raise InvalidDialURLError(
                f"{operation} lists the files of one skill, but this"
                " reference points at the bucket root. Descend to a skill"
                ' first, e.g. (client.skills / "my-skill").files.'
            )

    def _require_file_path(self, operation: str) -> None:
        self._require_skill_path(operation)
        if not self.path:
            raise InvalidDialURLError(
                f"{operation} addresses one file, but no file path was given."
                ' Use skill.files(path="SKILL.md") to name it.'
            )

    def _files_metadata_url(self, bucket: str) -> str:
        """``GET /v2/metadata/skills/{b}/{p}/files[/{filePath}]``."""
        base = (
            f"{METADATA_PREFIX_V2}skills/{bucket}"
            f"/{_encode(self.skill_path)}/{_FILES_SEGMENT}"
        )
        tail = _encode(self.path)
        return f"{base}/{tail}" if tail else base

    def _file_url(self, bucket: str) -> tuple[FinalRequestOptions, str]:
        """``GET /v2/skills/{b}/{p}/files/{filePath}`` - one bundled file."""
        options = FinalRequestOptions(
            method="GET",
            url=(
                f"{API_PREFIX_V2}skills/{bucket}"
                f"/{_encode(self.skill_path)}/{_FILES_SEGMENT}"
                f"/{_encode(self.path)}"
            ),
        )
        # The path is percent-encoded; return a human-readable filename.
        return options, unquote(self.path[-1])


class SkillsRef(Resource, _SkillsRefBase):
    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False

    resolve_bucket: Callable[[], str]

    def _bucket(self) -> str:
        if self.bucket is not None:
            return self.bucket
        return self.resolve_bucket()

    @property
    def files(self) -> "SkillFilesRef":
        return SkillFilesRef(
            http_client=self.http_client,
            dial_api_url=self.dial_api_url,
            bucket=self.bucket,
            skill_path=self.path,
            resolve_bucket=self.resolve_bucket,
        )

    def list(
        self,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillMetadata:
        """
        List the skills and grouping folders this reference points at.

        Follow ``next_token`` until it is ``None`` to read every page.
        """
        return self.http_client.request(
            cast_to=SkillMetadata,
            options=FinalRequestOptions(
                method="GET",
                url=self._metadata_url(self._bucket()),
                params=_listing_params(limit, token, recursive),
            ),
            on_http_error=_storage_error_processor,
        )

    def download(self) -> FileDownloadResponse:
        """Download the whole skill as a ZIP archive."""
        self._require_skill_path("download()")
        options, filename = self._archive_url(self._bucket())
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)


class SkillFilesRef(Resource, _SkillFilesRefBase):
    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False

    resolve_bucket: Callable[[], str]

    def _bucket(self) -> str:
        if self.bucket is not None:
            return self.bucket
        return self.resolve_bucket()

    def list(
        self,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillFileMetadata:
        """
        List the skill's files, optionally scoped to a subfolder.

        A page may hold fewer entries than ``limit``, so follow ``next_token``
        until it is ``None`` rather than assuming one page is complete.
        """
        self._require_skill_path("list()")
        return self.http_client.request(
            cast_to=SkillFileMetadata,
            options=FinalRequestOptions(
                method="GET",
                url=self._files_metadata_url(self._bucket()),
                params=_listing_params(limit, token, recursive),
            ),
            on_http_error=_storage_error_processor,
        )

    def read(self) -> FileDownloadResponse:
        """Download the single file this reference names."""
        self._require_file_path("read()")
        options, filename = self._file_url(self._bucket())
        response = self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)


class AsyncSkillsRef(AsyncResource, _SkillsRefBase):
    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False

    resolve_bucket: Callable[[], Awaitable[str]]

    async def _bucket(self) -> str:
        if self.bucket is not None:
            return self.bucket
        return await self.resolve_bucket()

    @property
    def files(self) -> "AsyncSkillFilesRef":
        return AsyncSkillFilesRef(
            http_client=self.http_client,
            dial_api_url=self.dial_api_url,
            bucket=self.bucket,
            skill_path=self.path,
            resolve_bucket=self.resolve_bucket,
        )

    async def list(
        self,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillMetadata:
        """
        List the skills and grouping folders this reference points at.

        Follow ``next_token`` until it is ``None`` to read every page.
        """
        return await self.http_client.request(
            cast_to=SkillMetadata,
            options=FinalRequestOptions(
                method="GET",
                url=self._metadata_url(await self._bucket()),
                params=_listing_params(limit, token, recursive),
            ),
            on_http_error=_storage_error_processor,
        )

    async def download(self) -> FileDownloadResponse:
        """Download the whole skill as a ZIP archive."""
        self._require_skill_path("download()")
        options, filename = self._archive_url(await self._bucket())
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    @asynccontextmanager
    async def stream_download(self) -> AsyncIterator[FileDownloadResponse]:
        """Stream the whole skill as a ZIP archive."""
        self._require_skill_path("stream_download()")
        options, filename = self._archive_url(await self._bucket())
        async with self.http_client.stream(
            options=options,
            on_http_error=_storage_error_processor,
        ) as response:
            yield FileDownloadResponse(response=response, filename=filename)


class AsyncSkillFilesRef(AsyncResource, _SkillFilesRefBase):
    class Config:
        arbitrary_types_allowed = True
        allow_mutation = False

    resolve_bucket: Callable[[], Awaitable[str]]

    async def _bucket(self) -> str:
        if self.bucket is not None:
            return self.bucket
        return await self.resolve_bucket()

    async def list(
        self,
        *,
        limit: int | None = None,
        token: str | None = None,
        recursive: bool | None = None,
    ) -> SkillFileMetadata:
        """
        List the skill's files, optionally scoped to a subfolder.

        A page may hold fewer entries than ``limit``, so follow ``next_token``
        until it is ``None`` rather than assuming one page is complete.
        """
        self._require_skill_path("list()")
        return await self.http_client.request(
            cast_to=SkillFileMetadata,
            options=FinalRequestOptions(
                method="GET",
                url=self._files_metadata_url(await self._bucket()),
                params=_listing_params(limit, token, recursive),
            ),
            on_http_error=_storage_error_processor,
        )

    async def read(self) -> FileDownloadResponse:
        """Download the single file this reference names."""
        self._require_file_path("read()")
        options, filename = self._file_url(await self._bucket())
        response = await self.http_client.request(
            cast_to=httpx.Response,
            options=options,
            on_http_error=_storage_error_processor,
        )
        return FileDownloadResponse(response=response, filename=filename)

    @asynccontextmanager
    async def stream(self) -> AsyncIterator[FileDownloadResponse]:
        """Stream the single file this reference names."""
        self._require_file_path("stream()")
        options, filename = self._file_url(await self._bucket())
        async with self.http_client.stream(
            options=options,
            on_http_error=_storage_error_processor,
        ) as response:
            yield FileDownloadResponse(response=response, filename=filename)
