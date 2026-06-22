from collections.abc import AsyncIterator, Iterator

from aidial_client._log import logger

_UNCOMMITTED_BUFFER_WARNING = (
    "Uncommitted data chunks in SSE stream "
    "(stream ended without a terminating blank line); discarding."
)


def _strip_field(line: str, prefix: str) -> str:
    """
    Strip a single leading U+0020 SPACE after the field colon, per the SSE spec.
    """
    value = line[len(prefix) :]
    return value.removeprefix(" ")


def iter_data_events(lines: Iterator[str]) -> Iterator[str]:
    """
    Yield the payload of each complete ``data:`` event from an SSE line stream.

    An event is complete when a blank line follows the ``data:`` line(s). Per
    the SSE dispatch rule, a buffer that has not been terminated by a blank
    line is discarded (we do NOT flush partial events at end of stream).
    Comment lines (``:``) and other field names are ignored.
    """
    buffer: list[str] = []
    for line in lines:
        if line == "":
            if buffer:
                yield "\n".join(buffer)
                buffer = []
        elif line.startswith("data:"):
            buffer.append(_strip_field(line, "data:"))
    if buffer:
        logger.warning(_UNCOMMITTED_BUFFER_WARNING)


async def aiter_data_events(lines: AsyncIterator[str]) -> AsyncIterator[str]:
    buffer: list[str] = []
    async for line in lines:
        if line == "":
            if buffer:
                yield "\n".join(buffer)
                buffer = []
        elif line.startswith("data:"):
            buffer.append(_strip_field(line, "data:"))
    if buffer:
        logger.warning(_UNCOMMITTED_BUFFER_WARNING)
