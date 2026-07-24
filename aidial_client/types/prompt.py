from aidial_client._compatibility.pydantic import PYDANTIC_V2
from aidial_client._internal_types._model import ExtraAllowModel
from aidial_client._utils._alias import to_camel


class Prompt(ExtraAllowModel):
    """A DIAL prompt resource."""

    if PYDANTIC_V2:
        model_config = {
            "alias_generator": to_camel,
            "populate_by_name": True,
        }
    else:

        class Config:
            alias_generator = to_camel
            allow_population_by_field_name = True

    id: str
    name: str
    folder_id: str
    content: str | None = None
