import contextlib
import os
import uuid

import pytest

from aidial_client import AsyncDial, Dial
from aidial_client._exception import ResourceNotFoundError


@pytest.fixture
def dial_url() -> str:
    url = os.getenv("DIAL_URL")
    assert url
    return url


@pytest.fixture
def dial_api_key() -> str:
    api_key = os.getenv("DIAL_API_KEY")
    assert api_key
    return api_key


@pytest.fixture
def sync_client(dial_url, dial_api_key):
    return Dial(base_url=dial_url, api_key=dial_api_key)


@pytest.fixture
def async_client(dial_url, dial_api_key):
    return AsyncDial(base_url=dial_url, api_key=dial_api_key)


@pytest.fixture
def test_deployment(sync_client: Dial) -> str:
    deployments = sync_client.deployments.list()
    assert len(deployments)
    deployment = next(d for d in deployments if d.id.startswith("gpt-"))
    assert deployment
    return deployment.id


@pytest.fixture
def absent_test_file(sync_client):
    def _save_delete_file(p):
        with contextlib.suppress(ResourceNotFoundError):
            sync_client.files.delete(p)

    unique_name = f"test-file-{uuid.uuid4()}.txt"
    full_path = sync_client.my_files_home() / unique_name
    _save_delete_file(full_path)
    yield full_path
    _save_delete_file(full_path)
