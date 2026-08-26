from typing import Literal

from typing_extensions import TypedDict


class CacheBreakpointParam(TypedDict, total=False):
    expire_at: str | None


class PromptCacheBreakpointParam(TypedDict):
    mode: Literal["explicit"]


class PromptCacheOptionsParam(TypedDict, total=False):
    mode: Literal["implicit", "explicit"] | None
    ttl: Literal["30m"] | str | None
