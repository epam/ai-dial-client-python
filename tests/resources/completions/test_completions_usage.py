"""Chat completion usage, including the DIAL and reasoning token details"""

import pytest

from tests.resources.completions.conftest import GetCompletion

pytestmark = pytest.mark.asyncio


class TestUsage:
    _TOKENS = {"prompt_tokens": 11, "completion_tokens": 1, "total_tokens": 12}

    async def test_response_tokens(self, get_completion: GetCompletion):
        completion = await get_completion(usage=self._TOKENS)

        assert completion.usage
        assert completion.usage.prompt_tokens == 11
        assert completion.usage.completion_tokens == 1
        assert completion.usage.total_tokens == 12
        assert completion.usage.prompt_tokens_details is None
        assert completion.usage.completion_tokens_details is None

    async def test_response_prompt_tokens_details(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            usage={
                **self._TOKENS,
                "prompt_tokens_details": {
                    "cached_tokens": 8,
                    "cache_write_tokens": 3,
                },
            }
        )

        assert completion.usage and completion.usage.prompt_tokens_details
        details = completion.usage.prompt_tokens_details
        assert details.cached_tokens == 8
        assert details.cache_write_tokens == 3

    async def test_response_completion_tokens_details(
        self, get_completion: GetCompletion
    ):
        completion = await get_completion(
            usage={
                **self._TOKENS,
                "completion_tokens_details": {"reasoning_tokens": 1},
            }
        )

        assert completion.usage and completion.usage.completion_tokens_details
        assert completion.usage.completion_tokens_details.reasoning_tokens == 1

    async def test_response_without_usage(self, get_completion: GetCompletion):
        completion = await get_completion()

        assert completion.usage is None
