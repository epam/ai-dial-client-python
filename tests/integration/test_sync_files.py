import os

import pytest

from aidial_client import Dial, DialException
from aidial_client.types.metadata import FileMetadata
from tests.integration.fixtures import *  # type: ignore # noqa

current_file_path = os.path.abspath(__file__)
file_name = "test-file"
file_path = f"test-folder-artifacts/{file_name}"


def test_upload(sync_client: Dial):
    file_content = b""

    # Upload file
    with open(current_file_path, "rb") as file:
        file_content = file.read()
        upload_result = sync_client.files.upload(
            url=sync_client.my_files_home() / file_path, file=file
        )
    assert isinstance(upload_result, FileMetadata)
    assert upload_result.bucket == sync_client.my_bucket()
    assert upload_result.node_type == "ITEM"
    assert upload_result.name == file_name
    assert upload_result.parent_path == file_path.split("/")[0]

    # Download file, and compare it's content
    download_result = sync_client.files.download(
        url=sync_client.my_files_home() / file_path
    )
    assert b"".join([chunk for chunk in download_result]) == file_content
    assert download_result.get_content() == file_content


def test_delete(sync_client):
    # Upload file
    with open(current_file_path, "rb") as file:
        sync_client.files.upload(
            url=sync_client.my_files_home() / file_path, file=file
        )

    metadata = sync_client.files.get_metadata(
        url=sync_client.my_files_home() / file_path
    )
    assert metadata.node_type == "ITEM"
    # Delete file
    sync_client.files.delete(url=sync_client.my_files_home() / file_path)

    # Try to access metadata
    with pytest.raises(DialException):
        sync_client.files.get_metadata(
            url=sync_client.my_files_home() / file_path
        )
    # Try to access content
    with pytest.raises(DialException):
        sync_client.files.download(url=sync_client.my_files_home() / file_path)
