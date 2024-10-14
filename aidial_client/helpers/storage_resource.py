from pathlib import PurePosixPath
from typing import Literal, Optional, Union, cast, get_args
from urllib.parse import urljoin, urlparse

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._constants import API_PREFIX
from aidial_client._exception import InvalidDialURLError, NotDialURLError
from aidial_client.helpers._url import enforce_trailing_slash

StorageResourceType = Literal["files", "conversations", "prompts"]


def _is_directory(s: str) -> bool:
    return s[-1] == "/"


class DialStorageResource(BaseModel):
    resource_type: StorageResourceType

    """Bucket name, like 'my-bucket'"""
    bucket: str

    """Absolute url, like 'https://dial.core/v1/files/my-bucket/my-file.txt'"""
    absolute_url: str

    """Relative url, like '/v1/files/my-bucket/my-file.txt'"""
    relative_url: str

    """Path without api prefix, like 'files/my-bucket/my-folder/my-file.txt'"""
    api_path: str

    """Path without bucket, like my-folder/'my-file.txt'"""
    bucket_path: str

    """
    Filename, like 'my-file.txt'
    None for a directory
    """
    filename: Optional[str] = None


def safe_parse_storage_resource(
    *,
    url: str,
    dial_api_url: str,
    expected_resource_type: Optional[StorageResourceType] = None,
) -> Union[DialStorageResource, NotDialURLError, InvalidDialURLError]:
    """
    Parse the storage resource from the URL, that could be
    1. Absolute: "https://dial.core/v1/files/my-bucket/my-file.txt"
    2. Relative to API prefix: "files/my-bucket/my-file.txt"
    """
    dial_api_url = enforce_trailing_slash(dial_api_url)
    if url.startswith("/"):
        return InvalidDialURLError(f"Root-relative URL is forbidden: {url}")
    if url.startswith(API_PREFIX):
        return InvalidDialURLError(
            f"API prefix as relative part is not allowed: {url}"
        )

    absolute_url = urljoin(dial_api_url, url)
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

    resource_path = api_path.parents[len(api_path.parents) - 2]
    parsed_resource_type = str(resource_path)

    if parsed_resource_type not in get_args(StorageResourceType):
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
        return InvalidDialURLError(f"Missing bucket in URL: {url}")

    bucket_path = api_path.parents[len(api_path.parents) - 3]
    return DialStorageResource(
        resource_type=cast(StorageResourceType, parsed_resource_type),
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
    expected_resource_type: Optional[StorageResourceType] = None,
) -> DialStorageResource:
    result = safe_parse_storage_resource(
        url=url,
        dial_api_url=dial_api_url,
        expected_resource_type=expected_resource_type,
    )
    if isinstance(result, (NotDialURLError, InvalidDialURLError)):
        raise result
    return result


class DialStorageResourceMixin(BaseModel):
    """
    Mixin class for resources that are using DIAL storage:
    - /v1/files
    - /v1/conversations
    - /v1/prompts
    """

    resource_type: StorageResourceType
    dial_api_url: str

    def get_storage_resource(self, url: str) -> DialStorageResource:
        """
        Get the storage resource object from the URL
        Args:
            url (str): The URL to be processed.
        Returns:
            DialStorageResource: The storage resource object
        """
        return parse_storage_resource(
            url=url,
            dial_api_url=self.dial_api_url,
            expected_resource_type=self.resource_type,
        )

    def get_api_path(self, url: str) -> str:
        """
        Convert URL, that could relative or absolute, to relative URL
        """
        return self.get_storage_resource(url).api_path

    def get_display_name(self, url: str) -> str:
        """
        Get the display name of the resource from the URL
        """
        return self.get_storage_resource(url).bucket_path
