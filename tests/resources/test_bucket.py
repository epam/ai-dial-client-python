import pytest

from aidial_client.types.bucket import BucketResponse
from tests.client_mock import get_async_client_mock, get_client_mock


def test_get_bucket():
    client = get_client_mock(status_code=200, json_mock={"bucket": "test"})

    raw_response = client.bucket.get_raw()
    assert isinstance(raw_response, BucketResponse)
    assert client.bucket.get_bucket() == raw_response.bucket == "test"


@pytest.mark.asyncio
async def test_async_get_bucket():
    async_client = get_async_client_mock(
        status_code=200, json_mock={"bucket": "test"}
    )
    raw_response = await async_client.bucket.get_raw()
    assert isinstance(raw_response, BucketResponse)
    assert (
        await async_client.bucket.get_bucket() == raw_response.bucket == "test"
    )


def test_get_appdata():
    client = get_client_mock(status_code=200, json_mock={"bucket": "test"})
    assert not client.bucket.get_appdata()
    client = get_client_mock(
        status_code=200,
        json_mock={
            "bucket": "test",
            "appdata": "test-bucket/appdata/dall-e-3",
        },
    )
    appdata = client.bucket.get_appdata()
    assert appdata
    assert appdata.app_name == "dall-e-3"
    assert appdata.user_bucket == "test-bucket"


@pytest.mark.asyncio
async def test_async_get_appdata():
    client = get_async_client_mock(
        status_code=200, json_mock={"bucket": "test"}
    )
    assert not await client.bucket.get_appdata()
    client = get_async_client_mock(
        status_code=200,
        json_mock={
            "bucket": "test",
            "appdata": "test-bucket/appdata/dall-e-3",
        },
    )
    appdata = await client.bucket.get_appdata()
    assert appdata
    assert appdata.app_name == "dall-e-3"
    assert appdata.user_bucket == "test-bucket"
