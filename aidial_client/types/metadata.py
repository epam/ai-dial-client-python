from typing import Literal

from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client._utils._alias import to_camel


class BaseMetadata(ExtraAllowModel):
    if PYDANTIC_V2:
        model_config = {
            "alias_generator": to_camel,
            "populate_by_name": True,
        }
    else:

        class Config:
            alias_generator = to_camel
            allow_population_by_field_name = True

    name: str | None = None
    parent_path: str | None = None
    bucket: str
    url: str
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["FILE", "CONVERSATION", "PROMPT"]


class FileItem(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["FILE"]
    content_length: int | None = None
    content_type: str | None = None


class FileMetadata(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["FILE"]
    content_length: int | None = None
    content_type: str | None = None
    next_token: str | None = None
    items: list[FileItem] | None = None
    etag: str | None = None


class ConversationItem(BaseMetadata):
    updated_at: int
    resource_type: Literal["CONVERSATION"]


class ConversationMetadata(BaseMetadata):
    content_length: int | None = None
    next_token: str | None = None
    items: list[ConversationItem] | None
    resource_type: Literal["CONVERSATION"]


class PromptItem(BaseMetadata):
    updated_at: int
    resource_type: Literal["PROMPT"]


class PromptMetadata(BaseMetadata):
    content_length: int | None = None
    next_token: str | None = None
    items: list[PromptItem] | None
    resource_type: Literal["PROMPT"]
