from aidial_client.types.metadata import FileMetadata

BUCKET = "684f6Lz7ubje66aoCRsa5c"

PAYLOAD = {
    "bucket": BUCKET,
    "name": None,
    "nodeType": "FOLDER",
    "parentPath": None,
    "resourceType": "FILE",
    "url": f"files/{BUCKET}/",
    "items": [
        {
            "bucket": BUCKET,
            "name": "appdata",
            "nodeType": "FOLDER",
            "parentPath": None,
            "resourceType": "FILE",
            "url": f"files/{BUCKET}/appdata/",
        }
    ],
}


def test_name_is_none_round_trip():
    """Root folder returned by the API has name=None; parse→serialize must reproduce the original payload."""
    assert PAYLOAD["name"] is None
    result = FileMetadata(**PAYLOAD)
    assert result.name is None
    assert result.model_dump(by_alias=True, exclude_unset=True) == PAYLOAD
