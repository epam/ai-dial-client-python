from typing import List

from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.deployment import (
    Deployment,
    DeploymentConfig,
    DeploymentsResponse,
)


class Deployments(Resource):
    def _list_raw(self) -> DeploymentsResponse:
        return self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    def list(self) -> List[Deployment]:
        return self._list_raw().data

    def get(self, deployment_id: str) -> Deployment:
        return self.http_client.request(
            cast_to=Deployment,
            options=FinalRequestOptions(
                method="GET", url=f"openai/deployments/{deployment_id}"
            ),
        )

    def get_config(self, deployment_id: str) -> DeploymentConfig:
        return self.http_client.request(
            cast_to=DeploymentConfig,
            options=FinalRequestOptions(
                method="GET",
                url=f"v1/deployments/{deployment_id}/configuration",
            ),
        )


class AsyncDeployments(AsyncResource):
    async def _list_raw(self) -> DeploymentsResponse:
        return await self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    async def list(self) -> List[Deployment]:
        return (await self._list_raw()).data

    async def get(self, deployment_id: str) -> Deployment:
        return await self.http_client.request(
            cast_to=Deployment,
            options=FinalRequestOptions(
                method="GET", url=f"openai/deployments/{deployment_id}"
            ),
        )

    async def get_config(self, deployment_id: str) -> DeploymentConfig:
        return await self.http_client.request(
            cast_to=DeploymentConfig,
            options=FinalRequestOptions(
                method="GET",
                url=f"v1/deployments/{deployment_id}/configuration",
            ),
        )
