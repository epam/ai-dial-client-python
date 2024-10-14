import pytest

from aidial_client import Dial
from aidial_client._exception import DialException
from tests.integration.fixtures import *  # type: ignore # noqa


def test_completions_without_streaming(sync_client: Dial, test_deployment: str):
    completion = sync_client.chat.completions.create(
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


def test_default_api_version(
    sync_client: Dial, dial_url: str, dial_api_key: str
):
    with pytest.raises(DialException):
        sync_client.chat.completions.create(
            deployment_name="gpt-35-turbo",
            stream=False,
            messages=[
                {
                    "role": "system",
                    "content": "2+3=",
                }
            ],
        )
    client_with_default_api_version = Dial(
        base_url=dial_url,
        api_key=dial_api_key,
        api_version="2024-02-15-preview",
    )
    client_with_default_api_version.chat.completions.create(
        deployment_name="gpt-35-turbo",
        stream=False,
        messages=[
            {
                "role": "system",
                "content": "2+3=",
            }
        ],
    )


def test_completions_with_streaming(sync_client: Dial):
    deployments = sync_client.deployments.list()
    assert len(deployments)
    deployment = next((d for d in deployments if d.id.startswith("gpt-")))
    assert deployment
    completion = sync_client.chat.completions.create(
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
    for chunk in completion:
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
