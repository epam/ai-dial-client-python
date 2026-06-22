from typing import Literal

from aidial_client._internal_types._model import ExtraAllowModel


class ScaleSettings(ExtraAllowModel):
    scale_type: Literal["standard"]


class Features(ExtraAllowModel):
    rate: bool | None = None
    tokenize: bool | None = None
    temperature: bool | None = None
    truncate_prompt: bool | None = None
    configuration: bool | None = None
    system_prompt: bool | None = None
    tools: bool | None = None
    seed: bool | None = None
    url_attachments: bool | None = None
    folder_attachments: bool | None = None
    allow_resume: bool | None = None
    parallel_tool_calls: bool | None = None
    accessible_by_per_request_key: bool | None = None
    content_parts: bool | None = None
    cache: bool | None = None
    auto_caching: bool | None = None
    assistant_attachments_in_request: bool | None = None
    mcp: bool | None = None


class DeploymentBase(ExtraAllowModel):
    id: str
    object: str
    owner: str | None = None
    reference: str | None = None
    icon_url: str | None = None
    description: str | None = None
    display_name: str | None = None
    display_version: str | None = None
    status: str | None = None
    created_at: int
    updated_at: int | None = None
    scale_settings: ScaleSettings | None = None
    defaults: dict = {}
    input_attachment_types: list[str] | None = None
    features: Features | None = None


class Deployment(DeploymentBase):
    object: Literal["deployment", "model"]
    model: str


class DeploymentsResponse(ExtraAllowModel):
    data: list[Deployment]
    object: Literal["list"]
