import re
from typing import Optional

from aidial_client._internal_types._model import ExtraAllowModel


class AppData(ExtraAllowModel):
    raw: str
    user_bucket: str
    app_name: str

    @classmethod
    def parse(cls, appdata: str) -> "AppData":
        match = re.match(r"^(.+)/appdata/(.+)$", appdata)
        if not match:
            raise ValueError("Invalid appdata format")

        user_bucket, app_name = match.groups()
        return cls(raw=appdata, user_bucket=user_bucket, app_name=app_name)


class BucketResponse(ExtraAllowModel):
    bucket: str
    appdata: Optional[str] = None
