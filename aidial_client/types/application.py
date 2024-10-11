from typing import Dict, List, Literal, Optional

from aidial_client._internal_types._model import ExtraAllowModel


class Features(ExtraAllowModel):
    rate: Optional[bool] = None
    tokenize: Optional[bool] = None
    truncate_prompt: Optional[bool] = None
    configuration: Optional[bool] = None
    system_prompt: Optional[bool] = None
    tools: Optional[bool] = None
    seed: Optional[bool] = None
    url_attachments: Optional[bool] = None
    folder_attachments: Optional[bool] = None
    allow_resume: Optional[bool] = None


class Application(ExtraAllowModel):
    object: Literal["application"]
    id: str
    description: Optional[str] = None
    application: str
    display_name: Optional[str] = None
    display_version: Optional[str] = None
    icon_url: Optional[str] = None
    reference: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    created_at: int
    updated_at: Optional[int] = None
    features: Features
    input_attachment_types: Optional[List[str]] = None
    defaults: Dict = {}


class ApplicationsResponse(ExtraAllowModel):
    data: List[Application]
    object: Literal["list"]
