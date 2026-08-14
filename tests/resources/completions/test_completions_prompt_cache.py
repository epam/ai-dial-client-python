"""Prompt caching request fields"""

from typing import Any

import pytest

from tests.resources.completions.conftest import GetRequestBody

pytestmark = pytest.mark.asyncio


class TestPromptCache:
    """Prompt cache options must reach the request body as-is"""

    async def test_request_prompt_cache_key(
        self, get_request_body: GetRequestBody
    ):
        body = await get_request_body(prompt_cache_key="user-42")

        assert body["prompt_cache_key"] == "user-42"

    async def test_request_prompt_cache_options(
        self, get_request_body: GetRequestBody
    ):
        body = await get_request_body(
            prompt_cache_options={"mode": "explicit", "ttl": "30m"}
        )

        assert body["prompt_cache_options"]["mode"] == "explicit"
        assert body["prompt_cache_options"]["ttl"] == "30m"

    @pytest.mark.parametrize(
        "part",
        [
            {"type": "text", "text": "What is on the picture?"},
            {"type": "image_url", "image_url": {"url": "http://a.com/b.png"}},
            {"type": "file", "file": {"file_id": "files/bucket/a.pdf"}},
            {
                "type": "input_audio",
                "input_audio": {"data": "Zm9v", "format": "wav"},
            },
        ],
        ids=["text", "image_url", "file", "input_audio"],
    )
    async def test_request_content_part_breakpoint(
        self, get_request_body: GetRequestBody, part: dict[str, Any]
    ):
        body = await get_request_body(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            **part,
                            "prompt_cache_breakpoint": {"mode": "explicit"},
                        }
                    ],
                }
            ]
        )

        sent_part = body["messages"][0]["content"][0]
        assert sent_part["prompt_cache_breakpoint"] == {"mode": "explicit"}
