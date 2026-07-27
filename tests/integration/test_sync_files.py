import os

import pytest

from aidial_client import Dial, DialException
from aidial_client._exception import EtagMismatchError
from aidial_client.types.metadata import FileItem

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
    assert isinstance(upload_result, FileItem)
    assert upload_result.bucket == sync_client.my_bucket()
    assert upload_result.node_type == "ITEM"
    assert upload_result.name == file_name
    assert upload_result.parent_path == file_path.split("/")[0]

    # Download file, and compare it's content
    download_result = sync_client.files.download(
        url=sync_client.my_files_home() / file_path
    )
    assert b"".join(list(download_result)) == file_content
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


def test_etag_in_response(sync_client, absent_test_file):
    upload_response = sync_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    assert upload_response.etag is not None
    first_etag = upload_response.etag

    upload_response = sync_client.files.upload(
        url=absent_test_file, file=b"test 2"
    )
    assert upload_response.etag is not None
    second_etag = upload_response.etag

    assert first_etag != second_etag


def test_upload_with_etag_if_match(sync_client, absent_test_file):
    upload_response = sync_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    first_etag = upload_response.etag

    upload_response = sync_client.files.upload(
        url=absent_test_file,
        file=b"test 2",
        etag_if_match=first_etag,
    )
    assert upload_response.etag != first_etag

    with pytest.raises(EtagMismatchError):
        sync_client.files.upload(
            url=absent_test_file,
            file=b"test 3",
            etag_if_match="invalid_etag",
        )


def test_upload_with_etag_if_none_match(sync_client, absent_test_file):
    sync_client.files.upload(
        url=absent_test_file, file=b"test 1", etag_if_none_match="*"
    )

    with pytest.raises(EtagMismatchError):
        sync_client.files.upload(
            url=absent_test_file, file=b"test 2", etag_if_none_match="*"
        )


def test_delete_with_etag(sync_client, absent_test_file):
    upload_response = sync_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    etag = upload_response.etag

    with pytest.raises(EtagMismatchError):
        sync_client.files.delete(
            url=absent_test_file,
            etag_if_match="invalid_etag",
        )

    sync_client.files.delete(
        url=absent_test_file,
        etag_if_match=etag,
    )


def test_download_with_etag(sync_client, absent_test_file):
    upload_response = sync_client.files.upload(
        url=absent_test_file,
        file=b"test 1",
    )
    etag = upload_response.etag

    download_result = sync_client.files.download(
        url=absent_test_file,
        etag_if_match=etag,
    )
    assert download_result.get_content() == b"test 1"

    with pytest.raises(EtagMismatchError):
        sync_client.files.download(
            url=absent_test_file,
            etag_if_match="invalid_etag",
        )
