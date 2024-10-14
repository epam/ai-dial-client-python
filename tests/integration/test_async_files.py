import os

import pytest

from aidial_client import AsyncDial, DialException
from aidial_client.types.metadata import FileMetadata
from tests.integration.fixtures import *  # type: ignore # noqa

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
    assert isinstance(upload_result, FileMetadata)
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
