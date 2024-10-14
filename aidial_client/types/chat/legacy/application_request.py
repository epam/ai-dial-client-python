from typing import Dict, Mapping, Optional

from aidial_client._auth import AuthType, get_auth_headers
from aidial_client._compatibility.pydantic_v1 import (
    SecretStr,
    StrictStr,
    root_validator,
)
from aidial_client._internal_types._model import ExtraForbidModel
from aidial_client.types.chat.legacy.chat_completion import (
    ChatCompletionRequest,
)


class RequestParams(ExtraForbidModel):
    api_key_secret: SecretStr
    jwt_secret: Optional[SecretStr] = None

    deployment_id: StrictStr
    api_version: Optional[StrictStr] = None
    headers: Mapping[StrictStr, StrictStr]

    @root_validator(pre=True)
    def create_secrets(cls, values: dict):
        if "api_key" in values:
            if "api_key_secret" not in values:
                values["api_key_secret"] = SecretStr(values.pop("api_key"))
            else:
                raise ValueError(
                    "api_key and api_key_secret cannot be both provided"
                )

        if "jwt" in values:
            if "jwt_secret" not in values:
                values["jwt_secret"] = SecretStr(values.pop("jwt"))
            else:
                raise ValueError("jwt and jwt_secret cannot be both provided")

        return values

    @property
    def api_key(self) -> str:
        return self.api_key_secret.get_secret_value()

    @property
    def jwt(self) -> Optional[str]:
        return self.jwt_secret.get_secret_value() if self.jwt_secret else None

    @property
    def auth_headers(self) -> Dict[str, str]:
        if self.jwt_secret is not None:
            return get_auth_headers(
                auth_type=AuthType.BEARER,
                auth_value=self.jwt_secret.get_secret_value(),
            )
        else:
            return get_auth_headers(
                auth_type=AuthType.API_KEY,
                auth_value=self.api_key_secret.get_secret_value(),
            )


class ApplicationChatCompletionRequest(ChatCompletionRequest, RequestParams):
    pass
