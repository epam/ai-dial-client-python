from typing import Literal

from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client.types.deployment import DeploymentBase


class Application(DeploymentBase):
    object: Literal["application"]
    application: str
    application_type_schema_id: str | None = None
    application_properties: dict | None = None
    invalid: bool | None = None


class ApplicationsResponse(ExtraAllowModel):
    data: list[Application]
    object: Literal["list"]
