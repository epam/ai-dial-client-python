import pytest

from aidial_client._exception import DialException
from aidial_client.types.model import ModelCapabilities, ModelInfo, ModelLimits, ModelPricing
from tests.client_mock import get_async_client_mock, get_client_mock

MODEL_MOCK = {
    "id": "gpt-4",
    "model": "gpt-4",
    "display_name": "GPT 4",
    "description": "Chat completion model.",
    "owner": "organization-owner",
    "object": "model",
    "status": "succeeded",
    "created_at": 1672534800,
    "updated_at": 1672534800,
    "lifecycle_status": "generally-available",
    "tokenizer_model": "gpt-4-0314",
    "capabilities": {
        "scale_types": ["standard"],
        "completion": False,
        "chat_completion": True,
        "embeddings": False,
        "fine_tune": False,
        "inference": False,
    },
    "limits": {
        "max_prompt_tokens": 8192,
        "max_completion_tokens": 4096,
    },
    "pricing": {
        "unit": "token",
        "prompt": "0.00003",
        "completion": "0.00006",
    },
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_get_model():
    client = get_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = client.model.get("gpt-4")
    assert isinstance(result, ModelInfo)
    assert result.id == "gpt-4"
    assert result.model == "gpt-4"
    assert result.object == "model"
    assert result.lifecycle_status == "generally-available"


@pytest.mark.asyncio
async def test_async_get_model():
    client = get_async_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = await client.model.get("gpt-4")
    assert isinstance(result, ModelInfo)
    assert result.id == "gpt-4"
    assert result.model == "gpt-4"


# ---------------------------------------------------------------------------
# Nested type fields
# ---------------------------------------------------------------------------


def test_get_model_pricing():
    client = get_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = client.model.get("gpt-4")
    assert isinstance(result.pricing, ModelPricing)
    assert result.pricing.unit == "token"
    assert result.pricing.prompt == "0.00003"
    assert result.pricing.completion == "0.00006"


def test_get_model_limits_prompt_and_completion():
    client = get_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = client.model.get("gpt-4")
    assert isinstance(result.limits, ModelLimits)
    assert result.limits.max_prompt_tokens == 8192
    assert result.limits.max_completion_tokens == 4096
    assert result.limits.max_total_tokens is None


def test_get_model_limits_total_tokens():
    mock = {**MODEL_MOCK, "limits": {"max_total_tokens": 16384}}
    client = get_client_mock(status_code=200, json_mock=mock)
    result = client.model.get("gpt-4")
    assert isinstance(result.limits, ModelLimits)
    assert result.limits.max_total_tokens == 16384
    assert result.limits.max_prompt_tokens is None


def test_get_model_capabilities():
    client = get_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = client.model.get("gpt-4")
    assert isinstance(result.capabilities, ModelCapabilities)
    assert result.capabilities.chat_completion is True
    assert result.capabilities.embeddings is False
    assert result.capabilities.scale_types == ["standard"]


def test_get_model_tokenizer_model():
    client = get_client_mock(status_code=200, json_mock=MODEL_MOCK)
    result = client.model.get("gpt-4")
    assert result.tokenizer_model == "gpt-4-0314"


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_get_model_no_pricing():
    mock = {**MODEL_MOCK}
    del mock["pricing"]
    client = get_client_mock(status_code=200, json_mock=mock)
    result = client.model.get("gpt-4")
    assert result.pricing is None


def test_get_model_embedding_no_completion_price():
    mock = {
        **MODEL_MOCK,
        "id": "ada-002",
        "model": "ada-002",
        "pricing": {"unit": "token", "prompt": "0.0000001"},
    }
    client = get_client_mock(status_code=200, json_mock=mock)
    result = client.model.get("ada-002")
    assert isinstance(result.pricing, ModelPricing)
    assert result.pricing.completion is None


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_get_model_http_error():
    client = get_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        client.model.get("gpt-4")


@pytest.mark.asyncio
async def test_async_get_model_http_error():
    client = get_async_client_mock(
        status_code=401,
        json_mock={"error": {"message": "Unauthorized", "type": "auth_error"}},
    )
    with pytest.raises(DialException):
        await client.model.get("gpt-4")
