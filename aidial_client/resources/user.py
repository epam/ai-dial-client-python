from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.user import UserInfo


class User(Resource):
    def info(self) -> UserInfo:
        return self.http_client.request(
            cast_to=UserInfo,
            options=FinalRequestOptions(method="GET", url="v1/user/info"),
        )


class AsyncUser(AsyncResource):
    async def info(self) -> UserInfo:
        return await self.http_client.request(
            cast_to=UserInfo,
            options=FinalRequestOptions(method="GET", url="v1/user/info"),
        )
