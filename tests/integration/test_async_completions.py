import pytest

from aidial_client import AsyncDial
from aidial_client._exception import DialException
from tests.integration.configuration import DIAL_MODEL
from tests.integration.fixtures import *  # noqa


@pytest.mark.asyncio
async def test_async_default_api_version(
    async_client: AsyncDial,
    dial_url: str,
    dial_api_key: str,
    test_deployment: str,
):
    with pytest.raises(DialException):
        await async_client.chat.completions.create(
            deployment_name=DIAL_MODEL,
            stream=False,
            messages=[
                {
                    "role": "system",
                    "content": "2+3=",
                }
            ],
        )
    client_with_default_api_version = AsyncDial(
        base_url=dial_url,
        api_key=dial_api_key,
        api_version="2024-02-15-preview",
    )
    await client_with_default_api_version.chat.completions.create(
        deployment_name=test_deployment,
        stream=False,
        messages=[
            {
                "role": "system",
                "content": "2+3=",
            }
        ],
    )


@pytest.mark.asyncio
async def test_completions_without_streaming(
    async_client: AsyncDial, test_deployment: str
):
    completion = await async_client.chat.completions.create(
        deployment_name=test_deployment,
        stream=False,
        messages=[
            {
                "role": "system",
                "content": "2+3=",
            }
        ],
        api_version="2024-02-15-preview",
    )
    assert completion.choices
    assert completion.choices[0].message
    assert completion.choices[0].message.content
    assert "5" in completion.choices[0].message.content
    assert completion.usage
    assert completion.usage.completion_tokens
    assert completion.usage.prompt_tokens
    assert completion.usage.total_tokens
    assert (
        completion.usage.completion_tokens + completion.usage.prompt_tokens
        == completion.usage.total_tokens
    )


@pytest.mark.asyncio
async def test_completions_with_streaming(async_client: AsyncDial):
    deployments = await async_client.deployments.list()
    assert len(deployments)
    deployment = next(d for d in deployments if d.id.startswith("gpt-"))
    assert deployment
    completion = await async_client.chat.completions.create(
        deployment_name=deployment.id,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": "2+3=",
            }
        ],
        api_version="2024-02-15-preview",
    )
    total_content = ""
    async for chunk in completion:
        assert chunk.choices
        assert chunk.choices[0].delta
        if chunk.choices[0].delta.content:
            total_content += chunk.choices[0].delta.content

    assert "5" in total_content

    last_chunk = chunk
    assert last_chunk.choices[0].finish_reason
    assert last_chunk.usage
    assert last_chunk.usage.total_tokens
    assert last_chunk.usage.prompt_tokens
    assert last_chunk.usage.completion_tokens
    assert (
        last_chunk.usage.completion_tokens + last_chunk.usage.prompt_tokens
        == last_chunk.usage.total_tokens
    )


@pytest.mark.asyncio
async def test_error_during_streaming(
    async_client: AsyncDial, test_deployment: str
):
    completion = await async_client.chat.completions.create(
        deployment_name=test_deployment,
        stream=True,
        messages=[
            {
                "role": "system",
                "content": "2+3=",
            }
        ],
        max_tokens=20,
        api_version="2024-02-15-preview",
    )

    async for chunk in completion:
        print(chunk)
