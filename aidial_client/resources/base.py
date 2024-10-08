from aidial_client._compatibility.pydantic_v1 import BaseModel
from aidial_client._http_client import AsyncHTTPClient, SyncHTTPClient


class Resource(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    http_client: SyncHTTPClient


class AsyncResource(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    http_client: AsyncHTTPClient
