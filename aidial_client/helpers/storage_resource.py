from pathlib import PurePosixPath
from typing import Literal, cast, get_args
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit

import httpx
from typing_extensions import assert_never

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._constants import API_PREFIX_V1, API_PREFIX_V2
from aidial_client._exception import (
    DialException,
    EtagMismatchError,
    InvalidDialURLError,
    NotDialURLError,
    ResourceNotFoundError,
)
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client._utils._dict import remove_none
from aidial_client.helpers._url import enforce_trailing_slash

StorageResourceTypeV1 = Literal["files", "conversations", "prompts"]
"""Resource types served by the /v1 storage API."""

StorageResourceTypeV2 = Literal["skills"]
"""Folder-shaped resource types served by the /v2 API."""

AnyStorageResourceType = StorageResourceTypeV1 | StorageResourceTypeV2


def api_prefix_for(resource_type: AnyStorageResourceType) -> str:
    """The API prefix that serves ``resource_type``."""
    match resource_type:
        case "files" | "conversations" | "prompts":
            return API_PREFIX_V1
        case "skills":
            return API_PREFIX_V2
        case _:
            assert_never(resource_type)


def _percent_encode_relative_url(url: str) -> str:
    """
    Percent-encode each path segment so reserved characters (space, ``#``,
    ``?``, ``[`` …) reach DIAL Core encoded instead of making it answer 500.
    Segments are decoded first, so a decoded path (``my file.txt``) and an
    already-encoded one (``my%20file.txt``, as returned by the API) converge
    without double-encoding. Absolute URLs come from the API already encoded and
    are returned untouched.
    """
    if urlsplit(url).netloc:
        return url

    segments = url.split("/")
    return "/".join(quote(unquote(seg), safe="") for seg in segments)


def split_relative_segments(
    path: str,
    param: str,
    *,
    allow_trailing_slash: bool = False,
) -> tuple[str, ...]:
    """
    Split a relative path and reject any segment that would change which
    resource the path addresses.

    Each segment is checked *as it will decode*, because
    ``_percent_encode_relative_url`` normalizes with ``unquote`` before
    quoting: "%2e%2e" would otherwise pass a literal check and still reach
    ``urljoin`` as "..", and "%2f" would smuggle in a separator. ``urljoin``
    resolves "." and ".." while building a request, which shifts the bucket
    segment - "../../../other-bucket/x" turns a validated "skills/my-bucket"
    into a request against ``other-bucket``.

    ``allow_trailing_slash`` accepts one trailing empty segment, which is how
    DIAL spells "this is a folder". It is off for paths given to a resource
    reference, where the terminal call decides file vs folder.
    """
    if not path.strip():
        raise InvalidDialURLError(f"{param} must not be empty")
    if path.startswith("/"):
        raise InvalidDialURLError(f"{param} must be relative, got: {path!r}")

    segments = tuple(path.split("/"))
    if not allow_trailing_slash and path.endswith("/"):
        raise InvalidDialURLError(
            f"{param} must not end with '/', got: {path!r}. The terminal call"
            " decides whether the reference names a file or a folder."
        )

    # A trailing slash marks a folder; it is not a segment of its own.
    checked = segments[:-1] if path.endswith("/") else segments
    for segment in checked:
        decoded = unquote(segment)
        if decoded == "":
            raise InvalidDialURLError(
                f"Empty path segment in {param}, got: {path!r}"
            )
        if decoded in (".", ".."):
            raise InvalidDialURLError(
                f'"." and ".." are not allowed in {param}, got: {path!r}'
            )
        if "/" in decoded:
            raise InvalidDialURLError(
                "An encoded path separator is not allowed in"
                f" {param}, got: {path!r}"
            )
    return segments


def _storage_error_processor(
    http_status_error: httpx.HTTPStatusError,
) -> DialException | None:
    """
    Translate the status codes DIAL storage endpoints use for optimistic
    concurrency and absence into the typed exception hierarchy.
    """
    if http_status_error.response.status_code == 412:
        return EtagMismatchError(
            message=http_status_error.response.text,
        )
    elif http_status_error.response.status_code == 404:
        return ResourceNotFoundError(
            message=http_status_error.response.text,
        )
    return None


def _is_directory(s: str) -> bool:
    return s.endswith("/")


class DialStorageResource(BaseModel):
    resource_type: AnyStorageResourceType

    """Bucket name, like 'my-bucket'"""
    bucket: str

    """Absolute url, like 'https://dial.core/v1/files/my-bucket/my-file.txt'"""
    absolute_url: str

    """Relative url, like '/v1/files/my-bucket/my-file.txt'"""
    relative_url: str

    """Path without api prefix, like 'files/my-bucket/my-folder/my-file.txt'"""
    api_path: str

    """
    Path without bucket, like 'my-folder/my-file.txt'
    None when the URL points at the bucket root
    """
    bucket_path: str | None = None

    """
    Filename, like 'my-file.txt'
    None for a directory
    """
    filename: str | None = None


def safe_parse_storage_resource(
    *,
    url: str,
    dial_api_url: str,
    expected_resource_type: AnyStorageResourceType | None = None,
    allow_empty_bucket_path: bool = False,
) -> DialStorageResource | NotDialURLError | InvalidDialURLError:
    """
    Parse the storage resource from the URL, that could be
    1. Absolute: "https://dial.core/v1/files/my-bucket/my-file.txt"
    2. Relative to API prefix: "files/my-bucket/my-file.txt"

    ``allow_empty_bucket_path`` accepts a URL that names a bucket and nothing
    inside it, like "skills/my-bucket". It is opt-in because a two-segment path
    is ambiguous: "files/my-file.txt" has the same shape and is a missing-bucket
    error. A resource reference passes it unconditionally - it does not yet know
    which call comes next, so the endpoint's own requirements are checked when
    the request is built.
    """
    dial_api_url = enforce_trailing_slash(dial_api_url)
    if url.startswith("/"):
        return InvalidDialURLError(f"Root-relative URL is forbidden: {url}")
    if url.startswith((API_PREFIX_V1, API_PREFIX_V2)):
        return InvalidDialURLError(
            f"API prefix as relative part is not allowed: {url}"
        )

    # Reject traversal on the raw string, before urljoin below resolves it:
    # _percent_encode_relative_url leaves ".." intact (quote treats "." as
    # always-safe), so urljoin would silently retarget another bucket.
    url_path = urlsplit(url).path.lstrip("/")
    if url_path:
        try:
            split_relative_segments(url_path, "url", allow_trailing_slash=True)
        except InvalidDialURLError as error:
            return error

    absolute_url = urljoin(dial_api_url, _percent_encode_relative_url(url))
    url_parsed = urlparse(absolute_url)
    dial_api_parsed = urlparse(dial_api_url)
    if url_parsed.netloc != dial_api_parsed.netloc:
        return NotDialURLError(message=f"Provided URL is not DIAL URL: {url}")
    try:
        url_path_parsed = PurePosixPath(url_parsed.path)
        api_path = url_path_parsed.relative_to(dial_api_parsed.path)
    except ValueError:
        return InvalidDialURLError(
            f"Provided URL path {url_parsed.path} does not match with"
            f" DIAL API URL {dial_api_parsed.path}"
        )

    # "{resource_type}/{bucket}" is the shortest addressable path.
    if len(api_path.parents) < 2:
        return InvalidDialURLError(f"Missing bucket in URL: {url}")

    resource_path = api_path.parents[len(api_path.parents) - 2]
    parsed_resource_type = str(resource_path)

    if parsed_resource_type not in (
        *get_args(StorageResourceTypeV1),
        *get_args(StorageResourceTypeV2),
    ):
        return InvalidDialURLError(
            f"Invalid resource type: {parsed_resource_type}"
        )
    # If user provided expected resource type, check it
    if (
        expected_resource_type is not None
        and parsed_resource_type != expected_resource_type
    ):
        return InvalidDialURLError(
            f"Invalid resource type for URL: {url}\n"
            f"Expected: {expected_resource_type}, got: {parsed_resource_type}"
        )

    if len(api_path.parents) < 3:
        if not allow_empty_bucket_path:
            return InvalidDialURLError(f"Missing bucket path in URL: {url}")
        # The URL is "{resource_type}/{bucket}" - the bucket itself.
        return DialStorageResource(
            resource_type=cast(AnyStorageResourceType, parsed_resource_type),
            absolute_url=absolute_url,
            api_path=str(api_path),
            bucket=api_path.name,
            bucket_path=None,
            relative_url=str(url_path_parsed),
            filename=None,
        )

    bucket_path = api_path.parents[len(api_path.parents) - 3]
    return DialStorageResource(
        resource_type=cast(AnyStorageResourceType, parsed_resource_type),
        absolute_url=absolute_url,
        api_path=str(api_path),
        bucket=str(bucket_path.relative_to(resource_path)),
        bucket_path=str(api_path.relative_to(bucket_path)),
        relative_url=str(url_path_parsed),
        filename=url_path_parsed.name if not _is_directory(url) else None,
    )


def parse_storage_resource(
    *,
    url: str,
    dial_api_url: str,
    expected_resource_type: AnyStorageResourceType | None = None,
    allow_empty_bucket_path: bool = False,
) -> DialStorageResource:
    result = safe_parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
        expected_resource_type=expected_resource_type,
        allow_empty_bucket_path=allow_empty_bucket_path,
    )
    if isinstance(result, NotDialURLError | InvalidDialURLError):
        raise result
    return result


class DialStorageResourceMixin(BaseModel):
    """
    Mixin class for resources that are using DIAL storage:
    - /v1/files
    - /v1/conversations
    - /v1/prompts
    - /v2/skills
    """

    resource_type: AnyStorageResourceType
    dial_api_url: str

    def get_api_prefix(self) -> str:
        """The API prefix serving this resource, implied by its type."""
        return api_prefix_for(self.resource_type)

    def get_storage_resource(
        self,
        url: str | PurePosixPath,
        *,
        allow_empty_bucket_path: bool = False,
    ) -> DialStorageResource:
        """
        Get the storage resource object from the URL
        Args:
            url (str | PurePosixPath): The URL to be processed.
            allow_empty_bucket_path (bool): Accept a URL naming a bucket and
                nothing inside it, such as "skills/my-bucket". Off by default,
                since a two-segment path is otherwise a missing-bucket error.
        Returns:
            DialStorageResource: The storage resource object
        """
        return parse_storage_resource(
            url=str(url),
            dial_api_url=self.dial_api_url,
            expected_resource_type=self.resource_type,
            allow_empty_bucket_path=allow_empty_bucket_path,
        )

    def get_api_path(
        self,
        url: str | PurePosixPath,
        *,
        allow_empty_bucket_path: bool = False,
    ) -> str:
        """
        Convert URL, that could relative or absolute, to relative,
        percent-encoded API path.
        """
        return self.get_storage_resource(
            url, allow_empty_bucket_path=allow_empty_bucket_path
        ).api_path

    def get_display_name(self, url: str | PurePosixPath) -> str | None:
        """
        Get the display name of the resource from the URL
        None when the URL points at the bucket root.
        """
        return self.get_storage_resource(url).bucket_path

    def _prepare_download_request(
        self,
        url: str | PurePosixPath,
        etag_if_match: str | None,
    ) -> tuple[FinalRequestOptions, str]:
        storage_resource = self.get_storage_resource(url)

        if storage_resource.filename is None:
            raise InvalidDialURLError("URL points to a directory, not a file")

        options = FinalRequestOptions(
            method="GET",
            url=urljoin(self.get_api_prefix(), storage_resource.api_path),
            headers=remove_none(
                {
                    "If-Match": etag_if_match,
                }
            ),
        )

        # api_path is percent-encoded; return a human-readable filename.
        return options, unquote(storage_resource.filename)
