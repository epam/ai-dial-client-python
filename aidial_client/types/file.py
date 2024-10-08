from pathlib import Path
from typing import Union

import aiofiles
import httpx


class FileDownloadResponse:

    def __init__(self, response: httpx.Response, filename: str):
        self._response = response
        self._filename = filename

    def write_to(self, file: Union[str, Path]) -> None:
        """
        Write the content to a file
        """
        with open(file, "wb") as f:
            for chunk in self._response.iter_bytes():
                f.write(chunk)

    async def awrite_to(self, file: Union[str, Path]) -> None:
        """
        Async write content to a file
        """

        async with aiofiles.open(file, "wb") as f:
            async for chunk in self._response.aiter_bytes():
                await f.write(chunk)

    def __aiter__(self):
        return self._response.aiter_bytes()

    def __iter__(self):
        return self._response.iter_bytes()

    def get_content(self) -> bytes:
        return self._response.read()

    async def aget_content(self) -> bytes:
        return await self._response.aread()

    @property
    def filename(self) -> str:
        return self._filename
