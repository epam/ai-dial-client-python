from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client.types.deployment import Features


class ToolsetInfo(ExtraAllowModel):
    id: str
    toolset: str
    display_name: str | None = None
    display_version: str | None = None
    description: str | None = None
    icon_url: str | None = None
    owner: str | None = None
    object: str | None = None
    status: str | None = None
    created_at: int | None = None
    updated_at: int | None = None
    reference: str | None = None
    description_keywords: list[str] = []
    max_retry_attempts: int | None = None
    transport: str | None = None
    allowed_tools: list[str] = []
    features: Features | None = None
