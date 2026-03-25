import json

import httpx

from aidial_client._utils._response_processing import process_block_response
from aidial_client.types.metadata import FileMetadata


def _make_response(payload: dict, status_code: int = 200) -> httpx.Response:
    raw = json.dumps(payload).encode()
    return httpx.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=raw,
    )


BUCKET = "684f6Lz7ubje66aoCRsa5c"


class TestFileMetadataName:
    def test_name_is_none(self):
        """Root folder returned by the API has name=null; must parse without error."""
        payload = {
            "bucket": BUCKET,
            "items": [
                {
                    "bucket": BUCKET,
                    "items": None,
                    "name": "appdata",
                    "nodeType": "FOLDER",
                    "parentPath": None,
                    "resourceType": "FILE",
                    "url": f"files/{BUCKET}/appdata/",
                }
            ],
            "name": None,
            "nodeType": "FOLDER",
            "parentPath": None,
            "resourceType": "FILE",
            "url": f"files/{BUCKET}/",
        }
        result = process_block_response(FileMetadata, _make_response(payload))

        assert result.name is None
        assert result.bucket == BUCKET
        assert result.node_type == "FOLDER"
        assert result.parent_path is None
        assert result.resource_type == "FILE"
        assert result.url == f"files/{BUCKET}/"
        assert result.items is not None and len(result.items) == 1
        item = result.items[0]
        assert item.name == "appdata"
        assert item.bucket == BUCKET
        assert item.node_type == "FOLDER"
        assert item.parent_path is None
        assert item.resource_type == "FILE"
        assert item.url == f"files/{BUCKET}/appdata/"

    def test_name_is_string(self):
        """Root folder whose single child is a file (non-null name)."""
        payload = {
            "bucket": BUCKET,
            "items": [
                {
                    "bucket": BUCKET,
                    "contentLength": 2207949,
                    "contentType": "application/pdf",
                    "name": "ontologies.pdf",
                    "nodeType": "ITEM",
                    "parentPath": None,
                    "resourceType": "FILE",
                    "url": f"files/{BUCKET}/ontologies.pdf",
                }
            ],
            "name": None,
            "nodeType": "FOLDER",
            "parentPath": None,
            "resourceType": "FILE",
            "url": f"files/{BUCKET}/",
        }
        result = process_block_response(FileMetadata, _make_response(payload))

        assert result.name is None
        assert result.bucket == BUCKET
        assert result.node_type == "FOLDER"
        assert result.parent_path is None
        assert result.resource_type == "FILE"
        assert result.url == f"files/{BUCKET}/"
        assert result.items is not None and len(result.items) == 1
        item = result.items[0]
        assert item.name == "ontologies.pdf"
        assert item.bucket == BUCKET
        assert item.node_type == "ITEM"
        assert item.parent_path is None
        assert item.resource_type == "FILE"
        assert item.content_length == 2207949
        assert item.content_type == "application/pdf"
        assert item.url == f"files/{BUCKET}/ontologies.pdf"
