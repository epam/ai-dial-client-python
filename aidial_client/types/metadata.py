from typing import Any, Literal

from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._compatibility.pydantic_v1 import validator
from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client._utils._alias import to_camel

if PYDANTIC_V2:
    from pydantic import field_validator


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


# Fixing the bug in DIAL Core: a non-recursive listing of a skill's files
# reports its subfolders with nodeType "ITEM".
# https://github.com/epam/ai-dial-core/issues/1912
def _node_type_from_url(node_type: Any, url: Any) -> Any:
    if not isinstance(url, str):
        return node_type
    return "FOLDER" if url.endswith("/") else "ITEM"


class SkillItem(ResourceItemMetadata):
    """
    A node in the skills listing: a skill (ITEM) or a grouping folder (FOLDER).

    ``node_type`` is taken from the response as-is. The bug worked around in
    ``SkillFileItem`` was observed only on the file listing inside a skill,
    not on this one.
    """

    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]


class SkillMetadata(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]
    next_token: str | None = None
    items: list[SkillItem] | None = None


class SkillFileItem(ResourceItemMetadata):
    """
    A file or a subfolder inside a skill.

    ``node_type`` is derived from ``url`` rather than taken from the
    response - see ``_node_type_from_url``. A recursive listing is flattened
    and contains no subfolder entries at all, so the two kinds only ever
    appear together in a non-recursive one.

    Sparser than the /v1 files listing: no ``content_length``, no
    ``content_type``, and in observed responses no ``etag`` either.
    Subfolder entries carry no timestamps.
    """

    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]

    if PYDANTIC_V2:

        @field_validator("node_type")
        @classmethod
        def _derive_node_type_v2(cls, value: Any, info: Any) -> Any:
            return _node_type_from_url(value, info.data.get("url"))

    else:

        @validator("node_type")
        def _derive_node_type_v1(  # noqa: N805
            cls, value: Any, values: dict[str, Any]
        ) -> Any:
            return _node_type_from_url(value, values.get("url"))


class SkillFileMetadata(BaseMetadata):
    node_type: Literal["FOLDER", "ITEM"]
    resource_type: Literal["SKILL"]
    next_token: str | None = None
    items: list[SkillFileItem] | None = None

    if PYDANTIC_V2:

        @field_validator("node_type")
        @classmethod
        def _derive_node_type_v2(cls, value: Any, info: Any) -> Any:
            return _node_type_from_url(value, info.data.get("url"))

    else:

        @validator("node_type")
        def _derive_node_type_v1(  # noqa: N805
            cls, value: Any, values: dict[str, Any]
        ) -> Any:
            return _node_type_from_url(value, values.get("url"))
