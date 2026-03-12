from typing import Dict, List, Literal, Optional

from aidial_client._internal_types._model import ExtraAllowModel


class ScaleSettings(ExtraAllowModel):
    scale_type: Literal["standard"]


class Features(ExtraAllowModel):
    rate: Optional[bool] = None
    tokenize: Optional[bool] = None
    temperature: Optional[bool] = None
    truncate_prompt: Optional[bool] = None
    configuration: Optional[bool] = None
    system_prompt: Optional[bool] = None
    tools: Optional[bool] = None
    seed: Optional[bool] = None
    url_attachments: Optional[bool] = None
    folder_attachments: Optional[bool] = None
    allow_resume: Optional[bool] = None
    parallel_tool_calls: Optional[bool] = None


class DeploymentBase(ExtraAllowModel):
    id: str
    object: str
    owner: Optional[str] = None
    reference: Optional[str] = None
    icon_url: Optional[str] = None
    description: Optional[str] = None
    display_name: Optional[str] = None
    display_version: Optional[str] = None
    status: Optional[str] = None
    created_at: int
    updated_at: Optional[int] = None
    scale_settings: Optional[ScaleSettings] = None
    defaults: Dict = {}
    input_attachment_types: Optional[List[str]] = None
    features: Optional[Features] = None


class Deployment(DeploymentBase):
    object: Literal["deployment", "model"]
    model: str


class DeploymentsResponse(ExtraAllowModel):
    data: List[Deployment]
    object: Literal["list"]


class DeploymentConfig(ExtraAllowModel):
    """JSON Schema document returned by GET /v1/deployments/{id}/configuration.

    No fields are pinned because the schema is entirely deployment-specific
    and callers are expected to access fields dynamically (e.g. via
    model.model_extra or model_dump()). The named type exists so that:
    - http_client.request(cast_to=DeploymentConfig) can deserialise the response;
    - the public API carries a meaningful return type rather than a bare dict;
    - common top-level fields (e.g. 'type', '$schema') can be pinned here
      in a future non-breaking change.
    """
