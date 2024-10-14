import pytest

from aidial_client.helpers._url import (
    enforce_trailing_slash,
    remove_leading_slash,
)


@pytest.mark.parametrize(
    "input_url, expected_output",
    [
        ("https://dial.core", "https://dial.core/"),
        ("https://dial.core/", "https://dial.core/"),
        ("https://dial.core/path", "https://dial.core/path/"),
        ("https://dial.core/path/", "https://dial.core/path/"),
    ],
)
def test_enforce_trailing_slash(input_url, expected_output):
    assert enforce_trailing_slash(input_url) == expected_output


@pytest.mark.parametrize(
    "input_url, expected_output",
    [
        ("///path/to/resource", "path/to/resource"),
        ("path/to/resource", "path/to/resource"),
        ("//path", "path"),
        ("https://dial.core/path", "https://dial.core/path"),
        ("/https://dial.core/path", "https://dial.core/path"),
    ],
)
def test_remove_leading_slash(input_url, expected_output):
    assert remove_leading_slash(input_url) == expected_output
