import pydantic

from aidial_client._compatibility.openai import BaseModel as OpenAIBaseModel
from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._compatibility.pydantic_v1 import BaseModel, Extra


class ExtraAllowModel(OpenAIBaseModel):
    if PYDANTIC_V2:
        model_config = {"extra": "allow"}
    else:

        class Config(pydantic.BaseConfig):  # pyright: ignore[reportDeprecated]
            extra = Extra.allow


class ExtraForbidModel(BaseModel):
    class Config:
        extra = Extra.forbid  # type: ignore
