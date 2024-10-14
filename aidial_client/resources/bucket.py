from typing import Optional
from urllib.parse import urljoin

from aidial_client._constants import API_PREFIX
from aidial_client._internal_types._http_request import FinalRequestOptions
from aidial_client.resources.base import AsyncResource, Resource
from aidial_client.types.bucket import AppData, BucketResponse


class Bucket(Resource):
    def get_raw(self) -> BucketResponse:
        return self.http_client.request(
            cast_to=BucketResponse,
            options=FinalRequestOptions(
                method="GET", url=urljoin(API_PREFIX, "bucket")
            ),
        )

    def get_bucket(self) -> str:
        response = self.get_raw()
        return response.bucket

    def get_appdata(self) -> Optional[AppData]:
        response = self.get_raw()
        if not response.appdata:
            return None
        return AppData.parse(response.appdata)


class AsyncBucket(AsyncResource):
    async def get_raw(self) -> BucketResponse:
        return await self.http_client.request(
            cast_to=BucketResponse,
            options=FinalRequestOptions(
                method="GET", url=urljoin(API_PREFIX, "bucket")
            ),
        )

    async def get_bucket(self) -> str:
        response = await self.get_raw()
        return response.bucket

    async def get_appdata(self) -> Optional[AppData]:
        response = await self.get_raw()
        if not response.appdata:
            return None
        return AppData.parse(response.appdata)
