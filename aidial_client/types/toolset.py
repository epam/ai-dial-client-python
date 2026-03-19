from typing import List, Optional

from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client.types.deployment import Features


class ToolsetInfo(ExtraAllowModel):
    id: str
    toolset: str
    display_name: Optional[str] = None
    display_version: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    owner: Optional[str] = None
    object: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    reference: Optional[str] = None
    description_keywords: List[str] = []
    max_retry_attempts: Optional[int] = None
    transport: Optional[str] = None
    allowed_tools: List[str] = []
    features: Optional[Features] = None
