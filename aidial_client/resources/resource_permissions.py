from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.helpers.storage_resource import (
    _percent_encode_relative_url,
)
from aidial_client.resources.base import AsyncResource, Resource

_GRANT_URL = "v1/ops/resource/per-request-permissions/grant"


def _grant_body(
    resources: list[str],
    receiver: str,
    permissions: list[str],
) -> dict[str, object]:
    return {
        "resourcePermissions": [
            {
                "url": _percent_encode_relative_url(url),
                "permissions": permissions,
            }
            for url in resources
        ],
        "receiver": receiver,
    }


class ResourcePermissions(Resource):
    def grant(
        self,
        resources: list[str],
        receiver: str,
        permissions: list[str] | None = None,
    ) -> None:
        if permissions is None:
            permissions = ["READ"]
        self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=_GRANT_URL,
                json_data=_grant_body(resources, receiver, permissions),
            ),
        )


class AsyncResourcePermissions(AsyncResource):
    async def grant(
        self,
        resources: list[str],
        receiver: str,
        permissions: list[str] | None = None,
    ) -> None:
        if permissions is None:
            permissions = ["READ"]
        await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=_GRANT_URL,
                json_data=_grant_body(resources, receiver, permissions),
            ),
        )
