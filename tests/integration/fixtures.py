import os

import pytest

from aidial_client import AsyncDial, Dial


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
    deployments = sync_client.deployments.get()
    assert len(deployments)
    deployment = next((d for d in deployments if d.id.startswith("gpt-")))
    assert deployment
    return deployment.id
