from typing import Union

from typing_extensions import TypedDict


class ExternalAddon(TypedDict):
    # The URL for accessing the OpenAI Plugin Schema.
    # The system object used for converting the Addon name to the Addon link.
    url: str


class SystemAddon(TypedDict):
    # The name of the system Addon.
    name: str


Addon = Union[ExternalAddon, SystemAddon]
