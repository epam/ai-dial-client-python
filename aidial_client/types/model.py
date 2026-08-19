from aidial_client._internal_types._model import ExtraAllowModel


class ModelCapabilities(ExtraAllowModel):
    scale_types: list[str] = []
    completion: bool | None = None
    chat_completion: bool | None = None
    embeddings: bool | None = None
    fine_tune: bool | None = None
    inference: bool | None = None


class ModelLimits(ExtraAllowModel):
    """Token limits for the model.

    Either `max_total_tokens` is set alone, or `max_prompt_tokens` and
    `max_completion_tokens` are set together (oneOf in the schema).
    All fields are Optional here to accommodate both variants.
    """

    max_total_tokens: int | None = None
    max_prompt_tokens: int | None = None
    max_completion_tokens: int | None = None


class ModelPricing(ExtraAllowModel):
    unit: str
    prompt: str
    completion: str | None = None


class ModelInfo(ExtraAllowModel):
    id: str
    model: str
    display_name: str | dict[str, str] | None = None
    description: str | dict[str, str] | None = None
    owner: str | None = None
    object: str | None = None
    status: str | None = None
    created_at: int | None = None
    updated_at: int | None = None
    lifecycle_status: str | None = None
    tokenizer_model: str | None = None
    embedding_dimensions: int | None = None
    capabilities: ModelCapabilities | None = None
    limits: ModelLimits | None = None
    pricing: ModelPricing | None = None
