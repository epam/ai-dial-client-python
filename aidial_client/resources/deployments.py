import builtins
from collections.abc import Sequence
from typing import Any

import httpx

from aidial_client._exception import ParsingDataError
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.deployment import (
    Deployment,
    DeploymentKind,
    DeploymentName,
    DeploymentsResponse,
)


def _names_options(
    types: Sequence[DeploymentKind] | None,
) -> FinalRequestOptions:
    return FinalRequestOptions(
        method="GET",
        url="v1/deployment-names",
        params={"type": ",".join(types)} if types else None,
    )


def _parse_names(response: httpx.Response) -> list[DeploymentName]:
    try:
        return [DeploymentName(**item) for item in response.json()]
    except Exception as e:
        raise ParsingDataError(
            message=f"Error during parsing of response data: {str(e)}"
        )


class Deployments(Resource):
    def _list_raw(self) -> DeploymentsResponse:
        return self.http_client.request(
            cast_to=DeploymentsResponse,
            options=FinalRequestOptions(method="GET", url="openai/deployments"),
        )

    def list(self) -> list[Deployment]:
        return self._list_raw().data

    def list_names(
        self, types: Sequence[DeploymentKind] | None = None
    ) -> builtins.list[DeploymentName]:
        response = self.http_client.request(
            cast_to=httpx.Response, options=_names_options(types)
        )
        return _parse_names(response)

    def get(self, deployment_id: str) -> Deployment:
        return self.http_client.request(
            cast_to=Deployment,
            options=FinalRequestOptions(
                method="GET", url=f"openai/deployments/{deployment_id}"
            ),
        )

    def get_configuration_schema(self, deployment_id: str) -> dict[str, Any]:
        return self.http_client.request(
            cast_to=dict,
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

    async def list(self) -> list[Deployment]:
        return (await self._list_raw()).data

    async def list_names(
        self, types: Sequence[DeploymentKind] | None = None
    ) -> builtins.list[DeploymentName]:
        response = await self.http_client.request(
            cast_to=httpx.Response, options=_names_options(types)
        )
        return _parse_names(response)

    async def get(self, deployment_id: str) -> Deployment:
        return await self.http_client.request(
            cast_to=Deployment,
            options=FinalRequestOptions(
                method="GET", url=f"openai/deployments/{deployment_id}"
            ),
        )

    async def get_configuration_schema(
        self, deployment_id: str
    ) -> dict[str, Any]:
        return await self.http_client.request(
            cast_to=dict,
            options=FinalRequestOptions(
                method="GET",
                url=f"v1/deployments/{deployment_id}/configuration",
            ),
        )
