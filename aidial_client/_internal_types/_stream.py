import json
from typing import Any, Optional

from aidial_client._exception import DialException


class ServerSentEvent:
    def __init__(
        self,
        *,
        event: Optional[str],
        data: str,
        id: Optional[str],
        retry: Optional[int],
    ) -> None:
        self._id = id
        self._data = data
        self._event = event or None
        self._retry = retry

    @property
    def event(self) -> Optional[str]:
        return self._event

    @property
    def id(self) -> Optional[str]:
        return self._id

    @property
    def retry(self) -> Optional[int]:
        return self._retry

    @property
    def data(self) -> str:
        return self._data

    def json(self) -> Any:
        try:
            return json.loads(self.data)
        except json.JSONDecodeError:
            raise DialException(
                message=f"Could not parse server event correctly {self.data}"
            )

    def __repr__(self) -> str:
        return (
            f"ServerSentEvent("
            f"event={self.event!r},"
            f"data={self.data!r},"
            f"id={self.id!r},"
            f"retry={self.retry!r})"
        )
