from typing import Any, Dict, Optional

from aidial_client._internal_types._model import ExtraAllowModel


class ModelInfo(ExtraAllowModel):
    id: str
    model: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[str] = None
    object: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    lifecycle_status: Optional[str] = None
    capabilities: Optional[Dict[str, Any]] = None
