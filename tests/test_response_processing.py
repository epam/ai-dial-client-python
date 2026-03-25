import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from aidial_client._exception import ParsingDataError
from aidial_client._utils._response_processing import process_block_response
from aidial_client.types.metadata import BaseMetadata, FileItem, FileMetadata

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Exact payload returned by the real API (from the bug report)
REAL_API_PAYLOAD = {
    "bucket": "684f6Lz7ubje66aoCRsa5c",
    "items": [
        {
            "bucket": "684f6Lz7ubje66aoCRsa5c",
            "items": None,
            "name": "appdata",
            "nodeType": "FOLDER",
            "parentPath": None,
            "resourceType": "FILE",
            "url": "files/684f6Lz7ubje66aoCRsa5c/appdata/",
        },
        {
            "bucket": "684f6Lz7ubje66aoCRsa5c",
            "contentLength": 2207949,
            "contentType": "application/pdf",
            "name": "ontologies.pdf",
            "nodeType": "ITEM",
            "parentPath": None,
            "resourceType": "FILE",
            "updatedAt": 1770130629876,
            "url": "files/684f6Lz7ubje66aoCRsa5c/ontologies.pdf",
        },
    ],
    "name": None,  # <-- root folder has null name (Fix 2)
    "nodeType": "FOLDER",
    "parentPath": None,
    "resourceType": "FILE",
    "url": "files/684f6Lz7ubje66aoCRsa5c/",
}


def _make_response(payload: dict, status_code: int = 200) -> httpx.Response:
    """Build a minimal httpx.Response carrying a JSON body."""
    raw = json.dumps(payload).encode()
    return httpx.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=raw,
    )


class TestBaseMetadataOptionalName:
    """
    Before the fix, name: str caused a ValidationError when the API returned
    "name": null for root-folder metadata entries.
    """

    def test_name_none_is_accepted(self):
        """Root-folder entries come back with name=null; this must not raise."""
        meta = BaseMetadata(
            name=None,
            bucket="abc",
            url="files/abc/",
            node_type="FOLDER",
            resource_type="FILE",
        )
        assert meta.name is None

    def test_name_str_still_works(self):
        meta = BaseMetadata(
            name="my-file.pdf",
            bucket="abc",
            url="files/abc/my-file.pdf",
            node_type="ITEM",
            resource_type="FILE",
        )
        assert meta.name == "my-file.pdf"

    def test_name_defaults_to_none_when_omitted(self):
        meta = BaseMetadata(
            bucket="abc",
            url="files/abc/",
            node_type="FOLDER",
            resource_type="FILE",
        )
        assert meta.name is None

    def test_file_metadata_name_none_via_model_validate(self):
        """End-to-end: parse the real API payload – name=null must not fail."""
        result = (
            FileMetadata.model_validate(REAL_API_PAYLOAD)
            if hasattr(FileMetadata, "model_validate")
            else FileMetadata.parse_obj(REAL_API_PAYLOAD)
        )  # type: ignore[attr-defined]

        assert result.name is None

    def test_file_metadata_full_real_payload(self):
        """The full payload from the bug report must parse without error."""
        response = _make_response(REAL_API_PAYLOAD)
        result = process_block_response(FileMetadata, response)
        assert result.name is None
        assert result.bucket == "684f6Lz7ubje66aoCRsa5c"

