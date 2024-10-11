import pytest
from pydantic import ValidationError

from aidial_client.types.chat.response import Attachment


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
