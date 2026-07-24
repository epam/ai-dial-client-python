import os

import pytest

from aidial_client import AsyncDial, DialException
from aidial_client._exception import EtagMismatchError
from aidial_client.types.metadata import FileItem

current_file_path = os.path.abspath(__file__)
file_name = "test-file-async"
file_path = f"test-folder-artifacts/{file_name}"


@pytest.mark.asyncio
async def test_upload(async_client: AsyncDial):
    # Upload file
    with open(current_file_path, "rb") as file:
        file_content = file.read()
        upload_result = await async_client.files.upload(
            url=await async_client.my_files_home() / file_path, file=file
        )
    assert isinstance(upload_result, FileItem)
    assert upload_result.bucket == await async_client.my_bucket()
    assert upload_result.node_type == "ITEM"
    assert upload_result.name == file_name
    assert upload_result.parent_path == file_path.split("/")[0]

    # Download file, and compare it's content
    download_result = await async_client.files.download(
        url=await async_client.my_files_home() / file_path
    )

    assert b"".join([chunk async for chunk in download_result]) == file_content
    assert await download_result.aget_content() == file_content


@pytest.mark.asyncio
async def test_delete(async_client: AsyncDial):
    # Upload file
    with open(current_file_path, "rb") as file:
        await async_client.files.upload(
            url=await async_client.my_files_home() / file_path, file=file
        )

    metadata = await async_client.files.get_metadata(
        url=await async_client.my_files_home() / file_path
    )
    assert metadata.node_type == "ITEM"
    # Delete file
    await async_client.files.delete(
        url=await async_client.my_files_home() / file_path
    )

    # Try to access metadata
    with pytest.raises(DialException):
        await async_client.files.get_metadata(
            url=await async_client.my_files_home() / file_path
        )
    # Try to access content
    with pytest.raises(DialException):
        await async_client.files.download(
            url=await async_client.my_files_home() / file_path
        )


@pytest.mark.asyncio
async def test_etag_in_response(async_client, absent_test_file):
    upload_response = await async_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    assert upload_response.etag is not None
    first_etag = upload_response.etag

    upload_response = await async_client.files.upload(
        url=absent_test_file, file=b"test 2"
    )
    assert upload_response.etag is not None
    second_etag = upload_response.etag

    assert first_etag != second_etag


@pytest.mark.asyncio
async def test_upload_with_etag_if_match(async_client, absent_test_file):
    upload_response = await async_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    first_etag = upload_response.etag

    upload_response = await async_client.files.upload(
        url=absent_test_file,
        file=b"test 2",
        etag_if_match=first_etag,
    )
    assert upload_response.etag != first_etag

    with pytest.raises(EtagMismatchError):
        await async_client.files.upload(
            url=absent_test_file,
            file=b"test 3",
            etag_if_match="invalid_etag",
        )


@pytest.mark.asyncio
async def test_upload_with_etag_if_none_match(async_client, absent_test_file):
    await async_client.files.upload(
        url=absent_test_file,
        file=b"test 1",
        etag_if_none_match="*",
    )

    with pytest.raises(EtagMismatchError):
        await async_client.files.upload(
            url=absent_test_file,
            file=b"test 2",
            etag_if_none_match="*",
        )


@pytest.mark.asyncio
async def test_delete_with_etag(async_client, absent_test_file):
    upload_response = await async_client.files.upload(
        url=absent_test_file, file=b"test 1"
    )
    etag = upload_response.etag

    with pytest.raises(EtagMismatchError):
        await async_client.files.delete(
            url=absent_test_file,
            etag_if_match="invalid_etag",
        )

    await async_client.files.delete(
        url=absent_test_file,
        etag_if_match=etag,
    )


@pytest.mark.asyncio
async def test_download_with_etag(async_client, absent_test_file):
    upload_response = await async_client.files.upload(
        url=absent_test_file,
        file=b"test 1",
    )
    etag = upload_response.etag

    download_result = await async_client.files.download(
        url=absent_test_file,
        etag_if_match=etag,
    )
    assert await download_result.aget_content() == b"test 1"

    with pytest.raises(EtagMismatchError):
        await async_client.files.download(
            url=absent_test_file,
            etag_if_match="invalid_etag",
        )
