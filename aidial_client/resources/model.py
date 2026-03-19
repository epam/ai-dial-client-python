from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.model import ModelInfo


class Model(Resource):
    def get(self, model_name: str) -> ModelInfo:
        return self.http_client.request(
            cast_to=ModelInfo,
            options=FinalRequestOptions(
                method="GET", url=f"openai/models/{model_name}"
            ),
        )


class AsyncModel(AsyncResource):
    async def get(self, model_name: str) -> ModelInfo:
        return await self.http_client.request(
            cast_to=ModelInfo,
            options=FinalRequestOptions(
                method="GET", url=f"openai/models/{model_name}"
            ),
        )
