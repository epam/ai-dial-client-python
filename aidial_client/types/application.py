from typing import Dict, List, Literal, Optional

from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client.types.deployment import DeploymentBase


class Application(DeploymentBase):
    object: Literal["application"]
    application: str
    application_type_schema_id: Optional[str] = None
    application_properties: Optional[Dict] = None
    invalid: Optional[bool] = None


class ApplicationsResponse(ExtraAllowModel):
    data: List[Application]
    object: Literal["list"]
