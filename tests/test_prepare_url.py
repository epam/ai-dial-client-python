import pytest

from aidial_client import AsyncDial, Dial

BASE_URL = "http://localhost:8090"


@pytest.fixture(params=[Dial, AsyncDial])
def client(request):
    return request.param(base_url=BASE_URL, api_key="dummy")


@pytest.mark.parametrize(
    "relative,expected_url",
    [
        (
            "v1/metadata/files/bucket/appdata/app/",
            f"{BASE_URL}/v1/metadata/files/bucket/appdata/app/",
        ),
        (
            "v1/metadata/files/bucket/appdata/app",
            f"{BASE_URL}/v1/metadata/files/bucket/appdata/app",
        ),
        ("/v1/foo/", f"{BASE_URL}/v1/foo/"),
        ("v1/x/?foo=1", f"{BASE_URL}/v1/x/?foo=1"),
        ('/', f"{BASE_URL}/"),
        ('', f"{BASE_URL}/"),
    ],
)
def test_prepare_url_preserves_trailing_slash(client, relative, expected_url):
    prepared = client._http_client._prepare_url(relative)
    assert str(prepared) == expected_url
