import uuid

import pytest

from aidial_client import AsyncDial
from aidial_client._exception import EtagMismatchError, ResourceNotFoundError
from aidial_client.types.metadata import PromptMetadata
from aidial_client.types.prompt import Prompt
from tests.integration.fixtures import *  # type: ignore # noqa

PROMPT_FOLDER = "test-folder-artifacts"


async def _delete_if_exists(async_client: AsyncDial, url: str) -> None:
    try:
        await async_client.prompts.delete(url)
    except ResourceNotFoundError:
        pass


def _create_prompt(
    url: str, content: str = "You are a helpful assistant."
) -> Prompt:
    path_parts = url.split("/")
    name = path_parts[-1]
    folder_id = "/".join(path_parts[2:-1])
    return Prompt(id=url, name=name, folder_id=folder_id, content=content)


def _get_etag_or_skip(metadata: PromptMetadata) -> str:
    etag = getattr(metadata, "etag", None)
    if not etag:
        pytest.skip("Prompt metadata does not include etag in this environment")
    return etag


@pytest.mark.asyncio
async def test_save_get_delete(async_client: AsyncDial):
    prompt_name = f"test-prompt-{uuid.uuid4()}"
    prompt_url = str(
        await async_client.my_prompts_home() / f"{PROMPT_FOLDER}/{prompt_name}"
    )
    await _delete_if_exists(async_client, prompt_url)

    save_result = await async_client.prompts.save(
        url=prompt_url, prompt=_create_prompt(prompt_url)
    )
    assert isinstance(save_result, PromptMetadata)
    assert save_result.node_type == "ITEM"
    assert save_result.bucket == await async_client.my_bucket()
    assert save_result.name == prompt_name

    prompt = await async_client.prompts.get(prompt_url)
    assert prompt.name == prompt_name
    assert prompt.content == "You are a helpful assistant."

    await async_client.prompts.delete(prompt_url)
    with pytest.raises(ResourceNotFoundError):
        await async_client.prompts.get(prompt_url)


@pytest.mark.asyncio
async def test_save_with_etag_if_match(async_client: AsyncDial):
    prompt_name = f"test-prompt-{uuid.uuid4()}"
    prompt_url = str(
        await async_client.my_prompts_home() / f"{PROMPT_FOLDER}/{prompt_name}"
    )
    await _delete_if_exists(async_client, prompt_url)

    first_save = await async_client.prompts.save(
        url=prompt_url, prompt=_create_prompt(prompt_url, content="v1")
    )
    first_etag = _get_etag_or_skip(first_save)

    second_save = await async_client.prompts.save(
        url=prompt_url,
        prompt=_create_prompt(prompt_url, content="v2"),
        etag_if_match=first_etag,
    )
    assert _get_etag_or_skip(second_save) != first_etag

    with pytest.raises(EtagMismatchError):
        await async_client.prompts.save(
            url=prompt_url,
            prompt=_create_prompt(prompt_url, content="v3"),
            etag_if_match="invalid_etag",
        )


@pytest.mark.asyncio
async def test_save_with_etag_if_none_match(async_client: AsyncDial):
    prompt_name = f"test-prompt-{uuid.uuid4()}"
    prompt_url = str(
        await async_client.my_prompts_home() / f"{PROMPT_FOLDER}/{prompt_name}"
    )
    await _delete_if_exists(async_client, prompt_url)

    await async_client.prompts.save(
        url=prompt_url,
        prompt=_create_prompt(prompt_url),
        etag_if_none_match="*",
    )

    with pytest.raises(EtagMismatchError):
        await async_client.prompts.save(
            url=prompt_url,
            prompt=_create_prompt(prompt_url, content="v2"),
            etag_if_none_match="*",
        )


@pytest.mark.asyncio
async def test_delete_with_etag(async_client: AsyncDial):
    prompt_name = f"test-prompt-{uuid.uuid4()}"
    prompt_url = str(
        await async_client.my_prompts_home() / f"{PROMPT_FOLDER}/{prompt_name}"
    )
    await _delete_if_exists(async_client, prompt_url)

    save_result = await async_client.prompts.save(
        url=prompt_url, prompt=_create_prompt(prompt_url)
    )
    etag = _get_etag_or_skip(save_result)

    with pytest.raises(EtagMismatchError):
        await async_client.prompts.delete(
            url=prompt_url,
            etag_if_match="invalid_etag",
        )

    await async_client.prompts.delete(
        url=prompt_url,
        etag_if_match=etag,
    )
