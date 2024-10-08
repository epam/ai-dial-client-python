from typing import List

from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.deployment import Deployment, DeploymentsResponse


class Deployments(Resource):
    def raw_get(self) -> DeploymentsResponse:
        return self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    def get(self) -> List[Deployment]:
        return self.raw_get().data


class AsyncDeployments(AsyncResource):
    async def raw_get(self) -> DeploymentsResponse:
        return await self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    async def get(self) -> List[Deployment]:
        return (await self.raw_get()).data
