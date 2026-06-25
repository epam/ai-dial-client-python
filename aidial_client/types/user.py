from typing import Any

from aidial_client._internal_types._model import ExtraAllowModel


class UserInfo(ExtraAllowModel):
    """Information about the authenticated user or API key."""

    roles: list[str]
    project: str | None = None
    userClaims: dict[str, Any] | None = None  # depends on the IdP, so opaque
