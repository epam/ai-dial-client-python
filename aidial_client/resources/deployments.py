from typing import List

from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.deployment import Deployment, DeploymentsResponse


class Deployments(Resource):
    def _list_raw(self) -> DeploymentsResponse:
        return self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    def list(self) -> List[Deployment]:
        return self._list_raw().data


class AsyncDeployments(AsyncResource):
    async def _list_raw(self) -> DeploymentsResponse:
        return await self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    async def list(self) -> List[Deployment]:
        return (await self._list_raw()).data
