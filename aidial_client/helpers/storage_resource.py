from pathlib import PurePosixPath
from typing import Literal, Optional, overload
from urllib.parse import urljoin, urlparse

from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._constants import API_PREFIX
from aidial_client._exception import InvalidDialURLError
from aidial_client.helpers._url import (
    enforce_trailing_slash,
    remove_leading_slash,
    remove_prefix,
)

StorageResourceType = Literal["files", "conversations", "prompts"]


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
    """
    filename: Optional[str] = None


@overload
def parse_storage_resource(
    url: str,
    dial_api_url: str,
    resource_type: StorageResourceType,
    ignore_non_dial_url: Literal[True],
) -> Optional[DialStorageResource]: ...


@overload
def parse_storage_resource(
    url: str,
    dial_api_url: str,
    resource_type: StorageResourceType,
    ignore_non_dial_url: Literal[False],
) -> DialStorageResource: ...


def parse_storage_resource(
    url: str,
    dial_api_url: str,
    resource_type: StorageResourceType,
    ignore_non_dial_url: bool,
) -> Optional[DialStorageResource]:
    dial_api_url = enforce_trailing_slash(dial_api_url)
    url = remove_leading_slash(url)
    # If the URL starts with API_PREFIX, remove it
    url = remove_prefix(url, API_PREFIX)

    absolute_url = urljoin(dial_api_url, remove_leading_slash(url))
    url_parsed = urlparse(absolute_url)
    dial_api_parsed = urlparse(dial_api_url)
    # url is not from DIAL
    if url_parsed.netloc != dial_api_parsed.netloc:
        if ignore_non_dial_url:
            return None
        raise InvalidDialURLError(message="Provided url is not DIAL url: {url}")
    try:
        url_path = PurePosixPath(url_parsed.path)
        api_path = url_path.relative_to(dial_api_parsed.path)
    except ValueError:

        raise InvalidDialURLError(
            f"Provided url path {url_parsed.path} does not match with"
            f" DIAL API url {dial_api_parsed.path}"
        )

    resource_path = api_path.parents[len(api_path.parents) - 2]
    if str(resource_path) != resource_type:
        raise InvalidDialURLError(
            f"Invalid resource type for url: {url}\n"
            f"Expected: {resource_type}, got: {resource_path}"
        )

    if len(api_path.parents) < 3:
        raise InvalidDialURLError(f"Missing bucket in url: {url}")

    bucket_path = api_path.parents[len(api_path.parents) - 3]

    return DialStorageResource(
        resource_type=resource_type,
        absolute_url=absolute_url,
        api_path=str(api_path),
        bucket=str(bucket_path.relative_to(resource_path)),
        bucket_path=str(api_path.relative_to(bucket_path)),
        relative_url=str(url_path),
        filename=url_path.name,
    )


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
            url,
            self.dial_api_url,
            self.resource_type,
            ignore_non_dial_url=False,
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
