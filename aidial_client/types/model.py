from typing import List, Optional

from aidial_client._internal_types._model import ExtraAllowModel


class ModelCapabilities(ExtraAllowModel):
    scale_types: List[str] = []
    completion: Optional[bool] = None
    chat_completion: Optional[bool] = None
    embeddings: Optional[bool] = None
    fine_tune: Optional[bool] = None
    inference: Optional[bool] = None


class ModelLimits(ExtraAllowModel):
    """Token limits for the model.

    Either `max_total_tokens` is set alone, or `max_prompt_tokens` and
    `max_completion_tokens` are set together (oneOf in the schema).
    All fields are Optional here to accommodate both variants.
    """

    max_total_tokens: Optional[int] = None
    max_prompt_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None


class ModelPricing(ExtraAllowModel):
    unit: str
    prompt: str
    completion: Optional[str] = None


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
    tokenizer_model: Optional[str] = None
    capabilities: Optional[ModelCapabilities] = None
    limits: Optional[ModelLimits] = None
    pricing: Optional[ModelPricing] = None
