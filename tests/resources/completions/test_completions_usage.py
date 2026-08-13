"""Chat completion usage, including the DIAL and reasoning token details"""

import pytest

from tests.resources.completions.conftest import GetCompletion

pytestmark = pytest.mark.asyncio

_TOKENS = {"prompt_tokens": 11, "completion_tokens": 1, "total_tokens": 12}
_PROMPT_TOKENS_DETAILS = {"cached_tokens": 8, "cache_write_tokens": 3}
_COMPLETION_TOKENS_DETAILS = {"reasoning_tokens": 1}


class TestUsage:
    async def test_response_tokens(self, get_completion: GetCompletion):
        completion = await get_completion(usage=_TOKENS)

        assert completion.usage
        assert completion.usage.model_dump(exclude_none=True) == _TOKENS

    async def test_response_prompt_tokens_details(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            usage={**_TOKENS, "prompt_tokens_details": _PROMPT_TOKENS_DETAILS}
        )

        assert completion.usage and completion.usage.prompt_tokens_details
        details = completion.usage.prompt_tokens_details
        assert details.model_dump(exclude_none=True) == _PROMPT_TOKENS_DETAILS

    async def test_response_completion_tokens_details(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            usage={
                **_TOKENS,
                "completion_tokens_details": _COMPLETION_TOKENS_DETAILS,
            }
        )

        assert completion.usage and completion.usage.completion_tokens_details
        details = completion.usage.completion_tokens_details
        assert (
            details.model_dump(exclude_none=True) == _COMPLETION_TOKENS_DETAILS
        )

    async def test_response_without_usage(self, get_completion: GetCompletion):
        completion = await get_completion()

        assert completion.usage is None
