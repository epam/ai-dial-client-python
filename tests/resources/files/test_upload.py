import os
from unittest.mock import AsyncMock, Mock

import pytest

from aidial_client._exception import InvalidDialURLException
from aidial_client.types.metadata import FileMetadata
from tests.client_mock import get_async_client_mock, get_client_mock

UPLOAD_RESPONSE_MOCK = {
    "name": "file.png",
    "parentPath": "folder1/folder2",
    "bucket": "test-bucket",
    "url": "files/test/folder1/folder2/file.png",
    "nodeType": "ITEM",
    "resourceType": "FILE",
    "contentLength": 128630,
    "contentType": "image/png",
}
current_file_path = os.path.abspath(__file__)


def test_upload_file_object():
    client = get_client_mock(status_code=200, json_mock=UPLOAD_RESPONSE_MOCK)
    client._get_my_bucket = Mock(return_value="test-bucket")

    with open(current_file_path, "rb") as file:
        valid_response = client.files.upload(
            url="files/test-bucket/folder1/folder2/file.png",
            file=file,
        )

        valid_response_using_default_bucket = client.files.upload(
            url=client.my_files_home() / "folder1/folder2/file.png",
            file=file,
        )
        for r in [valid_response, valid_response_using_default_bucket]:
            assert isinstance(r, FileMetadata)
            assert r.bucket == "test-bucket"
            assert r.name == "file.png"
            assert r.parent_path == "folder1/folder2"


@pytest.mark.asyncio
async def test_upload_file_object_async():
    client = get_async_client_mock(
        status_code=200, json_mock=UPLOAD_RESPONSE_MOCK
    )
    client._get_my_bucket = AsyncMock(return_value="test-bucket")

    with open(current_file_path, "rb") as file:
        with pytest.raises(
            InvalidDialURLException, match="Invalid resource type for url"
        ):
            await client.files.upload(
                url="prompts/test-bucket/folder1/folder2/file.png", file=file
            )

        valid_response = await client.files.upload(
            url="files/test-bucket/folder1/folder2/file.png",
            file=file,
        )

        valid_response_with_files_home = await client.files.upload(
            url=await client.my_files_home() / "folder1/folder2/file.png",
            file=file,
        )
        for r in [valid_response, valid_response_with_files_home]:
            assert isinstance(r, FileMetadata)
            assert r.bucket == "test-bucket"
            assert r.name == "file.png"
            assert r.parent_path == "folder1/folder2"
