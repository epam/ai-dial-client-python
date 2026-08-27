from pathlib import PurePosixPath
from typing import Literal, cast, get_args
from urllib.parse import quote, unquote, urljoin, urlparse, urlsplit

import httpx

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._constants import API_PREFIX
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

StorageResourceType = Literal["files", "conversations", "prompts"]
"""Resource types served by the /v1 storage API."""

V2StorageResourceType = Literal["skills"]
"""Folder-shaped resource types served by the /v2 API."""

AnyStorageResourceType = StorageResourceType | V2StorageResourceType


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


def storage_error_processor(
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
    return s[-1] == "/"


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
    Empty string when the URL points at the bucket root
    """
    bucket_path: str

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
    api_prefix: str = API_PREFIX,
    allow_bucket_root: bool = False,
) -> DialStorageResource | NotDialURLError | InvalidDialURLError:
    """
    Parse the storage resource from the URL, that could be
    1. Absolute: "https://dial.core/v1/files/my-bucket/my-file.txt"
    2. Relative to API prefix: "files/my-bucket/my-file.txt"

    ``allow_bucket_root`` accepts a bucket-root URL like "skills/my-bucket".
    It is opt-in because a two-segment path is ambiguous: "files/my-file.txt"
    has the same shape and is a missing-bucket error. Only callers whose
    endpoint accepts an empty path (DIAL Core's v2 metadata listing) enable it.
    """
    dial_api_url = enforce_trailing_slash(dial_api_url)
    if url.startswith("/"):
        return InvalidDialURLError(f"Root-relative URL is forbidden: {url}")
    if url.startswith(api_prefix):
        return InvalidDialURLError(
            f"API prefix as relative part is not allowed: {url}"
        )

    absolute_url = urljoin(dial_api_url, _percent_encode_relative_url(url))
    url_parsed = urlparse(absolute_url)
    dial_api_parsed = urlparse(dial_api_url)
    if url_parsed.netloc != dial_api_parsed.netloc:
        return NotDialURLError(message=f"Provided URL is not DIAL URL: {url}")
    try:
        url_path = PurePosixPath(url_parsed.path)
        api_path = url_path.relative_to(dial_api_parsed.path)
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
        *get_args(StorageResourceType),
        *get_args(V2StorageResourceType),
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
        if not allow_bucket_root:
            return InvalidDialURLError(f"Missing bucket in URL: {url}")
        # The URL is "{resource_type}/{bucket}" — the bucket itself.
        return DialStorageResource(
            resource_type=cast(AnyStorageResourceType, parsed_resource_type),
            absolute_url=absolute_url,
            api_path=str(api_path),
            bucket=api_path.name,
            bucket_path="",
            relative_url=str(url_path),
            filename=None,
        )

    bucket_path = api_path.parents[len(api_path.parents) - 3]
    return DialStorageResource(
        resource_type=cast(AnyStorageResourceType, parsed_resource_type),
        absolute_url=absolute_url,
        api_path=str(api_path),
        bucket=str(bucket_path.relative_to(resource_path)),
        bucket_path=str(api_path.relative_to(bucket_path)),
        relative_url=str(url_path),
        filename=url_path.name if not _is_directory(url) else None,
    )


def parse_storage_resource(
    *,
    url: str,
    dial_api_url: str,
    expected_resource_type: AnyStorageResourceType | None = None,
    api_prefix: str = API_PREFIX,
    allow_bucket_root: bool = False,
) -> DialStorageResource:
    result = safe_parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
        expected_resource_type=expected_resource_type,
        api_prefix=api_prefix,
        allow_bucket_root=allow_bucket_root,
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
    api_prefix: str = API_PREFIX

    def get_storage_resource(
        self,
        url: str | PurePosixPath,
        *,
        allow_bucket_root: bool = False,
    ) -> DialStorageResource:
        """
        Get the storage resource object from the URL
        Args:
            url (str | PurePosixPath): The URL to be processed.
            allow_bucket_root (bool): Accept a bucket-root URL such as
                "skills/my-bucket". Off by default, since a two-segment path
                is otherwise a missing-bucket error.
        Returns:
            DialStorageResource: The storage resource object
        """
        return parse_storage_resource(
            url=str(url),
            dial_api_url=self.dial_api_url,
            expected_resource_type=self.resource_type,
            api_prefix=self.api_prefix,
            allow_bucket_root=allow_bucket_root,
        )

    def get_api_path(
        self,
        url: str | PurePosixPath,
        *,
        allow_bucket_root: bool = False,
    ) -> str:
        """
        Convert URL, that could relative or absolute, to relative,
        percent-encoded API path.
        """
        return self.get_storage_resource(
            url, allow_bucket_root=allow_bucket_root
        ).api_path

    def get_display_name(self, url: str | PurePosixPath) -> str:
        """
        Get the display name of the resource from the URL
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
            url=urljoin(self.api_prefix, storage_resource.api_path),
            headers=remove_none(
                {
                    "If-Match": etag_if_match,
                }
            ),
        )

        # api_path is percent-encoded; return a human-readable filename.
        return options, unquote(storage_resource.filename)
