from typing_extensions import TypedDict


class CacheBreakpointParam(TypedDict, total=False):
    expire_at: str | None
