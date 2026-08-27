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
    resource_type: Literal["FILE", "CONVERSATION", "PROMPT", "SKILL"]


class ResourceItemMetadata(BaseMetadata):
    created_at: int | None = None
    updated_at: int | None = None
    etag: str | None = None
    author: str | None = None


class FileItem(ResourceItemMetadata):
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


class ConversationItem(ResourceItemMetadata):
    resource_type: Literal["CONVERSATION"]


class ConversationMetadata(BaseMetadata):
    content_length: int | None = None
    next_token: str | None = None
    items: list[ConversationItem] | None
    resource_type: Literal["CONVERSATION"]


class PromptItem(ResourceItemMetadata):
    resource_type: Literal["PROMPT"]


class PromptMetadata(BaseMetadata):
    content_length: int | None = None
    next_token: str | None = None
    items: list[PromptItem] | None
    resource_type: Literal["PROMPT"]


class SkillItem(ResourceItemMetadata):
    """
    A node in the skills listing: a skill (ITEM) or a grouping folder (FOLDER).

    DIAL Core builds these from the folder marker's listing metadata without
    reading the marker body, so no ``etag`` and no skill name/description are
    carried here - they are available via a whole-resource GET.
    """

    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]


class SkillMetadata(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]
    next_token: str | None = None
    items: list[SkillItem] | None = None


class SkillFileItem(ResourceItemMetadata):
    """A file (ITEM) or a subfolder (FOLDER) inside a skill."""

    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]
    content_length: int | None = None
    content_type: str | None = None


class SkillFileMetadata(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]
    next_token: str | None = None
    items: list[SkillFileItem] | None = None
