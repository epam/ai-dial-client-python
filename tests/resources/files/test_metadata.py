from unittest.mock import AsyncMock, Mock

import pytest

from aidial_client.types.metadata import FileMetadata
from tests.client_mock import get_async_client_mock, get_client_mock

METADATA_RESPONSE_MOCK = {
    "name": "folder2",
    "parentPath": "folder1",
    "bucket": "test-bucket",
    "url": "files/test/folder1/folder2/",
    "nodeType": "FOLDER",
    "resourceType": "FILE",
    "items": [
        {
            "name": "file.png",
            "parentPath": "folder1/folder2",
            "bucket": "test",
            "url": "files/test/folder1/folder2/file.png",
            "nodeType": "ITEM",
            "resourceType": "FILE",
            "contentLength": 128630,
            "contentType": "image/png",
        }
    ],
}


def test_get_metadata():
    client = get_client_mock(status_code=200, json_mock=METADATA_RESPONSE_MOCK)
    client._get_my_bucket = Mock(return_value="test-bucket")

    valid_response = client.files.get_metadata(
        url="files/test-bucket/folder1/folder2/"
    )
    valid_response_with_default_bucket = client.files.get_metadata(
        url=client.my_files_home() / "folder1/folder2/"
    )

    for r in [valid_response, valid_response_with_default_bucket]:
        assert isinstance(r, FileMetadata)
        assert r.node_type == "FOLDER"
        assert r.bucket == "test-bucket"
        assert r.items and len(r.items) == 1
        assert r.items[0].node_type == "ITEM"


@pytest.mark.asyncio
async def test_get_metadata_async():
    client = get_async_client_mock(
        status_code=200, json_mock=METADATA_RESPONSE_MOCK
    )
    client._get_my_bucket = AsyncMock(return_value="test-bucket")

    valid_response = await client.files.get_metadata(
        url="files/test-bucket/folder1/folder2/"
    )
    valid_response_with_default_bucket = await client.files.get_metadata(
        url=await client.my_files_home() / "folder1/folder2/"
    )

    for r in [valid_response, valid_response_with_default_bucket]:
        assert isinstance(r, FileMetadata)
        assert r.node_type == "FOLDER"
        assert r.bucket == "test-bucket"
        assert r.items and len(r.items) == 1
        assert r.items[0].node_type == "ITEM"
