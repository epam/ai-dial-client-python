import pytest

from aidial_client._exception import DialException
from aidial_client.types.deployment import Deployment
from tests.client_mock import get_async_client_mock, get_client_mock

DEPLOYMENT_MOCK = {
    "id": "gpt-4",
    "model": "gpt-4",
    "object": "deployment",
    "owner": "organization-owner",
    "status": "succeeded",
    "created_at": 1672534800,
    "updated_at": 1672534800,
    "scale_settings": {"scale_type": "standard"},
}

CONFIG_MOCK = {
    "type": "object",
    "properties": {
        "model_to_use": {
            "type": "string",
            "enum": ["gpt-4", "gpt-4o"],
            "default": "gpt-4",
        }
    },
    "additionalProperties": False,
}


def test_get_deployment():
    client = get_client_mock(status_code=200, json_mock=DEPLOYMENT_MOCK)
    result = client.deployments.get("gpt-4")
    assert isinstance(result, Deployment)
    assert result.id == "gpt-4"
    assert result.model == "gpt-4"
    assert result.object == "deployment"


@pytest.mark.asyncio
async def test_async_get_deployment():
    client = get_async_client_mock(status_code=200, json_mock=DEPLOYMENT_MOCK)
    result = await client.deployments.get("gpt-4")
    assert isinstance(result, Deployment)
    assert result.id == "gpt-4"
    assert result.model == "gpt-4"
    assert result.object == "deployment"


def test_get_deployment_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        client.deployments.get("gpt-4")


@pytest.mark.asyncio
async def test_async_get_deployment_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        await client.deployments.get("gpt-4")


def test_get_deployment_config():
    client = get_client_mock(status_code=200, json_mock=CONFIG_MOCK)
    result = client.deployments.get_configuration_schema("gpt-4")
    assert isinstance(result, dict)
    assert result.get("type") == "object"
    assert "properties" in result


@pytest.mark.asyncio
async def test_async_get_deployment_config():
    client = get_async_client_mock(status_code=200, json_mock=CONFIG_MOCK)
    result = await client.deployments.get_configuration_schema("gpt-4")
    assert isinstance(result, dict)
    assert result.get("type") == "object"
    assert "properties" in result


def test_get_deployment_config_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        client.deployments.get_configuration_schema("gpt-4")


@pytest.mark.asyncio
async def test_async_get_deployment_config_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        await client.deployments.get_configuration_schema("gpt-4")
