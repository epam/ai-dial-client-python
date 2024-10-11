import pytest
from pydantic import ValidationError

from aidial_client.types.chat.response import Attachment
from aidial_client.types.metadata import BaseMetadata


@pytest.mark.parametrize(
    "invalid_attachment",
    [
        {},
        {"reference_type": "test"},
        {"reference_url": "test"},
    ],
)
def test_invalid_attachment(invalid_attachment):
    with pytest.raises(ValidationError):
        Attachment(**invalid_attachment)


@pytest.mark.parametrize(
    "valid_attachment",
    [
        {"data": "test"},
        {"url": "test"},
        {"data": "test", "url": "test"},
        {"data": "test", "reference_type": "test", "reference_url": "test"},
    ],
)
def test_valid_attachment(valid_attachment):
    attachment = Attachment(**valid_attachment)
    for key, value in valid_attachment.items():
        assert getattr(attachment, key) == value


def test_metadata_population():
    metadata_by_name = BaseMetadata(
        name="test",
        bucket="test",
        url="test",
        node_type="FOLDER",
        resource_type="FILE",
    )
    alias_json = {
        "name": "test",
        "bucket": "test",
        "url": "test",
        "nodeType": "FOLDER",
        "resourceType": "FILE",
    }
    metadata_by_alias = BaseMetadata(**alias_json)  # type: ignore

    for field in BaseMetadata.__annotations__:
        assert getattr(metadata_by_name, field) == getattr(
            metadata_by_alias, field
        )
