from typing import List
from urllib.parse import urljoin

from aidial_client._constants import APPLICATION_PREFIX
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.application import Application as ApplicationType
from aidial_client.types.application import ApplicationsResponse


class Application(Resource):
    def get(self, app_id: str) -> ApplicationType:
        return self.http_client.request(
            cast_to=ApplicationType,
            options=FinalRequestOptions(
                method="GET", url=urljoin(APPLICATION_PREFIX, app_id)
            ),
        )

    def _list_raw(self) -> ApplicationsResponse:
        return self.http_client.request(
            cast_to=ApplicationsResponse,
            options=FinalRequestOptions(method="GET", url=APPLICATION_PREFIX),
        )

    def list(self) -> List[ApplicationType]:
        return self._list_raw().data


class AsyncApplication(AsyncResource):
    async def get(self, app_id: str) -> ApplicationType:
        return await self.http_client.request(
            cast_to=ApplicationType,
            options=FinalRequestOptions(
                method="GET",
                url=urljoin(APPLICATION_PREFIX, app_id),
            ),
        )

    async def _list_raw(self) -> ApplicationsResponse:
        return await self.http_client.request(
            cast_to=ApplicationsResponse,
            options=FinalRequestOptions(method="GET", url=APPLICATION_PREFIX),
        )

    async def list(self) -> List[ApplicationType]:
        return (await self._list_raw()).data
