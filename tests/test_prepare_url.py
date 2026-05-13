import pytest

from aidial_client import AsyncDial, Dial


@pytest.fixture(params=[Dial, AsyncDial])
def client(request):
    return request.param(base_url="http://localhost:8090", api_key="dummy")


@pytest.mark.parametrize(
    "relative,expected_path",
    [
        ("v1/metadata/files/bucket/appdata/app/", "/v1/metadata/files/bucket/appdata/app/"),
        ("v1/metadata/files/bucket/appdata/app", "/v1/metadata/files/bucket/appdata/app"),
        ("/v1/foo/", "/v1/foo/"),
        ("v1/x/?foo=1", "/v1/x/"),
    ],
)
def test_prepare_url_preserves_trailing_slash(client, relative, expected_path):
    prepared = client._http_client._prepare_url(relative)
    assert prepared.raw_path.decode().split("?")[0] == expected_path
