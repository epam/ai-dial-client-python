import json
from typing import Optional, Union


def create_mock_chunk(
    *,
    delta: Optional[dict] = None,
    finish_reason: Optional[str] = None,
    usage: Optional[dict] = None,
) -> dict:
    return {
        "id": "chatcmpl-test",
        "choices": [
            {
                "delta": delta or {},
                "finish_reason": finish_reason,
                "index": 0,
                "logprobs": None,
            }
        ],
        "created": 1723806872,
        "model": "gpt-35-turbo",
        "object": "chat.completion.chunk",
        "system_fingerprint": None,
        **({} if usage is None else {"usage": usage}),
    }


def create_sse_data_field(chunk: Union[dict, str]) -> bytes:
    if isinstance(chunk, dict):
        s = json.dumps(chunk)
    else:
        s = chunk
    return f"data: {s}\n\n".encode()
