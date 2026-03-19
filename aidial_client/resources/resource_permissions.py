from typing import List

from aidial_client._internal_types._generic import NoneType
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource

_GRANT_URL = "v1/ops/resource/per-request-permissions/grant"


class ResourcePermissions(Resource):
    def grant(
        self,
        resources: List[str],
        receiver: str,
        permissions: List[str] = ["READ"],
    ) -> None:
        self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=_GRANT_URL,
                json_data={
                    "resources": [
                        {"url": url, "permissions": permissions}
                        for url in resources
                    ],
                    "receiver": receiver,
                },
            ),
        )


class AsyncResourcePermissions(AsyncResource):
    async def grant(
        self,
        resources: List[str],
        receiver: str,
        permissions: List[str] = ["READ"],
    ) -> None:
        await self.http_client.request(
            cast_to=NoneType,
            options=FinalRequestOptions(
                method="POST",
                url=_GRANT_URL,
                json_data={
                    "resources": [
                        {"url": url, "permissions": permissions}
                        for url in resources
                    ],
                    "receiver": receiver,
                },
            ),
        )
