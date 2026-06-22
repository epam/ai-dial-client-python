import httpx
import pytest
from pydantic import ValidationError

from aidial_client.types.chat.response import Attachment
from aidial_client.types.file import FileDownloadResponse
from aidial_client.types.metadata import BaseMetadata


@pytest.mark.parametrize(
    "invalid_attachment",
    [
        {},
        {"reference_type": "test"},
        {"reference_url": "test"},
    ],
)
def test_invalid_attachment(invalid_attachment):
    with pytest.raises(ValidationError):
        Attachment(**invalid_attachment)


@pytest.mark.parametrize(
    "valid_attachment",
    [
        {"data": "test"},
        {"url": "test"},
        {"data": "test", "url": "test"},
        {"data": "test", "reference_type": "test", "reference_url": "test"},
    ],
)
def test_valid_attachment(valid_attachment):
    attachment = Attachment(**valid_attachment)
    for key, value in valid_attachment.items():
        assert getattr(attachment, key) == value


def test_metadata_population():
    metadata_by_name = BaseMetadata(
        name="test",
        bucket="test",
        url="test",
        node_type="FOLDER",
        resource_type="FILE",
    )
    alias_json = {
        "name": "test",
        "bucket": "test",
        "url": "test",
        "nodeType": "FOLDER",
        "resourceType": "FILE",
    }
    metadata_by_alias = BaseMetadata(**alias_json)  # type: ignore

    for field in BaseMetadata.__annotations__:
        assert getattr(metadata_by_name, field) == getattr(
            metadata_by_alias, field
        )


def test_file_download_response_metadata():
    response = httpx.Response(
        200,
        content=b"test content",
        headers={"content-type": "text/plain", "x-test-header": "test"},
    )

    download_response = FileDownloadResponse(
        response=response, filename="test.txt"
    )

    assert download_response.headers["x-test-header"] == "test"
    assert download_response.content_type == "text/plain"


def test_file_download_response_metadata_without_content_type():
    response = httpx.Response(200, content=b"test content")
    download_response = FileDownloadResponse(
        response=response, filename="test.txt"
    )

    assert download_response.content_type is None
