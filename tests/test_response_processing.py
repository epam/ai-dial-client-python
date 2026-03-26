from aidial_client.types.metadata import FileMetadata

BUCKET = "684f6Lz7ubje66aoCRsa5c"

PAYLOAD = {
    "bucket": BUCKET,
    "name": None,
    "node_type": "FOLDER",
    "parent_path": None,
    "resource_type": "FILE",
    "url": f"files/{BUCKET}/",
    "items": [
        {
            "bucket": BUCKET,
            "name": "appdata",
            "node_type": "FOLDER",
            "parent_path": None,
            "resource_type": "FILE",
            "url": f"files/{BUCKET}/appdata/",
        }
    ],
}


def test_name_is_none_round_trip():
    """Root folder has name=None; parse→serialize must reproduce the original payload."""
    result = FileMetadata(**PAYLOAD)
    assert result.model_dump(exclude_unset=True) == PAYLOAD
