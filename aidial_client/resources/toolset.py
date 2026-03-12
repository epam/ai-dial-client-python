from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.toolset import ToolsetInfo


class Toolset(Resource):
    def get(self, toolset_id: str) -> ToolsetInfo:
        return self.http_client.request(
            cast_to=ToolsetInfo,
            options=FinalRequestOptions(
                method="GET", url=f"openai/toolsets/{toolset_id}"
            ),
        )


class AsyncToolset(AsyncResource):
    async def get(self, toolset_id: str) -> ToolsetInfo:
        return await self.http_client.request(
            cast_to=ToolsetInfo,
            options=FinalRequestOptions(
                method="GET", url=f"openai/toolsets/{toolset_id}"
            ),
        )
