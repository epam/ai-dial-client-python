from typing import List, Literal, Optional

from aidial_client._internal_types._model import ExtraAllowModel


class ScaleSettings(ExtraAllowModel):
    scale_type: Literal["standard"]


class Deployment(ExtraAllowModel):
    id: str
    model: str
    owner: str
    object: Literal["deployment"]
    status: Literal["succeeded"]
    created_at: int
    updated_at: int
    scale_settings: Optional[ScaleSettings] = None


class DeploymentsResponse(ExtraAllowModel):
    data: List[Deployment]
    object: Literal["list"]
